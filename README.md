# Quaestor

**SR 11-7-*shaped*, not a compliance product. Quaestor is not compliant, not certified, and not
suitable for regulatory submission. No bank data, no proprietary data, no personal data: the two
subjects are the author's own models rebuilt small, and everything published here ran on
synthetically generated panels.**

Quaestor is an agentic model-validation copilot. It takes a *model package* — the subject's code, a
reference to its data, its fitted artifacts and the developer's own declared thresholds and claims
— runs a fixed set of deterministic checks over it in a capped subprocess, and drafts a validation
report shaped after the interagency model-validation guidance, **SR 11-7 as revised by SR 26-2**
(the Fed / OCC / FDIC *Revised Guidance on Model Risk Management*, 2026-04-17, whose "Supersedes"
field lists SR 11-7). Both letters are in the retrieval corpus, SR 26-2 as the drafter's default
and SR 11-7 kept so that citations written before April 2026 still resolve.

Every quantitative claim in the prose carries a machine-checked citation to a computed artifact;
every finding is a structured object that cannot be constructed without an evidence artifact that
exists in the store; and the report prints its own grounding precision, before and after repair, on
its first page.

What makes it worth reading rather than another wrapper is the open evaluation: defects are seeded
into the author's own rebuilt models, and detection, the false-alarm rate and per-report grounding
precision are published — misses included.

---

## The result, stated plainly

On the study published in `eval/results/published/` — 54 cells, both subjects, synthetic data,
`claude-opus-5[1m]` through the Claude Code CLI:

**`full_agent` and `rules_only` both detect 14 of 14 seeded defects, with 0 false alarms on the
four controls. The LLM adds no detection over the deterministic checks on this study.**

`plain_llm` — the same model given the subject's own output files and no tools, no checks and no
verifier loop — detects 8 of 14, raises 16 false alarms across the four controls, and reaches a
grounding precision of 0.0004.

What the LLM *does* add on this study, measured rather than asserted:

- **narrative** — the `rules_only` arm's report is template text listing each candidate; the
  `full_agent` arm's is prose that states the mechanism, and the anchor comparison below is one
  reading of whether that prose is worth anything;
- **guidance citations** — retrieved regulatory spans cited by section id in the report text;
- **the bounded loop's two conditional slices** on the clean credit control
  (`metrics.test.sub.delinq_count_6m_low.auc` 0.6599 at a gap of 0.08813, and
  `metrics.test.sub.utilisation_high.auc` 0.5689 at a gap of 0.1791, both against the open-item
  bound `threshold.O1.slice_auc_gap` of 0.08), which the human validation did not attempt at all;
- **grounding precision 1.0000 post-repair** (0.9950 mean pre-repair, 0.9840 worst), against
  `rules_only`'s trivial 1.0000 and `plain_llm`'s 0.0004.

That is the honest summary: on these fourteen variants the deterministic checks are the detector,
and the model is the writer. Sections below give the per-class table, the misses by variant, and
the limits.

---

## Quick start

Offline, with no API key, no network and no data to download. Both shipped subjects generate a
small panel from a known process, and `--llm fake` is a deterministic offline provider that ships
with the package.

```bash
pip install -e .
quaestor validate subjects/credit_default --synthetic --llm fake --out /tmp/quaestor-demo
head -40 /tmp/quaestor-demo/report.md
```

That writes `report.md`, `claims.json`, `findings.json`, `trace.jsonl` and the content-addressed
artifact store under `--out`. The report's front matter carries its grounding precision before and
after repair; Appendix A lists every numeric claim with its citation, its status and the artifact
value it was checked against; Appendix B is the artifact index every citation resolves into;
Appendix D says what was not checked and why.

`quaestor validate --help` names the rest: `--data DIR` instead of `--synthetic` for a real sample,
`--llm anthropic` or `--llm claude-cli` for a live run, `--config rules_only|plain_llm` for the two
comparison arms, and `--record-cassettes DIR` to keep every model call a live run made.
`quaestor tool NAME --pkg PKG --run-dir DIR` runs one check on its own.

