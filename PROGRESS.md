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
  - the **live half is the operator's**: the first of the two `--llm claude-cli` runs of
    `03-RUNBOOK.md` §3 was made on 2026-09-08 and **refused to render**, so
    `eval/results/first-live/credit-attempt1/` is committed (trace, cassettes, artifact store and
    `run/*.json`; no row-level file, D-087) and **no report is**. The three defects it found are
    fixed in the Phase 9 follow-up below and written up in `docs/EVALUATION.md` §1; the
    **second `credit_default` attempt of 2026-09-08 also produced no report** — the bounded loop
    asked for `check_stability` on a package with no `regime.column`, the tool raised and
    `validate()` exited 1 — so `eval/results/first-live/credit-attempt2/` is committed on D-087's
    terms and its three defects are fixed in the second Phase 9 follow-up below; the
    **third `credit_default` attempt of 2026-09-08 rendered** — 19 model calls, 159 claims,
    0.9816 → 1.0000, zero findings, exit 0 — and is committed as
    `eval/results/first-live/credit-attempt3/` on D-087's terms; two of its sentences are false,
    both because the drafter was handed an incomplete set of artifacts, and the eight defects that
    reading found are fixed in the third Phase 9 follow-up below. Attempt 3 is **kept as the
    record** of what the pipeline produced that day. The **fourth `credit_default` attempt of
    2026-09-08 rendered as well** — 22 model calls, 17 tool calls, 161 claims, 0.9641 → 1.0000,
    zero findings, exit 0, $4.1603, 908.59 s — and is committed as
    `eval/results/first-live/credit-attempt4/` on D-087's terms. It is the first run whose
    **bounded loop did anything**: four steps, three executed, and one of them found test AUC of
    0.5875 on the 6,048 rows of 9,000 where `delinq_count_6m == 0`, which the report never
    mentioned. All six of its failed claims are one tokenizer defect and six of its sentences are
    the same shape of defect as attempt 3's; the ten that reading found are fixed in the fourth
    Phase 9 follow-up below. The **fifth attempt rendered** — 22 model calls, 285 claims, 0.9827 →
    1.0000, zero findings, exit 0, $6.0535, 1,328.47 s — and carries the first `### Open items` the
    pipeline produced live; it is committed as `eval/results/first-live/credit-attempt5/` and its
    seven defects are fixed in the fifth follow-up. The **`credit_default` live validation is now
    done and committed as `eval/results/first-live/credit/`**, on the **sixth** attempt: 18 model
    calls, 17 tool calls, 258 artifacts, 210 claims at grounding precision **1.0000 pre-repair and
    1.0000 post-repair**, **no repair round**, zero findings, no open item, exit 0, $3.9739,
    872.74 s, with the bounded loop running four steps that all executed. It carries the bare name
    because it is the run the README excerpts, `report.md` is committed as produced and is never
    edited, and the excerpt's five wording edits live outside it (D-120). Attempts 1 to 5 are
    archived beside it. The one deterministic defect reading found — a loop step whose
    `above_median` rule resolved to the whole split — is fixed in the sixth follow-up below. The
    **`msr_prepayment` real sample is built and committed** as of 2026-09-16: the five manifest
    digests, the three developer claims and `subjects/msr_prepayment/artifacts/real/` come from one
    `python -m code.run --data` on the Release 47 sample files, and the offline
    `--data … --llm fake` validate of that panel raises exactly one finding, `C1` at medium on the
    out-of-time and vintage-holdout splits, which D-161 records as the control's measured baseline
    rather than a false alarm (D-160 carries the fit). The **first `msr_prepayment` live run**, of
    2026-09-16, is archived as `eval/results/first-live/msr-attempt1/` on D-087's terms — 23 model
    calls, 305 claims at **0.9934 → 1.0000 over 304**, one finding, three open items, $7.1697,
    1,549.94 s. It is `attempt1` and not the bare name because its section 1 says no finding was
    raised under a scope table reading 0 / 1 / 0 / 0 (D-165); sections 4 and 5 carried one
    tokeniser class and one matcher class each (D-166, D-167). The **`msr_prepayment` live
    validation is now done and committed as `eval/results/first-live/msr/`**, on the **second**
    attempt, made on the build those three fixes ship in: 21 model calls, 19 tool calls, 364
    artifacts, 298 claims at grounding precision **0.9966 pre-repair and 1.0000 post-repair over
    297**, one repair round, one finding (`F-001`, `C1` at medium, ten candidates merged) and two
    open items, exit 0, $6.4858, 1,373.77 s, with the bounded loop running two complete partitions
    — `incentive` and `loan_age` — across both forward splits. Twenty row-level CSVs are outside
    the repository. It carries the bare name because it is **the run the README excerpts**:
    sections 2 and 4 verified whole pre-repair (48/48 and 109/109), section 1 names `F-001`, and
    its one pre-repair failure is in section 3 and outside the excerpt. `report.md` is committed as
    produced and is never edited; the excerpt's four wording edits live outside it (D-168). The one
    class it exposed — `SHA-256` tokenised as a claim of 256 — is fixed in the follow-up commit as
    D-169. **Phase 9 is closed on both halves.**
- [x] **Phase 10** — Taxonomy and seeded-defect generator (spec §5, `04` §2)
  - **nothing was dropped**: all fourteen seeded recipes produce their `expected_signal` on the
    synthetic subjects and all fourteen are detected at severity ≥ medium by `rules_only`, and the
    four controls raise exactly what D-017 and D-047 fix (D-136 records every measurement)
  - the `msr` `S1` recipe is **redesigned**, not dropped, along the line D-046 named: it re-cuts
    train and test by calendar time so the shift lands on the train-to-test comparison Quaestor
    tests (D-129)
  - two defects in **Quaestor** were found by seeding, both the same shape — a tool refusing to run
    on exactly the data a seeded defect produces, and the refusal ending the whole validation
    instead of being reported: `challenger_compare` on a missing value (D-125) and
    `compute_metrics` on a separable split (D-126). Both are fixed; neither changes a control