---

## What a report looks like

Verbatim from `eval/results/first-live/credit/report.md` — a live `full_agent` run of
`credit_default` on the **real** UCI *Default of Credit Card Clients* sample, 210 claims, grounding
precision 1.0000 before repair and 1.0000 after, 0 findings at any severity:

> On the held-out split, discrimination clears the declared floor, at 0.755
> `[[art:365b7034:metrics.test.auc]]` against a minimum of 0.7
> `[[art:8bfd02cc:threshold.package.auc.test.min]]`.
> The mean squared error of the predicted probabilities is 0.1385
> `[[art:86e93c8f:metrics.test.brier]]`, inside the declared ceiling of 0.2
> `[[art:d0f98b9c:threshold.package.brier.test.max]]`.
> The calibration slope is 0.9886 `[[art:e06564c7:calibration_slope.test]]`, inside the declared
> band running from 0.8 `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` to 1.2
> `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]`.

Each `[[art:<hash8>:<logical_name>]]` resolves into the run's own artifact store, and the developer's
declared thresholds are themselves stored as artifacts so the report can cite the bound as well as
the value. The threshold values are recomputed from the subject's scored output rather than read
from the developer's own `metrics.json`.

**This excerpt is not a detection result.** It is the clean control: a package that passes every
bound it declares, and what it demonstrates is evidence and citation, not that anything was caught.
`docs/EVALUATION.md` carries a *"What the excerpt does not show"* subsection listing what this run
misses — decile reversals no rule reads, a sign disagreement the report qualifies rather than
routes, and mixed SR 26-2 / SR 11-7 citations where retrieval returned no span for a point.

---

## The seeded-defect study

Source for every number in this section: `eval/results/published/summary.json` and
`eval/results/published/report.md`, scored 2026-09-20T23:31:20Z from the run in
`eval/results/20260918T065257Z` at commit `8959d5c`. Protocol: `docs/STUDY.md`.

Detection criterion, fixed before the run: a finding **of the seeded class** at severity **medium or
above**. Counts, never percentages — n is one or two variants per class. Nothing is read from a
report's prose; the scorer reads `findings.json` and the traces.

| defect class | seeded n | `rules_only` | `plain_llm` | `full_agent` |
|---|---:|---:|---:|---:|
| `L1` target leakage | 3 | 3 | 3 | 3 |
| `L2` train/test contamination | 2 | 2 | 0 | 2 |
| `R1` regime-dependent feature | 1 | 1 | 0 | 1 |
| `C1` miscalibration | 2 | 2 | 2 | 2 |
| `S1` population shift | 2 | 2 | 1 | 2 |
| `M1` multicollinearity | 1 | 1 | 1 | 1 |
| `D1` data integrity | 1 | 1 | 0 | 1 |
| `T1` false developer claim | 1 | 1 | 0 | 1 |
| `X1` scenario inconsistency | 1 | 1 | 1 | 1 |
| **all** | **14** | **14** | **8** | **14** |

### False alarms on the four controls

A false alarm is any finding at medium or above that the control's own measured baseline does not
carry.

| control | `rules_only` | `plain_llm` | `full_agent` |
|---|---:|---:|---:|
| `control_credit_clean` | 0 | 2 | 0 |
| `control_credit_perturbed` | 0 | 4 | 0 |
| `control_msr_clean` | 0 | 6 | 0 |
| `control_msr_perturbed` | 0 | 4 | 0 |
| **all** | **0** | **16** | **0** |

### The misses, by variant

`rules_only` and `full_agent` miss nothing on these fourteen. `plain_llm` misses six, and what each
report said instead is in `eval/results/published/report.md`:

- `credit__D1__test_only_missingness`
- `credit__L2__contamination`
- `credit__R1__regime_flip`
- `credit__S1__segment_shift`
- `credit__T1__false_claim`
- `msr__L2__contamination`

### Precision, and the caveat that governs it