- [x] **Phase 11** — Probatio test layer with recorded cassettes and judge validation (spec §6)
  - shipped in **two commits**: the layer and its ten tapes, then the judge's kappa, the tape
    pruning and the one defect reading the recorded drafts found (D-156)
  - the grounding judge is **validated**: kappa **0.771** over 40 human-labelled drafter outputs,
    agreement 38/40, the record committed at `.probatio/judges/grounding.validation.json` and the
    labels beside the rubric (D-157). The rubric is deliberately **not** revised on these labels
  - the layer's one defect in `src/quaestor`: section 6's prompt told the drafter to describe
    nothing as a finding and then ordered it to describe one, on **every run ever made**, and all
    eight recorded drafts silently demoted the finding to an open item with grounding precision
    1.0 (D-156)
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
  4.94); champion test AUC 0.7753, Brier 0.007894, calibration slope 0.959 (**0.937** from
  2026-09-16 on, when D-160's estimator fix made the subject report the converged unpenalised
  slope; nothing else in this line moves), train 0.7883, out-of-time 0.7846, vintage holdout
  0.7718; challenger (`HistGradientBoostingClassifier`,
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
- 2026-09-08 — **Phase 9 follow-up** — the three defects the first live validation found, decided
  in Cowork 2026-09-08 and fixed here. Gate green on **all five** conditions that apply:
  `pytest -q` 1120 passed, 0 failed, 0 skipped, 0 xfailed (10 new); coverage of `src/quaestor`
  **100%** (`coverage run -m pytest`, 5507 statements) against the 85% floor; `ruff check` and
  `ruff format --check` clean on `src tests eval subjects` (127 files); `mypy --strict
  src/quaestor` clean (60 source files). Gate condition **5a** passes — `tests/test_golden_spec.py`
  (13 checks) still pins `examples/golden_report/`, which this follow-up **did not touch**: no byte
  of the directory changed and no new D-011 row was needed, which is what keeping
  `leakage.overlap` as an alias is for. Gate condition **5b** passes: both
  `quaestor validate ... --synthetic --llm fake --out DIR` lines run through the installed console
  script in `tests/test_cli.py` and again from a shell here — **`credit_default` grounding
  precision 1.0000 pre- and post-repair over 49 claims, 124 artifacts, one finding (`E1 low`,
  D-017); `msr_prepayment` 1.0000 and 1.0000 over 45 claims, 230 artifacts, no finding (D-047)** —
  the Phase 9 figures with three more artifacts each, which are the three the leakage screen now
  stores. **Gate condition 6 belongs to Phase 11** (D-007).
  **The run this follow-up is about.** `eval/results/first-live/credit-attempt1/` is committed:
  **17 model calls** (1 plan, 8 draft, 8 extract, no re-ask), 13 tool calls in 2.66 s, **179 claim
  checks — 176 verified, 2 unattributed, 1 unsupported**, **1 repair round** on section 3 after
  which all 140 post-repair claims verified, one finding (`L2` at severity high, evidence
  `leakage.overlap` and `threshold.L2.overlap`), **92,196 output tokens of which 63,865 (69.3%)
  were the eight extractions**, longest single call 20,257 tokens and 197 s, **notional cost $3.82**
  of which $2.18 was extraction, **wall-clock 16:59** from the first traced event to the last
  (1,019 s; the operator's shell read 17:02 for the whole command, which the trace does not cover)
  — **and no report, because the renderer refused**: `['1.0']` in section 2's "the champion in
  credit_default 1.0" was covered by no verified claim. Every one of those figures is re-derived
  from that trace by `tests/test_live_credit_attempt1.py`. The row-level files — `run/*.csv` and
  the four `run.data_*` / `run.predictions_*` artifacts, which are the same rows under a content
  address — are **not** committed and were moved to `~/code/data-raw/` (D-087); the artifact
  index still lists all 121 names, so the four are visible as entries whose payload the
  repository does not hold.
  **Three fixes, each with its own tests.** (a) One tokenizer (D-084):
  `src/quaestor/verifier/tokens.py` holds the eligible-number tokenizer and D-015's exclusion
  rules, and `eligible_numbers(markdown, *, package_version=None)` is the single definition the
  pre-pass, the repair loop's wrapper and the renderer's uncovered-number check all read;
  `uncovered_numbers`, `check_report` and `wrap_unverified` take `package_version` and
  `render_report` and `validate()` fill it, and **`masked_prose` is deleted** because its
  defaulted argument was the defect. `tests/test_live_credit_attempt1.py` reconstructs sections 2
  and 3 of the attempt from its recorded extraction prompts and asserts the pre-pass and the
  renderer return the same token set, and that every section checked against its own post-repair
  verdicts now has nothing uncovered while section 2 checked *without* the version still reports
  `['1.0']`. The version guard's trailing lookahead also becomes `(?!\w|\.\d)`, so `1.0.` at the
  end of a sentence is excluded too. (b) A cheaper extractor (D-085): `ExtractedClaim.line`
  replaces `ExtractedClaim.text`, the prompt prints the prose one numbered line per line
  (`numbered_prose` / `numbered_lines`), and the deterministic side fills `Claim.text` from the
  line the index names, so `claims.json` and `CLAIMS_SCHEMA.json` are unchanged and a line number
  that is not in the prose is dropped exactly as an ineligible token's claim is; the offline fake
  and `eval/verifier_eval.py`'s fake extractor read the numbers back out of the prompt they were
  sent. (c) `L2` on discrete data (D-086): `check_leakage` stores `leakage.overlap.ids`,
  `leakage.overlap.features` (with `leakage.overlap` as its alias, for the golden) and
  `leakage.duplicates.train`, and the candidate is severity **high** on an identifier overlap
  above `threshold.L2.overlap` and severity **medium** on a feature overlap above
  `max(threshold.L2.overlap, 2 × leakage.duplicates.train)`, otherwise absent. **Measured on this
  machine (Python 3.12.14):** the seeded shape in both variants — 3% of test rows copied into
  train with ids kept gives identifier overlap 3.0% and a high candidate; re-keyed gives
  identifier overlap 0.0%, feature overlap 3.0% and a medium candidate; the clean synthetic
  control gives 0.0 / 0.0 / 0.0 and no candidate; and the attempt's case as a discrete panel gives
  **feature overlap 1.2667% against a within-train duplicate share of 1.2857%, identifiers
  disjoint, and no candidate** — where the Phase 5 rule raises `L2` high. On the live panel itself
  the two shares were 1.2556% (committed as `leakage.overlap`) and 1.1619% (recomputed from that
  run's `data_train.csv`, which is not committed): a ratio of 1.08 where the rule asks for more
  than 2. Also shipped: `docs/EVALUATION.md` with section 1 "Defects found in live runs",
  DECISIONS D-084 to D-087, the Phase 9 follow-up section of `docs/DESIGN.md` and the
  `CHANGELOG.md` entries. No test calls a live model, downloads data, trains on real data or reads
  an API key; the committed cassettes are read as text and no provider is constructed from them.
  No push.
- 2026-09-08 — **Phase 9 follow-up 2** — the three defects the *second* live validation found,
  decided in Cowork 2026-09-08 and fixed here. Gate green on **all five** conditions that apply:
  `pytest -q` 1139 passed, 0 failed, 0 skipped, 0 xfailed (19 new); coverage of `src/quaestor`
  **100%** (`coverage run -m pytest`, 5565 statements) against the 85% floor; `ruff check` and
  `ruff format --check` clean on `src tests eval subjects` (128 files); `mypy --strict
  src/quaestor` clean (60 source files). Gate condition **5a** passes —
  `tests/test_golden_spec.py` (13 checks) still pins `examples/golden_report/`, which this
  follow-up **did not touch**: no byte of the directory changed and no new D-011 row was needed.
  Gate condition **5b** passes: both `quaestor validate ... --synthetic --llm fake --out DIR`
  lines run through the installed console script in `tests/test_cli.py` and again from a shell
  here — **`credit_default` grounding precision 1.0000 pre- and post-repair over 49 claims, 124
  artifacts, one finding (`E1 low`, D-017), 7.85 s; `msr_prepayment` 1.0000 and 1.0000 over 45
  claims, 230 artifacts, no finding (D-047), 6.70 s** — unchanged from the first follow-up, which
  is what a change confined to the bounded loop was supposed to leave alone. **Gate condition 6
  belongs to Phase 11** (D-007).
  **The run this follow-up is about.** `eval/results/first-live/credit-attempt2/` is committed on
  D-087's terms: **16 trace events, 14 tool calls in 2.69 s over 124 artifacts, one model call**
  (the loop's first plan step: 693 output tokens of which 628 thinking, on 2 input tokens,
  **$0.10093**, 13.0 s), **no candidate raised by any of the 13 rule-based calls** — including no
  `L2`, which is D-086's fix measured on the panel that provoked it — **wall-clock 15.09 s** from
  the first traced event to the last, **and no report, because the loop asked for
  `check_stability({"split": "test"})` on a package with no `regime.column`, the tool raised
  `ToolError` and `validate()` exited 1**. Every one of those figures is re-derived from that
  trace by `tests/test_live_credit_attempt2.py`, which also asserts the run's single cassette is
  the `claude-cli` tape it claims to be and that the four row-level artifacts are listed in
  `index.json` with no payload in the repository (D-087); the row CSVs had already been moved out,
  and `find eval/results/first-live/credit-attempt2 -name '*.csv' -size +20k` returns nothing —
  the 13 CSVs that remain are aggregate tables of 203 to 826 bytes.
  **Three fixes, each with its own tests.** (a) A loop-requested tool that raises is the step's
  failure, not the run's (D-088): `follow_up_plan` catches `ToolError`, the step is traced
  `accepted: true` / `executed: false` with the tool's message on a new `error` field, the message
  reaches the next step's prompt, the step still counts against the maximum of four, and the
  pipeline drafts with what it has. `PlanStep` and the `plan_step` event gain `executed` and
  `error`; `pipeline.py`'s `tools_run` counts only steps that executed. **A `ToolError` from the
  rule-based plan is still the run's failure and still exits 1** — the asymmetry is the decision.
  (b) The menu is filtered by applicability (D-089): `inapplicable_reason(tool, package)` is the
  one definition — `check_stability` needs a `regime.column`, `run_scenarios` a
  `discrete_time_hazard` subject with a `scenarios` block, and `run_model` is never offered (spec
  §3.12) — `loop_prompt` filters the catalogue by it, and a request for a filtered tool is refused
  before execution with `not applicable to this package: <why>`, traced `accepted: false`, fed
  back on the next step. The rule is applied **last** of the four, so spec §3.12's three refusals
  keep their own messages: `run_model` with an invented `entrypoint` is still caught by the closed
  `Args` that names the field, and a path at `/etc` by the rule that says so. Measured: the loop's
  menu is 6 tools on `credit_default` and 8 on `msr_prepayment`, out of the registry's 9. (c) The
  prompt lists what ran (D-090): one line per completed rule-based call with its arguments and the
  classes it raised or `no candidate`, built by `completed_calls(plan, results)`, plus one line
  per earlier loop step saying whether it was refused and why, accepted and failed and with what
  message, or accepted and run; the instruction that the loop is for a follow-up on what the
  candidates show and not for repeating the plan is unchanged. The prompt became `loop_prompt`, a
  function, which is what lets a test send the loop the bytes a recorded run was sent.
  **The replay.** `tests/test_live_credit_attempt2.py` puts the attempt's own answer back through
  `validate()` on the synthetic subject: `ReplayLLM` serves the run's single cassette under the key
  it was recorded with — the recorded prompt, read back out of the cassette — and the offline fake
  answers every call the attempt never made. The tape is **not** re-keyed onto today's prompt,
  because (b) and (c) changed that prompt deliberately and a cassette's key is a hash of the
  request; what is replayed is the model's answer, byte for byte. On this build that answer is
  refused with the applicability reason, the loop stops, and the pipeline renders a report whose
  post-repair grounding precision is 1.0000 — the attempt's exit 1 becomes a report. Also shipped:
  the dated `docs/EVALUATION.md` §1 entry for `credit-attempt2`, DECISIONS D-088 to D-090, the
  Phase 9 follow-up 2 section of `docs/DESIGN.md` and the `CHANGELOG.md` entries. No test calls a
  live model, downloads data, trains on real data or reads an API key; the committed cassette is
  read as JSON and the only provider built from it is `ReplayLLM` over the committed directory.
  No push.
- 2026-09-08 — **Phase 9 follow-up 3** — the eight defects the *third* live validation found, the
  first that rendered a report, decided in Cowork 2026-09-08 and fixed here. Gate green on **all
  five** conditions that apply: `pytest -q` 1215 passed, 0 failed, 0 skipped, 0 xfailed (76 new);
  coverage of `src/quaestor` **100%** (`coverage run -m pytest`, 5740 statements) against the 85%
  floor; `ruff check` and `ruff format --check` clean on `src tests eval subjects` (130 files);
  `mypy --strict src/quaestor` clean (60 source files). Gate condition **5a** passes —
  `tests/test_golden_spec.py` (13 checks) still pins `examples/golden_report/`, which this
  follow-up **did not touch**: no byte of the directory changed and no new D-011 row was needed,
  which is what keeping the `### Open items` rule in `report/schema.py` rather than in
  `REPORT_SCHEMA.json`'s heading list is for. Gate condition **5b** passes: both
  `quaestor validate ... --synthetic --llm fake --out DIR` lines run through the installed console
  script in `tests/test_cli.py` and again from a shell here — **`credit_default` grounding
  precision 1.0000 pre- and post-repair over 49 claims, 168 artifacts, one finding (`E1 low`,
  D-017), 3.97 s; `msr_prepayment` 1.0000 and 1.0000 over 45 claims, 271 artifacts, no finding
  (D-047), 6.11 s** — the same claims and the same findings as the second follow-up over 44 and 41
  more artifacts, which are the ones the sign check, the ablation, the threshold table and the
  effective bound now store. **Gate condition 6 belongs to Phase 11** (D-007).
  **The run this follow-up is about.** `eval/results/first-live/credit-attempt3/` is committed on
  D-087's terms: **282 trace events, 19 model calls** (1 plan, 9 draft, 9 extract, no re-ask, every
  one of them `claude-opus-5[1m]` through `ClaudeCLILLM`), **13 tool calls in 2.89 s over 124
  artifacts raising no candidate at all**, **247 claim checks — 244 verified, 2 unattributed, 1
  unsupported**, **two repair rounds** (section 3 removing `9.982` and `6`, section 4 removing
  `50`; nothing rewritten), **159 post-repair claims all verified, grounding precision 0.9816 →
  1.0000**, **zero findings**, **104,675 output tokens** (525 plan, 34,003 draft, 70,147 extract)
  against **176,851 input tokens the cassettes record and 38 the trace did**, longest single call
  16,192 tokens and 180.6 s, **notional cost $4.3822** of which $2.4414 extraction, **wall-clock
  20:18** (1,217.79 s) — **and a report, the first one**. Every figure is re-derived from that
  trace by `tests/test_live_credit_attempt3.py`, which also asserts, for each defect, both what
  that run's store lacked and what a run of the same plan on this build now holds; the row CSVs
  were already outside the repository and `find eval/results/first-live/credit-attempt3 -size
  +20k -name '*.csv'` returns nothing, the largest committed CSV being an 826-byte aggregate
  table.
  **Two false sentences, both the tool's fault.** Section 3 wrote that a 1.256% feature-vector
  overlap "is recorded as a finding" while section 6 correctly said none was raised — the bound
  D-086's rule actually applied is `max(0.005, 2 × 0.011619) = 0.02324` and was **not an
  artifact**, so the drafter compared 0.01256 with the declared 0.005 and was arithmetically
  right. Section 4.4 wrote that PSI was "not recomputed in the artifacts available to this
  section" while sections 1 and 3 both cited `psi.max`, and listed the subject's wall-clock cap
  among the performance thresholds — both because it was asked to *assemble* that table from
  whatever `threshold.package.` matched.
  **Eight fixes, each with its own tests.** (a) A derived bound is an artifact (D-091):
  `effective_name(base, rule)` in `tools/thresholds.py`, `threshold.L2.overlap.features_effective`
  from `check_leakage`, both `L2` candidates citing it, section 3's brief naming which arm is read
  against which bound, and the section prompt stating the candidate list explicitly — the literal
  `candidates raised for this section: none -- describe nothing as a finding`, the numbered list
  where there are candidates, and a standing `DRAFT_INSTRUCTION` rule that a finding is something
  on that list. (b) The tool writes the threshold table (D-092): `compute_metrics` stores
  `thresholds.evaluation` from the same loop that raises `T1`, the drafter writes
  `[[table:thresholds.evaluation]]`, `threshold.package.max_seconds` becomes
  **`runtime.max_seconds`**, and section 4's selector takes every `threshold.*` and `psi.*`
  scalar while section 1's gains `runtime.`. (c) The record describes the run (D-093):
  `ReportInputs.model_id` from the trace's own `llm_call` events on the front matter and the scope
  block with a `provider adapter` row beside it in Appendix C; `_run_id` carrying the UTC second
  the run began, because attempts 1 and 3 both read `credit_default-full_agent-d03b07c6`; and
  `ClaudeCLILLM` summing `input_tokens`, `cache_creation_input_tokens` and
  `cache_read_input_tokens`. (d) Renderer tables at four significant figures with integral cells
  as integers (D-094). (e) The sign check and the ablation (D-095): `check_collinearity` stores
  `sign_check.<feature>.{coef_sign,univariate_direction,agrees}` and `sign_check.n_disagreements`,
  `challenger_compare` stores `ablation.<feature>.delta_auc` against `ablation.baseline_auc` with
  `MAX_ABLATION_FEATURES = 25` and an `ablation.skipped` note above it; neither raises a
  candidate, and section 2's brief asks for the ablation delta as the materiality measure of any
  sign disagreement. **Measured on the clean synthetic panel at seed 20260901: three of ten
  retained coefficients disagree with their univariate direction, and dropping `delinq_last`
  costs 0.0759 of test AUC against an all-feature refit of 0.7480.** (f) `### Open items` under
  section 6 (D-096), asked of the drafter, placed and supplied by the renderer, required by
  `check_structure`. (g) Appendix A counting claims rewritten and numbers removed apart, the
  removals read off the trace (D-097). (h) `package.yaml` gains an optional, nullable
  **`use: ranking | probability | both`** (D-098, the one `package.yaml` change of this follow-up,
  decided in Cowork): section 4 leads with calibration when the declared use is `probability` or
  `both`, otherwise by the event rate, states which rule applied, and cites
  `rule.calibration_first_event_rate` only where that rule was the reason — where the use decided,
  the scalar leaves section 4's selector, so it cannot be cited. `credit_default` declares
  `ranking` and `msr_prepayment` `probability`; `docs/REPORT_SCHEMA.md` §3 and §10 carry it.
  **What D-085 saved, measured on the run it promised to measure on.** Extraction output rose from
  63,865 tokens over 8 calls to 70,147 over 9, and the answer half — which is the half D-085
  changed — fell from **168 to 91 tokens per claim check** (30,032 over 179 against 22,597 over
  247). The bill did not fall because thinking grew from 53% to **68%** of everything extraction
  generates, which is where the next cost decision has to look. Also shipped: the dated
  `docs/EVALUATION.md` §1 entry for `credit-attempt3`, DECISIONS D-091 to D-098, the Phase 9
  follow-up 3 section of `docs/DESIGN.md` and the `CHANGELOG.md` entries. No test calls a live
  model, downloads data, trains on real data or reads an API key; the committed cassettes are read
  as JSON, and the only provider built from them is `ClaudeCLILLM`'s payload mapping driven over
  the recorded `usage` objects. No push.
- 2026-09-08 — **Phase 9 follow-up 4** — the operator's **fourth** `credit_default` live run
  (`--llm claude-cli`, real UCI sample, `full_agent`, `claude-opus-5[1m]`) **rendered**: 22 model
  calls (4 plan, 9 draft, 9 extract), 17 tool calls, 192 artifacts, 262 claim checks, 167
  pre-repair claims at grounding precision **0.9641** rising to **1.0000** over 161, zero findings,
  exit 0, **$4.1603**, **908.59 s**. It is the first run in which the bounded loop did anything —
  four steps, all accepted, step 1's tool raised on a column name and steps 2 to 4 computed three
  sub-populations — and its own record is accurate for the first time: D-093's model id, run-id
  stamp and three-field input-token sum all hold, and the trace's 219,975 input tokens are the
  figure the 22 cassettes carry. Committed as `eval/results/first-live/credit-attempt4/` on
  D-087's terms (`find … -name '*.csv' -size +20k` prints nothing). Gate green on the five
  conditions that apply: `pytest -q` **1301 passed**, 0 failed, 0 skipped, 0 xfailed; coverage of
  `src/quaestor` **100%** (`coverage run -m pytest`, 5,923 statements) against the 85% floor;
  `ruff check` and `ruff format --check` clean on `src tests eval subjects`; `mypy --strict
  src/quaestor` clean (60 source files); gate condition 5 green — `examples/golden_report/` is
  untouched, and `quaestor validate --synthetic --llm fake` renders both subjects (credit_default
  1.0000 → 1.0000 over 49 claims, 1 finding, 168 artifacts; msr_prepayment 1.0000 → 1.0000 over 45
  claims, 0 findings, 271 artifacts). Ten defects fixed, DECISIONS **D-099 to D-108**. (a) The
  tokenizer's missing exponent form (D-099), which is **all six** of the run's failed claims:
  `1.92e-05` matched as `1.92` and `05`, so three literals produced six `unattributed` claims, and
  attempt 3's `9.982`/`6` removals were the same defect unrecognised. Exponent notation is one
  token and the tolerance is the mantissa's precision at the exponent's scale — `1.920e-05` claims
  10^-8. The offline fake's copy of the expression, `tests/test_golden_spec.py` check 7's literal
  and `eval/verifier_eval.py`'s fake extractor (which gains the citation mask, because
  `[[art:2e30351e:answer]]` holds `2e30351`) all move with it. (b) A section's artifact list is a
  selection and not the store (D-100): `recomputed_for_declared_bounds` derives the recomputed
  value of every declared bound from the `thresholds.evaluation` rows, so section 7 can no longer
  be shown a Brier ceiling with no Brier value, and `DRAFT_INSTRUCTION` forbids any section to
  call a quantity absent, uncomputed or "not carried". (c) The loop's executed steps reach the
  prose (D-101): `FollowUp` carries the tool, its arguments, its `why` and the names the step
  **added**, `sections_for_follow_up` assigns it to every matching section but never to the
  summary or the findings section, and a required level-3 `### Follow-up analyses` subsection
  reports it — supplied by the renderer where the drafter omitted it, so the rule cannot lose a
  finished report. (d) Where a follow-up result goes (D-102): `compute_metrics` stores
  `metrics.<split>.sub.<slug>.{auc_gap,share}` and the two new bounds
  **`threshold.O1.slice_auc_gap` = 0.08** and **`threshold.O1.slice_min_share` = 0.10**, both
  artifacts so the sentence can cite them; a slice over the gap on at least the floor is an open
  item in section 6, written as a question about what the model discriminates on inside a segment
  whose correlates are also fixed. Neither bound raises a candidate. **On the run's own numbers
  the never-delinquent segment qualifies at a gap of 0.1676 on 0.672 of the split, and neither
  `limit_bal` half does (0.0436, 0.0073).** (e) A section with no finding says so once and does
  not describe what it reviewed (D-103); the renderer's "Checks that ran and raised no candidate"
  line is the enumeration. (f) Section 4's ordering decision is passed into section 7's brief
  (D-104), so "as this report does" cannot contradict section 4's own opening sentence. (g)
  `_pair`'s nearest-value fallback needs the same line — citations and numbers removed — or the
  same cited logical name (D-105); the attempt's `1.92` → `2` row is now a removal, and Appendix A
  would read 0 rewritten / 6 removed. (h) Integral values reach the drafting prompt as integers
  (D-106), which D-094 did for renderer tables only. (i) The loop prompt lists the data's own
  columns (D-107), read from the header of `data_<split>.csv`. (j) `retrieve_guidance` returns
  top-`k` **per document**, the current guidance first (D-108): on the run's data-quality and
  sensitivity queries a single ranked list returned three SR 11-7 spans and no SR 26-2 span at
  all, so sections 3 and 5 opened on text superseded in April 2026 while `SR26-2:IV.1` and
  `SR26-2:V.1.a` sat unretrieved; which to cite stays the drafter's choice under D-055.
  **What D-085 cost on this run, and what it measures.** Extraction output fell from 70,147 tokens
  over 247 claim checks to **45,230 over 262** — 284 to **173** per check — the whole run from
  $4.3822 to $4.1603 and from 1,217.79 s to 908.59 s. **None of that is a saving and this line
  does not claim one:** `verifier/extract.py` is byte-identical between the two builds, the
  reports differ in length and section shape, and two runs of one prompt on one model, n = 1 each,
  measure run-to-run variance in how much the model chose to think. A cost claim about extraction
  needs repeated runs, which is Phase 12's. Also shipped: the dated `docs/EVALUATION.md` §1 entry
  for `credit-attempt4` (including the never-delinquent segment as the observation the report
  failed to surface) with attempt 3's repair row amended to name the tokenizer cause,
  `tests/test_live_credit_attempt4.py` (28 checks re-deriving every figure from that directory),
  DECISIONS D-099 to D-108, the Phase 9 follow-up 4 section of `docs/DESIGN.md` and the
  `CHANGELOG.md` entries. No test calls a live model, downloads data, trains on real data or reads
  an API key. No push.
- 2026-09-08 — **Phase 9 follow-up 5** — the operator's **fifth** `credit_default` live run
  (`--llm claude-cli`, real UCI sample, `full_agent`, `claude-opus-5[1m]`) **rendered**: 22 model
  calls (4 plan, 9 draft, 9 extract), 17 tool calls **none of which raised**, 250 artifacts, 417
  claim checks, 289 pre-repair claims at grounding precision **0.9827** rising to **1.0000** over
  285, zero findings, exit 0, **$6.0535**, **1328.47 s**. The bounded loop ran four steps and **all
  four executed** — `limit_bal below_median`, `delinq_last equals:0`, `delinq_last equals:1`,
  `utilisation above_median`, different slices from attempt 4's on the same prompt, subject and
  model — and the report carries the **first `### Open items` the pipeline has produced live**: two
  questions for the model developer, on the two delinquency slices whose AUC gap (0.1238 and
  0.1037) exceeds `threshold.O1.slice_auc_gap` at 0.08 on 0.775 and 0.1218 of test. **Six of the
  seven defects attempt 4 found did not recur** (D-099, D-100, D-103, D-104, D-106, D-108, each
  read off the report); the seventh, D-105, did. Committed as
  `eval/results/first-live/credit-attempt5/` on D-087's terms (`find … -name '*.csv' -size +20k`
  prints nothing). Gate green on the five conditions that apply: `pytest -q` **1340 passed**, 0
  failed, 0 skipped, 0 xfailed; coverage of `src/quaestor` **100%** (`coverage run -m pytest`,
  6,012 statements) against the 85% floor; `ruff check` and `ruff format --check` clean on `src
  tests eval subjects`; `mypy --strict src/quaestor` clean (60 source files); gate condition 5
  green — `examples/golden_report/` is untouched, and `quaestor validate --synthetic --llm fake`
  renders both subjects (credit_default 1.0000 → 1.0000 over 49 claims, 1 finding, 168 artifacts;
  msr_prepayment 1.0000 → 1.0000 over 45 claims, 0 findings, 271 artifacts). Seven defects fixed,
  DECISIONS **D-109 to D-115**. (a) **The first defect a live run has produced that the verifier is
  structurally unable to catch** (D-109): the repair round on section 4 flagged four numbers and
  the drafter, sent the whole section, also rewrote an unflagged line into "…by -0.02732
  `[[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]]` **is not the figure for this
  slice**; on train the gap is -0.001109…" — another slice's train gap spliced into the limit_bal
  paragraph, every citation resolving, so grounding precision was 1.0000. A round now takes from
  the re-draft only the lines that carried a flagged claim, each returned line attributed to the
  line of the previous draft it most resembles with citations removed; every other line is kept
  byte-identical, `REDRAFT_SIMILARITY` is the floor under the argmax, the event records
  `lines_redrafted`, and `REPAIR_INSTRUCTION` states the rule. **Replayed on the run's own section
  4 it re-drafts four lines and never writes the damaged sentence.** (b) Integral values reach the
  drafter unrounded (D-110): `four_significant_figures(10158)` is 10160 and a count is held to half
  a unit, which is two of the five failed claims and one count deleted from the prose. (c) A cited
  claim pairs by its name and only an uncited one by its line (D-111): section 4's four slice
  paragraphs share one skeleton, so D-105's line ground paired the flagged 10160 with another
  slice's verified 10500 and Appendix A reports "1 rewritten, 4 removed" of a round that rewrote
  none and removed five. (d) Three tokens that are not claims were counted and removed (D-112): the
  `0` and `1` of "**delinq_last equals 0.**" are a slice rule's parameters, now written
  `delinq_last == 0` in inline code, and "Section 4 of this report" is now an exclusion beside
  `§4`. (e) The citation carries the logical name, so the prose does not (D-113). (f) Section 7 is
  told the run compared a challenger (D-114), having written that benchmarking "was not part of
  this validation" three pages after section 2 reported it. (g) A follow-up slice reports its nine
  metrics per split as a `metrics.<split>.sub.<slug>` table the renderer expands, and the brief
  asks for the gap, the share and the level-versus-ordering reading instead of the enumeration
  (D-115) — **72 of the run's 285 claims**, and D-013 keeps a table's cells out of extraction.
  **What extraction cost, and what it does not measure.** 76,400 output tokens over 417 claim
  checks is **183 per check**, against 173 on attempt 4, 284 on attempt 3 and 357 on attempt 1,
  with `verifier/extract.py` byte-identical across the last three: four runs of one prompt on one
  model, n = 1 each, measuring how much the model chose to think. The *total* is not variance —
  417 checks against 262 is the four executed slices — and that is what D-115 addresses. Also
  shipped: the dated `docs/EVALUATION.md` §1 entry for `credit-attempt5` with attempt 1's repair
  row amended to name D-099's tokenizer as the cause of its `9.982`/`6` removals,
  `tests/test_live_credit_attempt5.py` (23 checks re-deriving every figure from that directory,
  including a line-by-line replay of the repair round), DECISIONS D-109 to D-115, the Phase 9
  follow-up 5 section of `docs/DESIGN.md` and the `CHANGELOG.md` entries. No test calls a live
  model, downloads data, trains on real data or reads an API key. No push.