| configuration | precision |
|---|---:|
| `rules_only` | 1.0000 |
| `plain_llm` | 0.3333 |
| `full_agent` | 1.0000 |

**Read `1.0000` as precision over the pairings decided in advance, and not as precision over
everything the run raised.** `docs/STUDY.md` §5 fixed judgements for a small set of collateral
pairings — a finding of a class the variant was *not* seeded with — before any variant ran. The run
raised collateral outside that set, and `score.py` set every one of those aside as **`unjudged`**:
in neither the numerator nor the denominator. In the published scoring that is **46 unjudged
collateral findings, over 44 distinct (variant, class) pairings, all of them in `plain_llm`**;
`full_agent` and `rules_only` produced none. The 17 collateral findings that *were* covered by a
rule fixed in advance are all judged `true_consequence`; 0 are judged spurious, in any arm.

They are left unjudged deliberately. A verdict written after the numbers were seen is a different
object from a rule fixed before them, and judging them now would make the study's main claim a
construction of its own results. `docs/STUDY.md` §9, Amendment 1 is where this is decided.

> **A correction, recorded rather than quietly fixed.** Amendment 1 states that the run produced
> **93** collateral findings set aside as unjudged. That figure does not come from the published
> scoring. `eval/results/published/summary.json` carries `collateral_unjudged: 46`, and 93 is the
> line count of the string `unjudged` in `eval/results/published/report.md`, where each finding is
> printed twice — once in the collateral table and once in the "what was not scored" list — plus
> one line of prose: 46 + 46 + 1. The counts above — **46 findings over 44 distinct pairings** —
> are read from `summary.json`, which is what the scorer wrote. `docs/STUDY.md` §9 **Amendment 3**
> corrects the count and leaves Amendment 1 as written, because a dated amendment that is silently
> edited is not a dated amendment (D-198).

### Grounding precision

| configuration | reports | pre mean | pre min | post mean | post min |
|---|---:|---:|---:|---:|---:|
| `rules_only` | 18 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `plain_llm` | 18 | 0.0004 | 0.0000 | 0.0004 | 0.0000 |
| `full_agent` | 18 | 0.9950 | 0.9840 | 1.0000 | 1.0000 |

`rules_only`'s 1.0000 is trivial: template text emits only numbers it has already cited.
`plain_llm`'s 0.0004 is the baseline held to the same rule as the product — it writes numbers, and
essentially none of them carry a citation that resolves. `full_agent`'s figure is the one that
means something: 0.9950 mean before repair, worst report 0.9840, and **1.0000 on every one of the
18 reports after repair**.

### Cost and wall-clock

Summed from the per-cell figures in `eval/results/published/ledger.json`, which records each cell's
**last attempt only**; discarded attempts are excluded and are accounted for in `docs/STUDY.md` §9.

| configuration | cells | model calls | cost | median cell wall-clock |
|---|---:|---:|---:|---:|
| `rules_only` | 18 | 0 | $0 | 2.7 s |
| `plain_llm` | 18 | 144 | $28.4699 | 472.8 s |
| `full_agent` | 18 | 356 | $98.7958 | 1,233.9 s |
| **all** | **54** | **500** | **$127.2657** | — |

### What this study is not

Written here rather than left for a reader to find.

- **It is synthetic on both subjects.** All 54 cells ran in `--synthetic` mode. The two real-data
  bridge runs planned for the study were **not made**, and the four CSV-level transforms they
  needed were never built (`docs/STUDY.md` §9, Amendment 1, item 3).
- **Stability repeats were cut.** One run per (variant, configuration) pair for the headline table.
  No Wilson intervals, no repeat-to-repeat variance (Amendment 1, item 2).
- **`pytest tests/probatio --cassette=replay` stands at 7 failed / 33 passed** and is **not fixed in
  this version.** All seven failures are `draft_section` cases whose committed cassettes no longer
  replay into the same prompt hash; zero provider calls are made either way (D-188, and Amendment 1,
  item 6). The published study's own cassettes are committed under
  `eval/results/published/cassettes/`, but re-rendering a cell from them is a known gap, not a
  demonstrated property.