- 2026-09-08 — **Phase 9 pre-flight (follow-up 6)** — **no live run, no live data**: the three
  archived runs that rendered (`credit-attempt3`, `credit-attempt4`, `credit-attempt5`) turned into
  offline regression fixtures, so the next defect class is found by `pytest` rather than by a person
  reading a report at $6 and twenty-two minutes. Gate green on the five conditions that apply:
  `pytest -q` **1389 passed**, 0 failed, 0 skipped, 0 xfailed (49 new); coverage of `src/quaestor`
  **100%** (`coverage run -m pytest`, 6,020 statements) against the 85% floor; `ruff check` and
  `ruff format --check` clean on `src tests eval subjects` (137 files); `mypy --strict
  src/quaestor` clean (60 source files); gate condition 5 green — `examples/golden_report/` is
  **untouched** (`git diff --stat examples/golden_report/` prints nothing and `MANIFEST.json` still
  hashes to `40a9a75ffbed3cce3d50f226f79f84b0e21873f2326ba6383fb0ac4d6bc73116`, D-011's second and
  current row), and `quaestor validate --synthetic --llm fake` renders both subjects through the
  installed console script (credit_default 1.0000 → 1.0000 over 49 claims, 1 finding, 168
  artifacts, 4.28 s; msr_prepayment 1.0000 → 1.0000 over 45 claims, 0 findings, 271 artifacts,
  6.28 s — the same figures as follow-up 5, because an artifact caption is not a claim). Four
  decisions, **D-116 to D-119**.
  **What the archive found.** Generalising `tests/test_golden_spec.py` check 7 to the three live
  reports finds **nothing**: 159, 161 and 285 eligible tokens against 159, 161 and 285 post-repair
  claims, both directions clean. That is because a repair round deletes the numbers it could not
  verify, so the same check over the **twenty-one first drafts** those reports were repaired from —
  recovered from the cassettes — is where the classes are. Seven residue tokens over five
  sections, and **one new token
  class**: attempt 3's section 4 drafted "The declared bound on the train-to-test AUC gap under rule
  O1 **(D-050)** is 0.08 `[[art:630f28f4:threshold.O1.auc_gap]]`", the `50` was counted in the
  denominator, reported `unattributed`, and provoked a round whose re-draft also rewrote the
  neighbouring sentence and cost the report a **verified `0.08`**. The reference came out of the
  caption the prompt showed it (`"O1: the train-to-test AUC gap (D-050)"`). D-116 takes both halves
  — `\bD-\d{3}\b` becomes the seventh exclusion class, `decisions_reference`, and the four
  `THRESHOLD_SUMMARIES` captions and `check_collinearity`'s lose their references, asserted over
  every artifact both synthetic runs store. Both halves are needed and the archive is what shows
  it: attempts 1 and 3 sent **byte-identical** section-4 prompts (one cassette key,
  `a3a5316ac0480158`, in both directories) and only attempt 3 copied the reference, so the form is
  a choice a live model makes. Blast radius asserted as an equality: over the draft calls of all
  four archived runs that made any, the class removes **exactly one token**.
  **Three classes the archive shows earlier than the run that named them.** D-099's exponent form
  in attempts 1, 3 and 4, named at 4 (`9.982e-06`, `1.92e-05`, `-5.589e-05`); D-112's
  section-reference-in-words in attempt 1 — "the contamination finding in section 3.3", one of that
  run's three flagged claims — named at 5; and **D-109 in five of the six repair rounds the archive
  holds**, not one: the drafter changed a line nobody flagged in attempt 3's outcomes round (2
  lines), attempt 4's two rounds (2 and 1), and attempt 5's outcomes and monitoring rounds (2 and
  3), **ten lines in all**, and `scope_to_flagged_lines` keeps all **245** unflagged lines of those
  six previous drafts byte-identical. The D-111 pairing over the three runs' own records reports
  **0 rewritten / 3, 6 and 5 removed** — the splits `docs/EVALUATION.md` states for attempts 4 and
  5, and the first record of attempt 3's false rewrite row.
  **How it is built (D-118).** `tests/archivesupport.py` reads a run — report, `claims.json`,
  trace, cassettes, index — recovering each drafting call from its cassette, each round's
  **previous** draft from the repair prompt that quotes it verbatim, and each round's flagged
  claims from the ids its own `repair` event lists. `tests/claimsupport.py` holds the coverage
  arithmetic, **standard library only**, and check 7 now calls it instead of carrying a copy; the
  *tokenizer* stays a deliberate second copy in the golden test, which imports no part of the
  package it specifies (D-099's own arrangement). What the cassettes cannot support is written into
  the tests: the re-extraction after each archived round ran on that run's unscoped re-draft, so no
  tape holds the extraction of a scoped one and the replay asserts the text and not the claims;
  attempts 1 and 2 wrote no `claims.json`, so attempt 1's drafts are read against the verified
  `claim_check` events of its trace instead; and a re-draft is found by the section its prompt
  names, which is asserted to be unambiguous because no archived section went to a second round.
  **Two residuals closed while the archive was open.** `scope_to_flagged_lines` returns a
  `ScopedRedraft` and the `repair` event carries **`scoped`**, so the one path on which D-109's
  guarantee does not hold is a fact in the record and not an inference from `lines_redrafted`
  (D-117) — none of the six archived rounds took it, asserted by the reason it cannot. And
  `tests/test_pipeline.py`'s two Phase 9 follow-up cases move off `SMALL = 1200` to the default
  panel and assert the **whole** finding set `{E1 low}` instead of `"E1" in` it, which passed on a
  panel raising `T1` at **high**: **measured at 2.16 s a run at 1,200 rows against 2.40 s at 5,000,
  and 7.07 s against 6.93 s for the pair under `pytest -k`** (D-119). Also shipped: the dated
  `docs/EVALUATION.md` §1 entry for the archive fixtures, `tests/test_archive_fixtures.py` (44
  checks), the Phase 9 pre-flight section of `docs/DESIGN.md` and the `CHANGELOG.md` entries. No
  test calls a live model, downloads data, trains on real data or reads an API key; the archive is
  read as JSON and text only, and no byte of `eval/results/first-live/` changed. No push.
- 2026-09-08 — **Phase 9 follow-up 6** — the operator's **sixth** `credit_default` live run
  (`--llm claude-cli`, real UCI sample, `full_agent`, `claude-opus-5[1m]`) **rendered on
  `fc33dd7`** and **is the `credit_default` live validation**: 18 model calls (4 plan, 7 draft, 7
  extract, no re-ask), 17 tool calls **none of which raised**, 258 artifacts, 210 claim checks, 210
  claims at grounding precision **1.0000 pre-repair and 1.0000 post-repair**, **no repair round**,
  zero findings, **no Open item**, exit 0, **$3.9739**, **872.74 s**. The bounded loop ran four
  steps and **all four executed** — `limit_bal below_median`, `limit_bal above_median`,
  `delinq_count_6m above_median`, `utilisation above_median`. Committed **byte-for-byte as
  produced** as `eval/results/first-live/credit/` — the bare name, because it is the run the README
  excerpts — on D-087's terms (`find eval/results/first-live/credit -name '*.csv' -size +20k`
  prints nothing; the eight row-level CSVs are in `~/code/data-raw/credit/first-live-rows/`).
  Attempts 1 to 5 are archived beside it; the `msr_prepayment` live run remains outstanding on the
  Freddie Mac download. Gate green on the five conditions that apply: `pytest -q` **1431 passed**,
  0 failed, 0 skipped, 0 xfailed (42 new); coverage of `src/quaestor` **100%** (`coverage run -m
  pytest`, 6,030 statements) against the 85% floor; `ruff check` and `ruff format --check` clean on
  `src tests eval subjects` (139 files); `mypy --strict src/quaestor` clean (60 source files); gate
  condition 5 green — `examples/golden_report/` is **untouched** (`git diff --stat
  examples/golden_report/` prints nothing and `MANIFEST.json` still hashes to
  `40a9a75ffbed3cce3d50f226f79f84b0e21873f2326ba6383fb0ac4d6bc73116`, D-011's second and current
  row), and `quaestor validate --synthetic --llm fake` renders both subjects through the installed
  console script (credit_default 1.0000 → 1.0000 over 49 claims, 1 finding, 168 artifacts, 4.76 s;
  msr_prepayment 1.0000 → 1.0000 over 45 claims, 0 findings, 271 artifacts, 6.52 s — the same
  figures as the pre-flight, because neither fake run's loop asks for a slice and the new bound is
  stored only by a call that computes one). Five decisions, **D-120 to D-124**.
  **The excerpt policy (D-120).** `report.md` is committed as produced and is **never edited**. The
  README excerpt is §2 and §4 **whole** — `### Follow-up analyses` and the degenerate-slice
  paragraph included — with **five wording edits applied in the excerpt only**, recorded verbatim in
  D-120 so Phase 16 copies rather than reconstructs them and destined for a before/after diff in
  `docs/PROVENANCE.md`. No edit changes a number, asserted by tokenizing both sides of each pair;
  each `before` string is asserted to be in the committed report **exactly once**, so the entry
  cannot drift from the file. Two of the six strings the prompt supplied were quoted **without their
  citations** and are in the file only with them — the drafter writes the citation between the
  number and the words — so D-120 records the file's own strings.
  **One deterministic defect, found by reading.** The third loop step asked for `delinq_count_6m
  above_median`; `above_median` was `>= median`, the median of that column on this sample is **0**,
  and the rule selected **every row of both splits** — share **1** on each, an AUC gap of **0**, `n`
  of 21,000 and 9,000, **22 logical names per split** for a population identical to its parent, two
  rendered tables, three interpreting sentences and one of four steps spent. The drafter described
  it honestly and that paragraph stays in the report. `compute_metrics` now **refuses** a slice that
  is the whole split, on the D-088 path, with a message naming the resolved rule, the share and the
  bound (D-121): the bound is a **stored ceiling**, `threshold.O1.slice_max_share` at **0.95**,
  rather than an exact share of 1, because a slice holding 0.98 of its split has the same defect and
  because deriving it from `slice_min_share` would let the open-item floor silently re-tune what the
  tool computes; and the check is a **pre-pass over every split asked for**, so a slice degenerate
  on the second stores nothing of the first. `below_median` and `above_median` are now `<= median`
  and `> median` (D-122): they **partition** the split, the median's own rows are in the lower half,
  and on this column `below_median` is the 67% that has never been delinquent — the segment attempts
  4 and 5 found material at test AUC 0.5875 and 0.6312 against 0.755, which under `<`/`>=` **no
  median rule could name**. The prompt asked only for `above_median` to become strict `>`; taken
  alone that leaves the median's own rows in neither half, so both sides moved and D-122 records
  why. `equals:` needs no edge of its own, because the check reads the share the rule resolved to.
  The loop prompt now carries all of it (D-123), which is D-089, D-090 and D-107's argument a fourth
  time.
  **What the run does not show, and what it did not exercise.** It is the **first live run with no
  repair round**, so D-109's scoped re-draft path has **still not run live** and **no tape holds
  one** — all six archived rounds were made by builds without the scoping in them. Slice choice is
  the model's and has now differed on all three runs whose loop executed, and **no Open item was
  raised because this run did not test the never-delinquent segment**, not because the package has
  no question to answer. Extraction was **42,738 output tokens over 210 claim checks, 204 per
  check**, the fifth reading of 357 → 284 → 173 → 183 → 204 with `verifier/extract.py` unchanged
  behind the last four: **n = 1 each and no saving is claimed**. D-115 measured: **210 claims
  against attempt 5's 285** with four executed slices in both, and **$3.97 against $6.05** — the
  direction, not a coefficient, since the two runs sliced different columns and made seven drafting
  calls against nine. Also shipped: the dated `docs/EVALUATION.md` §1 entry for the sixth attempt,
  carrying a **"What the excerpt does not show"** subsection so Phase 16 quotes the known-limitations
  list rather than rewriting it (zero findings is evidence and judgement and not detection; the
  missed segment; the degenerate step; the decile reversals at 4/5 and 8/9 and calibration bin 6
  that no rule reads; the `bill_trend_6m` sign disagreement §2 qualifies and nothing routes to Open
  items; SR 26-2 and SR 11-7 mixed where SR 26-2 returned no span; one run, no stability repeats);
  `tests/test_live_credit.py` (30 checks); the run added to `tests/test_archive_fixtures.py` as the
  archive's **negative case** (D-124, 51 checks there now); DECISIONS D-120 to D-124; the Phase 9
  follow-up 6 section of `docs/DESIGN.md`; and the `CHANGELOG.md` entries. **Not in scope, noted:** a
  rule routing a sign disagreement with a material ablation delta (D-095) to Open items the way
  D-102 routes slices — it changes drafting behaviour and needs a bound, so it is a DECISIONS
  question and not this commit. No test calls a live model, downloads data, trains on real data or
  reads an API key; no byte of `eval/results/first-live/` outside the new `credit/` directory
  changed. No push.