- **Two subjects, one to two variants per class, one model, one run per pair**, and the defects were
  seeded by the same person who wrote the checks. The study measures whether the agent finds what
  its author knows to plant — not what it would find in the wild.
- **Two recipes clear their bounds thinly** on synthetic data
  (`credit__L1__after_outcome_hidden` at 0.945 against 0.90; the SMOTE slope arm at 0.795 against
  0.80).
- **The grounding judge used in the test layer fails about one reply in ten on its own tapes**,
  beside a Cohen's kappa of 0.771 against a human labeller over 40 rows.

---

## Verifier component evaluation

The claim verifier was measured on its own, off the pipeline, on FinQA and TAT-QA — the standard
numeric-reasoning benchmarks — used here only as a source of arithmetic-answer items. Run
2026-09-20 on `claude-opus-5[1m]` through `ClaudeCLILLM`: **100 items (50 FinQA, 50 TAT-QA) and
their 300 sentences**, $8.0857 over 100 model calls, cassettes committed under
`eval/results/verifier-eval/`. The protocol asks for 150 items per dataset; the operator cut the
sample to 50 per dataset to fit the study's budget, before the first live call (D-194), and the cut
is a field of `verifier_eval.json` and the first line the command prints.

| expected status | accuracy |
|---|---:|
| `verified` | 1.0000 |
| `mismatch` | 0.9900 |
| `unsupported` | 1.0000 |

Extraction recall 0.9967; 0 re-asks over 100 extractions. The single error in 300 sentences is a
`mismatch` the verifier did not flag, and it is the whole of the 0.9900.

**False-verified is 0 for all five perturbation types — `relative_up` 0/24, `relative_down` 0/19,
`digit_transposition` 0/19, `decimal_shift` 0/20, `percent_ratio_confusion` 0/18 — and that zero is
weaker evidence than it looks.** The templates render four decimals and a claim verifies at the
precision the prose used, so a 5–15% perturbation is essentially always outside the tolerance. The
tolerance boundary the protocol asks to be reported as a boundary is **empty here**: no perturbation
small enough to sit inside it was ever drawn. A sharper test would perturb at the fourth decimal;
it was not run.

Full write-up: `docs/EVALUATION.md`, *Verifier component evaluation*.

---

## Human anchor: one manual validation against the copilot's

[`docs/anchor/COMPARISON.md`](docs/anchor/COMPARISON.md) sets the author's own manual validation of
the clean `credit_default` package — committed at `225d902`, **before the copilot's report was
opened** — beside the copilot's report of the same package.

**This is n = 1: one subject, one validator, one run. It is an anchor for reading the reports, not
an evaluation, and nothing in it generalises.** On that one package the copilot cites strictly more
than the human and misses nothing the human found; the human's contribution is a single promotion
judgement (whether three consistent coefficient sign reversals are a finding or an open question),
and the copilot's is coverage the human did not attempt — principally the two conditional slices its
bounded loop chose to compute.

---

## Where the checks come from

Every check encodes a practice the author performed by hand as a model validator or on their own
models, and every seeded defect class names the concrete instance it was met in.
`docs/CHECKLIST.md` carries the full mapping; the shape of it:

| practice | check | classes |
|---|---|---|
| Declared thresholds with explicit pass/fail rules | every `package.yaml` bound re-evaluated against recomputed values | `T1` |
| Sensitivity scenarios over holding-period assumptions | rate-shock sweep, monotonicity and convexity against the declared expectation | `X1` |
| Classifying relationships as stable, regime-dependent or unreliable | per-regime coefficient sign and AUC across a declared split | `R1` |
| Beginning-of-month lagging to remove payoff-balance leakage | feature-timing declarations against the outcome window; target-adjacency screen | `L1` |
| Holdout hygiene: no subject on both sides of the split | identifier and feature-vector overlap against a within-train duplicate baseline | `L2` |
| Leave-one-vintage-out split over an unseen refinancing wave | metrics on declared out-of-time and vintage-holdout splits; PSI train-vs-test | `S1`, `O1` |
| Calibration and CPR fit prioritised over AUC at a low event rate | calibration slope and intercept, Brier, decile table, section order by event rate | `C1` |
| VIF-based feature screening | VIF and Belsley condition number on the retained design; sign check against univariate direction | `M1` |
| Champion vs challenger under several imbalance strategies | effective challenge at library defaults; SMOTE-without-recalibration shows in calibration | `E1`, `C1` |
| Input completeness before scoring | missingness per feature per split | `D1` |