- 2026-09-08 — **Phase 10** — gate green on all five conditions that apply: `pytest -q` **1486
  passed**, 0 failed, 0 skipped, 0 xfailed (55 new); coverage of `src/quaestor` **100%**
  (`coverage run -m pytest`, 6097 statements) against the 85% floor; `ruff check` and `ruff format
  --check` clean on `src tests eval subjects` (141 files); `mypy --strict src/quaestor` clean (60
  source files). Gate condition **5a** passes — `tests/test_golden_spec.py` still pins
  `examples/golden_report/`, which this phase **did not touch**: `MANIFEST.json` still has the
  sha256 D-011's table pins (`40a9a75f…`) and no byte of the directory changed. Gate condition
  **5b** passes: both `quaestor validate … --synthetic --llm fake --out DIR` lines run through the
  installed console script in `tests/test_cli.py` and again from a shell here — **`credit_default`
  grounding precision 1.0000 pre- and post-repair over 49 claims, 168 artifacts, one finding
  (`E1 low`, D-017); `msr_prepayment` 1.0000 and 1.0000 over 45 claims, 271 artifacts, no finding
  (D-047)** — the same figures as the last follow-up, which is what a phase that adds no artifact
  to a clean run should leave. **Gate condition 6 belongs to Phase 11** (D-007). Shipped
  `eval/taxonomy.yaml` and `docs/CHECKLIST.md` (copied from the Cowork drafts of 2026-09-09; no
  `met_where` sentence and no parameter was changed, and the checklist needed **no** correction —
  every tool it names is in the registry and every class code is one of spec §3.7's twelve, which
  `tests/test_seed.py` asserts), `eval/seed.py` (the fourteen recipes, `DefectSpec`, `Taxonomy`,
  `seed()`, `build_all()` and a `main()` of its own), `quaestor study build` in `cli.py`,
  `tests/test_seed.py` (51 checks), the separability and missing-value cases in
  `tests/test_tool_rules.py` and `tests/test_tool_frames.py`, DECISIONS **D-125 to D-137**, the
  Phase 10 section of `docs/DESIGN.md` and the `CHANGELOG.md` entries. `eval/variants/` is
  gitignored: a variant is a generated artefact and a real-data variant would carry rows of the
  data.
  **All fourteen seeded recipes fire and nothing was dropped.** Measured at seed 20260901 through
  `run_model` and `rules_only` (which calls no model), `credit_default --synthetic 5000` and
  `msr_prepayment --synthetic 2000`, each variant's signal against its bound: `L1` single-feature
  AUC **0.9450** against 0.90 on both credit arms (and `leakage.timing.n_flagged` 1 on the
  declared arm) and **1.0000** on the hazard subject; `L2` feature overlap **3.00%** and **2.997%**
  against 0.50% with identifier overlap 0.0000 on both, the medium arm of D-086 by the human's
  decision (D-128); `R1` `stability.bill_trend_6m.sign_flip` **1**; `C1` mean-predicted-to-observed
  gap **94.9%** and **371.6%** against 25%; `S1` `psi.limit_bal` **1.196** and `psi.burnout`
  **3.016** against 0.25; `M1` `vif.max` **121,914** and condition number **1,023** against 10 and
  30; `D1` test missingness **0.300** against a train 0.000 and a gap bound of 0.10; `T1` a
  declared minimum of **0.78** against a recomputed AUC of **0.7480**; `X1` convexity **+336,109**
  where the package declares negative, with −300 bp and +300 bp both **+168,055**. Every one is a
  finding of the seeded class at severity ≥ medium in `findings.json`, which is `04` §4's
  detection criterion. The four controls raise exactly what D-017 and D-047 fix — `{E1 low}` and
  `{}` — and the two harmlessly perturbed ones raise the same sets as their clean twins.
  **Two margins are thin and are named** (D-136): the hidden `L1` arm clears its ceiling by 0.045,
  and the SMOTE variant's calibration slope sits 0.005 below its floor, though that `C1` does not
  depend on the slope. **Two recipes needed a decision rather than a parameter**: the hazard `S1`
  is redesigned as a train-to-test re-cut, which is the branch D-046 promised and the alternative
  to dropping it (D-129), and `R1` had to *add* the effect it reverses, because `bill_trend_6m` is
  not in the clean generating process at all (D-130). **Seeding found two defects in Quaestor**,
  both the same shape — a tool refusing to run on exactly the data a seeded defect produces, and
  the refusal ending the whole validation instead of being reported: `challenger_compare` treated
  a missing value as a non-numeric one, so the `D1` variant produced no report (D-125), and
  `compute_metrics` let the calibration slope's non-convergence propagate, so the separable hazard
  `L1` variant produced no report either (D-126). Both are fixed and neither adds an artifact to a
  clean run. **Five of the eighteen variants are synthetic-only** — the two credit `L1` arms,
  credit `R1`, credit `M1` and the hazard `L1` — because each needs a column the real samples do
  not build; the list is D-137 and the work is Phase 12's. No test calls a live model, downloads
  data, trains on real data or reads an API key. No push.