Score mapping with SHAP/LIME is out of scope and is noted as a monitoring recommendation, not a
check.

---

## Prior art

**Every claim in this section was checked against the vendors' current documentation on
2026-09-20, with the URL and the quoted text recorded in [`notes/prior-art.md`](notes/prior-art.md).
Three claims this project carried in its own planning documents turned out to be wrong or stale on
that date and have been corrected rather than repeated.**

**[ValidMind](https://validmind.com/)** is the commercial reference. It describes itself today as
*"The Enterprise AI Governance Platform for regulated organizations"* rather than as an MRM
platform, sells to banks and insurers, and automates documentation and testing —
*"GenAI-assisted creation of validation reports, regulatory deliverables, and audit-ready
documentation"* — aligned to **SR 26-2**, E-23 and SS1/23. Its documentation names four LLM-powered
features, of which the *Document Checker* is the nearest neighbour to Quaestor's verifier: it
reviews a document against regulatory requirements, where Quaestor's verifier matches each number
in the prose against a computed artifact. **It is not closed.** The hosted platform is proprietary,
but the *ValidMind Library* — the client-side test and documentation framework — is dual-licensed
AGPL-3.0 or commercial, and *Atryum*, their agent-governance layer, is Apache-2.0. Its existence
proves the workflow is worth automating.

**[deepchecks](https://github.com/deepchecks/deepchecks)** is the open-source reference: AGPLv3,
component-level data and model suites whose named checks include Feature Drift, Label Drift,
Multivariate Drift, Index Leakage and Date Train-Test Leakage — roughly the ground Quaestor's
`profile_data` and `check_leakage` cover. Its output is a `SuiteResult`: check-by-check pass/fail,
exported as HTML or JSON. It does not draft a narrative validation report in which each number
carries a citation, and it does not structure its output around the model-validation guidance —
though "follows no regulatory structure" would overstate it, since they publish content on bank MRM
quoting the OCC's 2011 guidance. Two things a reader should know: the company was **acquired by
Check Point in May 2026** (team and IP), and the open-source project has shipped no release since
**December 2024**, so it is unarchived and AGPL-licensed but cannot be called actively maintained.
They also now sell a separate commercial LLM Evaluation Platform, which was not characterised.

**What neither publishes, on the searches recorded in `notes/prior-art.md`: a measured detection
rate against seeded defects, or a per-report grounding precision.** ValidMind's
`ai-testing-results` page reports a *Faithfulness* metric — statement-by-statement traceability of
a response to its source material — which is the closest analogue found, and it is grounding
against source text rather than detection against planted defects. These are negative search
results with their limits stated, not proofs of absence: neither vendor's full blog archive was
read, and deepchecks' JMLR paper could not be parsed.

That gap is the niche. Quaestor is an open, evaluated, agent-based validator in the shape of the
guidance — with the caveat, restated, that it is **not a compliance product**, and with a study
whose headline result is that on these fourteen variants the deterministic checks do the detecting
and the model does the writing.

Openlayer, ModelOp, CIMCON and the rest of the adjacent commercial MRM space are **not compared
here**, because they were not checked on the stated date and an unverified comparison is not worth
publishing.

---

## Test layer

Quaestor is [Probatio](https://github.com/Lexieli666/probatio)'s first external user. The LLM-facing
components — the section drafter, the claim extractor and the repair loop — are tested as Probatio
cases with committed cassettes, so CI replays recorded calls and makes **zero provider calls**:

- `draft_section` asserts every number in a drafted section carries a citation and that no
  `⟦unverified⟧` wrapper survives, under `@order_invariant` over artifact order, `@format_jitter`
  over the guidance spans and `@distractor_robust` with an irrelevant artifact appended, plus a
  judge scored against a grounding rubric;
- `extract_claims` asserts the extractor's JSON schema and expected values, run with `--runs 5`;
- `plan_followup` asserts the bounded loop's action schema and that it never names an unknown tool.

The judge rubric was validated against 40 human labels: agreement 0.950 (38/40), Cohen's kappa
0.771, both label distributions 35 pass / 5 fail. That figure is recorded as it stands; the rubric
was not revised on the strength of those labels, because tuning it to them is choosing a threshold
on a test set.

**Current status: `pytest tests/probatio --cassette=replay` is 7 failed, 33 passed** — the seven
`draft_section` cases, whose cassettes no longer replay into the same prompt hash (D-188). This is
not fixed in this version.

The rest of the suite is ordinary `pytest`: no live model call is made in any code path the test
suite exercises, no test downloads data, and no test trains on real data.

---

## Install

```bash
pip install -e .                 # runtime: pydantic, PyYAML, numpy, pandas, scikit-learn, jsonschema
pip install -e ".[anthropic]"    # the Anthropic SDK adapter
pip install -e ".[dev]"          # pytest, probatio-llm, ruff, mypy, coverage
```

Python 3.11 or 3.12. Distribution name `quaestor-mrm`, import name `quaestor`, console script
`quaestor`. MIT licensed. Anthropic is the only live provider shipped: `AnthropicLLM` over the SDK
and `ClaudeCLILLM` over the Claude Code CLI as a subprocess.

The regulatory corpus is built from public U.S. government documents the operator downloads once
(`data/README.md`) with `quaestor corpus ingest`; the extracted JSONL is committed.

---

## Documentation

| file | what it holds |
|---|---|
| `docs/DESIGN.md` | every non-obvious choice, with the alternative it rejected |
| `docs/CHECKLIST.md` | practice → check → defect class, and where each defect was met |
| `docs/STUDY.md` | the study protocol, its freeze date and its amendments |
| `docs/EVALUATION.md` | every measured number, with the run it came from |
| `docs/REPORT_SCHEMA.md` | the report's front matter schema and required headings |
| `docs/anchor/COMPARISON.md` | the n = 1 human anchor |
| `notes/prior-art.md` | the prior-art claims, checked against current documentation, dated |
| `DECISIONS.md` | numbered Q / A / Why entries for every judgement call |
| `eval/results/published/` | the run every number above is quoted from, with `MANIFEST.json` |

---

## Roadmap

Built and shipped: the package loader, artifact store and LLM layer; the subprocess sandbox; both
subjects; the eight tools with their statistics written by hand; the regulatory corpus and BM25
retrieval; findings and the claim verifier; the drafter, repair loop, renderer and planner; the CLI;
the seeded-defect generator and taxonomy; the Probatio test layer; the seeded-defect study; the
verifier component eval; the human anchor.

Not built:

- **The MCP server** (`quaestor mcp`, the tool registry over MCP stdio). Specified, not implemented.
- **`docs/PROVENANCE.md`**, the number-to-file map.
- **Cassette replay of a published study cell** (D-188) — the seven `draft_section` test failures
  and the study's own re-render are the same gap.
- **A real-data study.** Both subjects have real-sample scripts and both have been fitted on real
  data in one-off live runs, but the published study is synthetic throughout.
- **Repeats and intervals.** One run per pair; no Wilson intervals on detection.

---

*No number in this file comes from anywhere but `eval/results/published/summary.json`,
`eval/results/published/ledger.json`, `eval/results/published/report.md`, `docs/EVALUATION.md` or
`docs/STUDY.md`, and every one of them was produced by a run committed to this repository.*