- 2026-09-15 — **Phase 11** — gate green on **all six** conditions, condition 6 for the first time:
  `pytest -q` **1529 passed**, 0 failed, 0 skipped, 0 xfailed (5 new); coverage of `src/quaestor`
  **100%** (`coverage run -m pytest`, 6,102 statements) against the 85% floor; `ruff check` and
  `ruff format --check` clean on `src tests eval subjects` (148 files); `mypy --strict src/quaestor`
  clean (60 source files). Gate condition **5a** passes — `examples/golden_report/` is untouched by
  both Phase 11 commits and `tests/test_golden_spec.py`'s 13 checks pass. Gate condition **5b**
  passes: **`credit_default` grounding precision 1.0000 pre- and post-repair over 49 claims, 168
  artifacts, one finding (`E1 low`, D-017); `msr_prepayment` 1.0000 and 1.0000 over 45 claims, 271
  artifacts, no finding (D-047)** — unchanged by D-156, which edits a prompt no fake provider
  reads. Gate condition **6**: `pytest tests/probatio --cassette=replay` **40 passed**, and the
  zero-provider-call half is *measured* rather than asserted — a session plugin that raises on any
  `FakeProvider.complete` reports **0 calls**.
  **This is the phase's second commit.** The first shipped the layer, the ten tapes and DECISIONS
  D-138 to D-155; this one ships the judge's kappa, the tape pruning, and the one defect that
  reading the recorded drafts found.
  **The defect, and why it matters more than its size.** Section 6's prompt carried `candidates
  raised for this section: none -- describe nothing as a finding` (D-091) and, eleven lines below
  it, `Findings to write about, in this order` with `### F-001 · E1 effective challenge · severity
  **low**`. The two lines came from two arguments of `Drafter.prompt` filled from two objects, and
  because `SECTION_FOR_CLASS` maps **no** defect class to the findings section — a finding's
  `section` names the material it rests on, not where it is printed — `candidates_by_section` is
  empty for section 6 on every run, so **every section-6 prompt this project has ever built for a
  package with a finding said both things**. All eight recorded drafts resolved it identically:
  "this validation raised no findings", with `E1` moved into `### Open items` as a question for the
  developer. Every number in all eight is cited and correct and the grounding judge passed 8 of 8
  at 1.0 — **silent demotion with perfect grounding**. Nothing in this project can see it: the
  verifier measures whether a number matches the store, the judge measures grounding, and the
  renderer would have printed `### F-001` two lines under the drafter's sentence saying nothing was
  raised. Fixed by deriving both blocks from one list in `Drafter.prompt` rather than in
  `_draft_inputs`, so the state is unassemblable for every caller (D-156); three new checks in
  `tests/test_drafter.py`, the load-bearing one asserting for *every* section that a listed finding
  never appears beside `NO_CANDIDATES`. The edit stranded exactly one tape —
  `prompt_bytes` 21,947 → 22,296 and `prompt_sha256` `405694630f3c281f` → `2747cbbb12cc5043` on
  `draft_section.findings` alone, every other case byte-identical, which is D-147's pin doing the
  job it was added for — and the operator re-recorded that one case in a **fifth** sitting for
  **$2.46 over 16 calls**, into a moved-aside file per D-155. All eight new drafts write `F-001`
  under its own heading.
  **The kappa.** `probatio validate-judge --labels tests/probatio/labels/grounding.labels.csv
  --rubric <abs>/tests/probatio/rubrics/grounding.md --judge-column judge --human-column human`
  reports **n=40, agreement 0.950, kappa 0.771** — the operator's own figure to three decimals, so
  there are not two numbers to reconcile. Both label distributions 35 pass / 5 fail; the 2×2 of
  (human, judge) is 34 / 1 / 1 / 4. The record goes to `.probatio/judges/grounding.validation.json`,
  which `ProbatioSettings.validation_dir` fixes at `<rootdir>/.probatio/judges` with no flag to
  move it, and the seven "rubric has no validation record" warnings are gone. The merged CSV is
  committed after checking what is in it: its 141 distinct artifact names are all from the
  synthetic `credit_default` run at seed 20260901 plus the hazard subject's `projection.convexity`
  (D-141's distractor), and there is no data row, no identifier and no credential in it. **The two
  disagreements** (D-157): `conceptual_soundness-03`, human pass / judge fail, where the human read
  criterion 1's "every number" as digits — the tokenizer's reading — and the judge read "two and a
  half" as a number, on a derived ratio of two artifacts that is in no store; and `summary-03`,
  human fail / judge pass, where the judge passed "no severity is assigned here" having failed
  `summary-07`'s near-identical "no severity counts exist to report" on the same criterion, so that
  row is the judge inconsistent at its own boundary. **0.771 is recorded as it stands and the
  rubric is not revised in this commit**: revising it after reading the labels and re-grading the
  same 40 rows is choosing a threshold on a test set. Both boundary questions go to the Phase 12
  pre-flight with the `DRAFT_INSTRUCTION` change, and a revised rubric is validated on a fresh
  label set.
  **The pruning.** **64 interactions removed across six drafting tapes** — summary 9,
  conceptual_soundness 9, data_integrity 12, outcomes 11, sensitivity 9, monitoring 14, findings 0,
  and nothing on the three non-drafting tapes; 185 interactions to 121, 7.5 MB to 4.9 MB (D-158).
  Fifty-three are judge calls keyed on a superseded rubric (D-148's and D-153's revisions each
  strand a tape's whole judge half, since a rubric is part of every judge prompt) and eleven are
  `structured()` re-ask prompts whose first-call answer was later re-recorded. The live key set was
  **measured** — a session plugin logged every key a replay requests — and not inferred from the
  visible pattern, which would have missed all eleven re-asks. `draft_section.findings` prunes
  nothing, because D-155's move-aside rule means a tape recorded that way never accumulates one.
  **`docs/EVALUATION.md` keeps the ~$73 layer cost**: the pruned calls were made and paid for, and
  the tapes account for $28.95 of it because two sittings died and two rubric revisions stranded
  what they had bought.
  Also shipped: the dated `docs/EVALUATION.md` §1 entry for the layer — the five sittings against
  the $25.69 estimate with its three causes (the 120 s timeouts, the criterion-5 over-tightening,
  the judge-JSON noise); the judge-parse progression **80% → 25% → 0 of 60** and the statement that
  the relation rates of the first two recordings measured the grader and are therefore not
  published; **the relation table as committed** — `distractor_robust` 1/7, `format_jitter` 2/21,
  `order_invariant` 3/21, six flips over 49 variant runs, every one a judge assertion and none a
  parse failure — with `extract_claims` at 5 of 5, rate 1.00, Wilson [0.57, 1.00] against its 0.8
  floor; the kappa with its 2×2 and both disagreements; and **the three classes the clean relations
  found**, each named with the tape it came from: the findings contradiction and silent demotion
  above; **the drafter writing about any artifact it is shown** — the hazard subject's
  `projection.convexity` distractor became a sentence in section 1 and an *open item* in section 6,
  a question to the developer about a model the package does not contain, which the judge passed at
  1.0 and failed only for an incidental uncited `300`, and which is why **open items become
  rule-minted in the Phase 12 pre-flight**; and **spelled-out quantities walking past the
  verifier** — "by roughly a factor of two and a half", a ratio of two artifacts that is in no store
  and that nothing tokenises, in three of the 49 variant runs, which is why `DRAFT_INSTRUCTION`
  gains a no-spelled-out-quantities rule in the same pre-flight. D-151 gains the sentence that the
  recorded model's name lives in two places — the tapes' interaction keys and `pyproject.toml`'s
  `addopts` — and that they move together. DECISIONS **D-156 to D-158**, the Phase 11 second section
  of `docs/DESIGN.md`, and the `CHANGELOG.md` entries.
  **What this phase does not show, said rather than left to be inferred.** One recording of each
  case, so the relation rates have n = 8 at best; every flip is a judge assertion, so they measure a
  grader's stability as much as a drafter's; the kappa rests on 40 rows with five failures in each
  margin, where moving one cell of the 2×2 moves it by about 0.1; and the three classes are three
  that eight samples of seven prompts happened to surface, not an enumeration. Three tapes still
  carry the operator's home path inside a recorded completion — the Claude CLI answering a drafting
  prompt with an attempted `<invoke name="Bash">` listing its own memory directory — because the
  re-ask that followed each is a call the replay makes; unchanged from the previous commit, and no
  credential is in them. No test calls a live model, downloads data, trains on real data or reads
  an API key; the only live calls of this phase are the operator's five record sittings. No push.

- 2026-09-17 — **Phase 9 follow-up 8 (the MSR excerpt run)** — the operator's **second**
  `msr_prepayment` live run, committed as `eval/results/first-live/msr/` and **closing Phase 9 on
  both halves**. Gate green on the four conditions that apply to a commit that adds no
  `src/quaestor` code: `pytest -q` **1613 passed**, 0 failed, 0 skipped, 0 xfailed (1591 at HEAD,
  plus `tests/test_live_msr.py`'s 22); `ruff check` and `ruff format --check` clean on
  `src tests eval subjects`; `mypy --strict src/quaestor` clean and unchanged, nothing under `src/`
  having moved; `examples/golden_report/` untouched and both `--synthetic --llm fake` validates
  unchanged. The run: exit 0, 21 model calls (plan 4, draft 8, extract 8, reask 1), 19 tool calls
  none of which raised, 4 plan steps all executed, 364 artifacts, 298 claims at **0.9966 pre-repair
  → 1.0000 over 297**, one repair round in section 3, one finding (`F-001`, `C1` at medium, ten
  candidates merged, nine evidence artifacts), two open items, 3 of 3 developer claims verified,
  $6.4858 over 1,373.77 s. It is the **excerpt run**: sections 2 and 4 verified whole before any
  repair, section 1 names the finding under D-165 and section 6 draws it under D-156, and the
  single pre-repair failure — `SHA-256` read as a claim of 256 — is in section 3, outside the
  excerpt. `report.md` is the record and is never edited; **D-168** carries the excerpt's four
  wording edits verbatim, each asserted to quote the file exactly once and none of them changing a
  number, together with the four things read and deliberately not edited and the two Phase 12
  pre-flight items the run points at. D-087 sweep: twenty row-level CSVs to
  `~/code/data-raw/credit/first-live-msr-rows/excerpt/`, 219 MB → 3.4 MB,
  `find … -size +20k` printing nothing and `git grep --cached -i loan_sequence` finding nothing.
  The substantive addition over attempt 1 is the `loan_age` partition: the forward-split shortfall
  is alike in absolute terms across the two halves and about 3.8× against 1.5× in relative terms,
  so it is neither a clean level shift nor a seasoning-shape failure, and neither half is past
  `threshold.O1.slice_auc_gap`. `docs/EVALUATION.md` carries the dated attempt-2 entry. The one
  class the run exposed is fixed in the next commit as **D-169**. No live model call, no download
  and no training on real data from any test; the only live call is the operator's run. No push.
- 2026-09-17 — **Phase 12 pre-flight, commit A** — **no live run, no live data beyond the
  operator's own `--data` path**: the two artifact-side items of the pre-flight inventory, which
  D-171 records as one decision. A `C1` candidate now cites `calibration.<split>` for every split
  it fires on, and each sub-population stores `metrics.<split>.sub.<slug>.mean_rel_gap` beside its
  `mean_predicted` and `event_rate`, both levels calling the new module-level `relative_gap()`.
  Measured offline with `quaestor validate subjects/msr_prepayment --data /tmp/msr_data --llm
  fake`, the five `package.yaml` digests verified first: F-001's evidence **9 → 11**, gaining
  `calibration.out_of_time` and `calibration.vintage_holdout` and nothing else; 273 artifacts,
  51 claims, grounding precision 1.0000, the report differing from its predecessor only in the two
  rendered tables, the appendix count 50 → 52 and the run id. `control_msr_clean`'s baseline
  evidence in `eval/taxonomy.yaml` goes three keys → five and `tests/test_seed.py` with it; D-161
  is amended with a dated consequence paragraph, not rewritten. The `(pre-flight)` assertion at
  `tests/test_live_msr.py` is discharged into a test that reads two runs and says which is which.
  Gate green: `pytest -q` **1,622 passed**, 0 failed, 0 skipped, 0 xfailed (1,618 → 1,622, four
  added and one expectation amended); coverage of `src/quaestor` **99%**; `ruff check` and
  `ruff format --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean over
  60 source files; both `--synthetic --llm fake` validates unchanged at `{E1 low}` and `{}`;
  `examples/golden_report/` untouched; `pytest tests/probatio --cassette=replay` **40 passed** with
  zero provider calls, because this commit touches no prompt. No live model call, no download, no
  training on real data from any test. No push.
- 2026-09-17 — **Phase 12 pre-flight, commit B** — **one live record sitting, killed, nothing of it
  committed**: the pre-flight inventory's items (vi), (viii) and (v), the only commit of the
  pre-flight that spends money. `DRAFT_INSTRUCTION` gains three bullets — a quantity in digits with
  its citation, no computed ratio, and a comparison that names whether it is the difference or the
  ratio — and its docstring stops claiming every rule has a checker behind it: two of the three are
  drafting rules and are labelled as such (**D-172**). `quaestor.findings.open_items` mints section
  6's `### Open items` from the sub-population gap and share, the `sign_check.*` triple and the
  feature overlap, all against bounds already in the store; `_FINDINGS_BRIEF` stops naming examples,
  `drafter.open_items_block` renders the closed list, and `eval/score.py` will import the same
  function rather than re-derive it — no `open_items` block in `findings.json`, because that is a
  schema change after Phase 1 (**D-173**). Measured over the committed real-MSR excerpt run, the
  rule mints that run's own **three** sub-populations by name plus **three** sign disagreements
  (`orig_ltv`, `sato`, `season_sin`) it never wrote — a superset, which is the direction that makes
  it a fix. The seventh record sitting was started and **killed at 3.25 of 7 cases after ~35
  minutes and $17.1014**; `draft_section.data_integrity`'s judge fell 1.000 → 0.800 on criterion 5,
  so nothing was accepted: the four rewritten tapes were copied out of the repository and their
  paths restored, the rubric and the baselines were not touched, and the two omission bullets gained
  a cross-reference to D-100's silent-omission rule (**D-174**, **D-175**, **D-176**). Gate: full
  offline suite excluding `tests/probatio` **1,599 passed**, 0 failed, 0 skipped, 0 xfailed
  (1,582 → 1,599, seventeen added and three expectations amended); coverage of `src/quaestor`
  **99%**; `ruff check` and `ruff format --check` clean on `src tests eval subjects`;
  `mypy --strict src/quaestor` clean over 60 source files; both `--synthetic --llm fake` validates
  unchanged at `{E1 low}` and `{}`; the real-panel fake validate's one `C1` unchanged at eleven
  evidence keys; `examples/golden_report/` untouched. **[stranded]** `pytest tests/probatio
  --cassette=replay` is **7 failed, 33 passed** with zero provider calls: the seven drafting tapes
  are knowingly left stranded and are recorded after lean D with the pricing runs, in batches of at
  most three cases from a plain shell (D-174). No download, no training on real data from any test.
  No push.
- 2026-09-17 — **Phase 12 pre-flight, commit C** — **no live run, no live data, no provider call,
  no recording**: the inventory's item (i), the free one, and the cut list's step 2 — it lands
  before any paid run because a tool that crashes mid-run without it costs the whole run. A
  `ToolError` from the rule-based plan no longer ends the run: `_run_checklist` records a
  `FailedCheck`, Appendix D carries `` `check_collinearity` (M1) | did not run: <message> `` as its
  first row and skips that tool in the rows below, `tools_run` and `checks_without_candidates`
  exclude it, the `tool_call` trace event gains `error`, and a conditional `{extra}` block tells
  section 1 to say the validation is incomplete. `run_model` stays fatal — everything after it
  reads what it wrote — and `quaestor validate` now exits **0** with a partial checklist and **1**
  when the subject will not run, a narrowing of D-082's contract the operator signed before the
  commit (**D-177**, with dated amendments on **D-088** and **D-082**). Gate: full offline suite
  excluding `tests/probatio` **1,609 passed**, 0 failed, 0 skipped, 0 xfailed (1,599 → 1,609, ten
  added); coverage of `src/quaestor` **99%**; `ruff check` and `ruff format --check` clean on
  `src tests eval subjects`; `mypy --strict src/quaestor` clean over 60 source files; both
  `--synthetic --llm fake` validates unchanged at `{E1 low}` and `{}`; `examples/golden_report/`
  untouched; **`python tests/probatio/casebuilder.py` rebuilds all three case files byte-identical
  — 0 of 10 cases move, which is what makes this commit free**. **[stranded]** `pytest
  tests/probatio --cassette=replay` is **7 failed, 33 passed** with zero provider calls, unchanged
  from `06900d1`: the same seven drafting tapes, no new stranding. No download, no training on real
  data from any test. No push.
- 2026-09-17 — **Phase 12 pre-flight, D-178** — **no live run, no provider call, no recording**:
  two defects the free `rules_only` sweep over the eighteen seeded variants found, which is what
  the cut list put that sweep before any paid run for. `written_number`'s `.12f` was a precision
  ceiling rather than a rounding, so `challenger.brier` of **3.2264600208103315e-13** on
  `msr__L1__eom_balance` reached the prose as "is 0.0" — a number the artifact does not hold, in
  the one configuration whose grounding is 1.0 by construction — and the decimal count now comes
  from the value's own exponent with twelve decimals kept as a floor, so no number written before
  this moves. Separately and **pre-existing**, `wrap_unverified` paired a failed claim to a prose
  token by value alone and so mispaired on any section that repeats a value: `⟦unverified: 0⟧`
  was printed around `ablation.burnout.delta_auc`, whose claim verified, while the incorrect
  number was left bare; a claim is now wrapped inside its own sentence, with the value-only
  search kept as the fallback. Measured: exactly **one** scalar of the eighteen variants falls
  below the old ceiling, the next-smallest anywhere being **2.93905e-06**, and no committed report
  carries a wrapper at all, so defect two had never been seen in an artifact. `msr__L1__eom_balance`
  re-run: **0.9969 → 1.0000** pre and post, 317 verified + 1 unattributed → **318 verified, 0
  unattributed**, no wrapper, finding set `{L1 high, X1 high}` unchanged. Gate: full offline suite
  excluding `tests/probatio` **1,615 passed**, 0 failed, 0 skipped, 0 xfailed (1,609 → 1,615, six
  added, each verified to fail against the old code); `ruff check` and `ruff format --check` clean;
  `mypy --strict src/quaestor` clean over 60 source files; both `--synthetic --llm fake` validates
  unchanged at `{E1 low}` and `{}`; `examples/golden_report/` untouched. **[stranded]** `pytest
  tests/probatio --cassette=replay` unchanged at **7 failed, 33 passed**, zero provider calls: this
  commit touches no prompt. No push.
- 2026-09-17 — **Phase 12 pre-flight, steps 4 and 5** — **three live runs, $12.3290, no code
  change and no recording**: the cut list's pricing runs, made before commit D so that the
  measurement sets the harness's parameters rather than arriving after them, and its re-quote.
  `plain_llm` on `credit__C1__smote_uncalibrated` **$1.5622** over 8 calls in 461 s; `full_agent`
  on the same **$5.2635** over 20 calls in 1,019 s; `full_agent` on
  `msr__C1__oversampled_hazard` **$5.5033** over 17 calls in 1,305 s — **29% and 4% under** their
  $2.20 and $5.50 estimates. Both `full_agent` runs at grounding **1.0000** pre and post with no
  repair round, raising exactly the sets `rules_only` raised (`{T1 high, C1 medium, E1 low}` and
  `{C1 medium}`); `plain_llm` at **0.0000** over 106 claims with ten findings across ten classes,
  which is D-072's arm working. First live sight of commit B's rules on a seeded variant: section
  6's minted open items carry two `utilisation > median(utilisation)` sub-populations and the
  `limit_bal` sign disagreement, the last of which reached no report before D-173. Measured:
  subject is **not** the volatile cost term (MSR +4.6% per run, **+23.8% on drafting alone**) —
  the loop's step count and the reask rate are, one reask pair costing **16.2%** of a run, which
  is the argument for `--max-cost` per chunk (**D-179**). Re-quote: **$170.15 over 62 paid runs**,
  **$227.58–230.58 all-in**, and the runtime corrected from "≈6–7 h" to a measured **≈10.85 h in
  about 19 sittings** — with this session's own ≈18 h figure recorded as wrong, it having applied
  `full_agent`'s duration to the `plain_llm` arm (**D-180**). The three run directories stay
  outside the repository, with their cassettes. Gate: no source file touched, so the offline suite
  stands where `8a01b49` left it at **1,615 passed**; `ruff` and `mypy --strict` clean.
  **[stranded]** `pytest tests/probatio --cassette=replay` unchanged at **7 failed, 33 passed**.
  No push.
- 2026-09-17 — **Phase 12 pre-flight, commit D lean** — **no live run, no live data, no provider
  call, no recording**: the cut list's step 6, three things and nothing else. **`quaestor study
  run`** (`eval/run_study.py`, loaded from beside the taxonomy as `seed.py` is) runs the study one
  **chunk** at a time — a chunk being one invocation, about 35 minutes and two `full_agent` runs
  (D-174) — and resumes from a `ledger.json` rewritten after every cell through a temporary name
  and a rename, carrying per `(variant, configuration)` cell the status, the attempt count, the
  cost, the wall clock, both grounding figures, the finding classes and **`checks_failed`**;
  `--max-cost` is **two** ceilings, one before a cell starts so that a chunk ends on a cell
  boundary and one before every model call so that a run doubling its own drafting bill is stopped
  (D-179's 16.2% re-ask pair), priced from D-179's measured table until the ledger has a cell of
  its own to price from, and an unpriced completion under a ceiling is an error rather than a free
  call. A capped chunk exits **0** as a finished one does, so a driver reads `remaining`, and a
  cell that reported without a check is `done` with a non-empty `checks_failed` — **D-177** carried
  from one run to a study of them (**D-181**). **`eval/score.py`** reads `findings.json`,
  `claims.json`, `trace.jsonl` and `artifacts/index.json` and never the prose, and refuses three
  things rather than defaulting them: a variant whose seeded class's check did not run, a control
  whose baseline the taxonomy records as `null`, and a collateral pairing `docs/STUDY.md` §5 did
  not decide in advance (**D-182**). Measured on the **eighteen free `rules_only` directories**:
  **14/14 detected** (`C1` 2/2, `D1` 1/1, `L1` 3/3, `L2` 2/2, `M1` 1/1, `R1` 1/1, `S1` 2/2, `T1`
  1/1, `X1` 1/1), **0 false alarms over four controls**, **0 collateral spurious**, **0
  unjudged**, **precision 1.0000**, grounding 1.0000 mean and minimum, scorer exit 0 with nothing
  owed. Two things the human decided on the sweep's evidence and this commit carries. **The two
  perturbed controls' synthetic baselines are written into `eval/taxonomy.yaml`** —
  `control_credit_perturbed` `{E1 low}`, `control_msr_perturbed` `{}`, each its clean control's and
  the credit one to the artifact hash — so the false-alarm denominator is four controls and not
  two; both `real` cells stay `null`, and the MSR row records that the shuffle is not
  value-neutral (`challenger.auc` 0.7337 → 0.7000) though it changes no finding set (**D-184**).
  **And `msr__S1__vintage_shift` raising `C1 medium` is §5's sixth collateral rule, a true
  consequence, dated today**: the hazard is fitted through 2019 and tested on the 2020–21
  refinancing wave, which is the mechanism **D-161** measured on the real MSR control and recorded
  as a true finding there, and a mechanism cannot be true on a real panel and spurious on a
  synthetic one built to carry it; every rule now carries the date it was decided and
  `summary.json` prints it, five reading 2026-09-09 and one 2026-09-17 (**D-182**, amended).
  **`quaestor study build --data`** is the flag, the pass-through to `load_package` (so a
  manifest is verified at build time) and `SEED.yaml`'s `mode: real`; the four recipes needing a
  column the real sample does not carry are skipped by name, which is ten of the fourteen recipes
  and thirteen of the eighteen variants, and **D-137 takes a dated amendment** (**D-183**). Not in
  this commit, by the cut list: the four CSV transforms, the open-items descriptive column and the
  cost/latency aggregation. Gate: full
  offline suite excluding `tests/probatio` **1,699 passed**, 0 failed, 0 skipped, 0 xfailed
  (1,615 → 1,699, 84 added); coverage of `src/quaestor` **99%**, `cli.py` at 100%; `ruff check`
  and `ruff format --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean
  over 60 source files; both `--synthetic --llm fake` validates unchanged at `{E1 low}` and `{}`;
  `examples/golden_report/` untouched. **[stranded]** `pytest tests/probatio --cassette=replay`
  unchanged at **7 failed, 33 passed**, zero provider
  calls: this commit touches no prompt. No download, no training on real data from any test. No
  push.
- 2026-09-18 — **Phase 12, chunk 1 and the results-tree rule** — **no provider call, no live data,
  $0.0000**: the study's first chunk, `rules_only` over all eighteen variants through
  `quaestor study run` itself rather than a hand-driven sweep, written to
  `eval/results/20260918T065257Z/` with `--max-cost 0` — a ceiling a free arm must not touch, and
  did not. **18 cells run, 0 failed, 0 remaining, 66 s of subject time**, grounding precision
  1.0000 pre- and post-repair on every one over 200–330 claims, and **0 cells with
  `checks_failed`**, so commits C and D's crash path stayed dormant. **All eighteen finding sets
  are byte-identical to the pre-commit-C/D sweep**, 18 of 18, nothing gained or lost. Scored:
  **14/14 detected** (`C1` 2/2, `D1` 1/1, `L1` 3/3, `L2` 2/2, `M1` 1/1, `R1` 1/1, `S1` 2/2, `T1`
  1/1, `X1` 1/1), four controls, **0 false alarms, 0 collateral spurious, 0 unjudged, 0 not
  scorable, precision 1.0000**, `eval/score.py` exit 0 with nothing owed; the seven collateral
  findings carry their provenance, six dated 2026-09-09 and one 2026-09-17. Two things shipped
  with it. `summary.json` now carries **the date it was scored**, UTC to the second and spelled as
  a report's front matter spells `generated`, because the published file travels without the
  directory whose name carries the stamp. And **what of a study run enters the repository is a
  `.gitignore` rule** (**D-185**), decided on chunk 1's own measurement — 104 MB of artifact
  stores, 87 MB of `run/` output, 8.9 MB of documents — before the four paid arms write anything:
  timestamped working directories out, `published/` in without its artifact stores,
  `first-live/` untouched, and **`run/*.csv` out of every results directory**, because a `--data`
  run writes the real panel there and Phase 9 was keeping it out by hand. Gate: offline suite
  excluding `tests/probatio` **1,702 passed**, 0 failed, 0 skipped, 0 xfailed (1,699 → 1,702,
  three added); `ruff check` and `ruff format --check` clean on `src tests eval subjects`;
  `mypy --strict src/quaestor` clean over 60 source files. **[stranded]** `pytest tests/probatio
  --cassette=replay` unchanged at **7 failed, 33 passed**. Chunk 1's 200 MB tree stays on disk and
  out of the repository. Pushed.
