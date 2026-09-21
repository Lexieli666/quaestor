# Provenance: every number in this documentation, and the file behind it

`CLAUDE.md` says it twice: **no number in `README.md`, in `docs/` or in a report that a committed
run did not produce.** This file is the index that makes that rule checkable rather than
aspirational. `tests/test_docs_provenance.py` reads the tables below, runs each row's check against
the file it names, and fails the suite when a document and its source disagree — in either
direction, so a figure edited in prose fails and a source re-scored without updating the prose
fails too.

The half that cannot be satisfied by writing more prose is the **sweep**: every numeral in
`README.md` is stripped by one of the two tables below, and whatever is left over fails the test by
name. A number added to the README stays a failure until somebody names the committed file it came
from.

## How to read a row

- **number** — the figure exactly as it appears in the prose, with any `**` emphasis removed.
- **appears in** — every document that prints it. A number printed in two documents has one row,
  unless two *different* measurements print the same string, which is why `18` has several rows:
  the eighteen reports per configuration and the eighteen cells per configuration are the same
  integer measured two ways, out of two different files.
- **source file** — the committed file it came from. Where one document quotes a figure another
  document already carries, the source is that document, and the last table records which test
  guards it; the chain always ends at a file a run wrote.
- **check** — how the figure is tied to the file. `text` means the number's string is present in
  the source. Everything else names a derivation `run_check` recomputes and formats to the decimals
  the prose prints:
  - `json <path>`, `json-int <path>`, `json-len <path>` read a dotted path out of a JSON document;
  - `detected <config>`, `missed <config>`, `seeded-scored <config>`, `reports <config>` and
    `precision <config>` read the scorer's own fields for one configuration;
  - `per-class <config> <class> <column>` reads one cell of the detection table;
  - `false-alarms <config> [control]` counts the scorer's false alarms, optionally for one control;
  - `grounding <config> <field>` reads a grounding-precision figure;
  - `collateral <config|all> <verdict>` counts collateral findings by verdict and
    `collateral-pairings <config|all> <verdict>` counts the distinct `(variant, class)` pairings
    they fall on — the two numbers the D-198 correction turns on;
  - `ledger-cells <config|all>`, `ledger-sum <config|all> <field>` and
    `ledger-median-seconds <config>` aggregate the published run's per-cell ledger;
  - `front-matter <key>` reads a report's YAML front matter;
  - `verifier-false-verified <perturbation> <field>` reads the component eval's per-perturbation
    counts.

  A check the test does not implement raises rather than passing.
- **regenerate** — the command that rebuilds the source file. `—` means the file is not a run
  output: a committed constant, a protocol document, or the run log itself.

Three commands recur and are written once here rather than in sixty rows:

```bash
# R1 — the published seeded-defect study, 54 cells, synthetic, claude-opus-5[1m]
quaestor study run --variants eval/variants --configs full_agent,rules_only,plain_llm \
        --llm claude-cli --model claude-opus-5[1m] --out eval/results/<ts>
quaestor study score --results eval/results/<ts>

# R2 — the verifier component eval, 100 items over FinQA and TAT-QA
quaestor verifier-eval --finqa <dev.json> --tatqa <dev.json> --n 100 --seed 20260901 \
        --llm claude-cli --model claude-opus-5[1m] --out eval/results/verifier-eval

# R3 — the first live validation of credit_default on its real UCI sample, the README's excerpt
quaestor validate subjects/credit_default --data <dir> --llm claude-cli \
        --model claude-opus-5[1m] --out eval/results/first-live/credit
```

R1 and R2 cost money and call a live model. Neither is run by `pytest`, and neither may be: the
tests below read the committed outputs of the runs that were already made.

## Measurements

| number | appears in | source file | check | regenerate |
|---|---|---|---|---|
| `14` | `README.md` | `eval/results/published/summary.json` | detected full_agent | R1 |
| `8` | `README.md` | `eval/results/published/summary.json` | detected plain_llm | R1 |
| `16` | `README.md` | `eval/results/published/summary.json` | false-alarms plain_llm | R1 |
| `6` | `README.md` | `eval/results/published/summary.json` | missed plain_llm | R1 |
| `54` | `README.md` | `eval/results/published/ledger.json` | ledger-cells all | R1 |
| `18` | `README.md` | `eval/results/published/summary.json` | reports full_agent | R1 |
| `0.3333` | `README.md` | `eval/results/published/summary.json` | precision plain_llm | R1 |
| `1.0000` | `README.md` | `eval/results/published/summary.json` | precision full_agent | R1 |
| `0.9950` | `README.md` | `eval/results/published/summary.json` | grounding full_agent pre_repair_mean | R1 |
| `0.9840` | `README.md` | `eval/results/published/summary.json` | grounding full_agent pre_repair_min | R1 |
| `0.0004` | `README.md` | `eval/results/published/summary.json` | grounding plain_llm pre_repair_mean | R1 |
| `0.0000` | `README.md` | `eval/results/published/summary.json` | grounding plain_llm pre_repair_min | R1 |
| `46` | `README.md`, `docs/STUDY.md` | `eval/results/published/summary.json` | collateral all unjudged | R1 |
| `44` | `README.md`, `docs/STUDY.md` | `eval/results/published/summary.json` | collateral-pairings all unjudged | R1 |
| `17` | `README.md`, `docs/STUDY.md` | `eval/results/published/summary.json` | collateral all true_consequence | R1 |
| `63` | `docs/STUDY.md` | `eval/results/published/summary.json` | collateral-total all | R1 |
| `356` | `README.md` | `eval/results/published/ledger.json` | ledger-sum full_agent calls | R1 |
| `144` | `README.md` | `eval/results/published/ledger.json` | ledger-sum plain_llm calls | R1 |
| `500` | `README.md` | `eval/results/published/ledger.json` | ledger-sum all calls | R1 |
| `$98.7958` | `README.md` | `eval/results/published/ledger.json` | ledger-sum full_agent cost_usd | R1 |
| `$28.4699` | `README.md` | `eval/results/published/ledger.json` | ledger-sum plain_llm cost_usd | R1 |
| `$127.2657` | `README.md`, `docs/STUDY.md` | `eval/results/published/ledger.json` | ledger-sum all cost_usd | R1 |
| `1,233.9` | `README.md` | `eval/results/published/ledger.json` | ledger-median-seconds full_agent | R1 |
| `472.8` | `README.md` | `eval/results/published/ledger.json` | ledger-median-seconds plain_llm | R1 |
| `2.7` | `README.md` | `eval/results/published/ledger.json` | ledger-median-seconds rules_only | R1 |
| `210` | `README.md`, `docs/EVALUATION.md` | `eval/results/first-live/credit/report.md` | front-matter n_claims | R3 |
| `0.755` | `README.md`, `docs/EVALUATION.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `0.1385` | `README.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `0.9886` | `README.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `0.2` | `README.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `0.7` | `README.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `0.8` | `README.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `1.2` | `README.md` | `eval/results/first-live/credit/report.md` | text | R3 |
| `0.6599` | `README.md`, `docs/anchor/COMPARISON.md` | `eval/results/published/full_agent/control_credit_clean/report.md` | text | R1 |
| `0.08813` | `README.md`, `docs/anchor/COMPARISON.md` | `eval/results/published/full_agent/control_credit_clean/report.md` | text | R1 |
| `0.5689` | `README.md`, `docs/anchor/COMPARISON.md` | `eval/results/published/full_agent/control_credit_clean/report.md` | text | R1 |
| `0.1791` | `README.md`, `docs/anchor/COMPARISON.md` | `eval/results/published/full_agent/control_credit_clean/report.md` | text | R1 |
| `0.08` | `README.md`, `docs/anchor/COMPARISON.md` | `eval/results/published/full_agent/control_credit_clean/report.md` | text | R1 |
| `100` | `README.md` | `eval/results/verifier-eval/verifier_eval.json` | json-int n_items | R2 |
| `50` | `README.md` | `eval/results/verifier-eval/verifier_eval.json` | json-int n_per_dataset.finqa | R2 |
| `0.9900` | `README.md` | `eval/results/verifier-eval/verifier_eval.json` | json status_accuracy.mismatch | R2 |
| `0.9967` | `README.md` | `eval/results/verifier-eval/verifier_eval.json` | json extraction_recall | R2 |
| `$8.0857` | `README.md`, `docs/EVALUATION.md` | `eval/results/verifier-eval/verifier_eval.json` | json cost_usd | R2 |
| `24` | `README.md`, `docs/EVALUATION.md` | `eval/results/verifier-eval/verifier_eval.json` | verifier-false-verified relative_up n | R2 |
| `19` | `README.md`, `docs/EVALUATION.md` | `eval/results/verifier-eval/verifier_eval.json` | verifier-false-verified relative_down n | R2 |
| `20` | `README.md`, `docs/EVALUATION.md` | `eval/results/verifier-eval/verifier_eval.json` | verifier-false-verified decimal_shift n | R2 |
| `18` | `README.md`, `docs/EVALUATION.md` | `eval/results/verifier-eval/verifier_eval.json` | verifier-false-verified percent_ratio_confusion n | R2 |
| `300` | `README.md`, `docs/EVALUATION.md` | `docs/STUDY.md` | text | — |
| `150` | `README.md`, `docs/STUDY.md` | `docs/STUDY.md` | text | — |
| `0.771` | `README.md`, `docs/EVALUATION.md`, `docs/STUDY.md` | `docs/EVALUATION.md` | text | — |
| `0.950` | `README.md`, `docs/EVALUATION.md` | `docs/EVALUATION.md` | text | — |
| `38` | `README.md`, `docs/EVALUATION.md` | `docs/EVALUATION.md` | text | — |
| `40` | `README.md`, `docs/EVALUATION.md` | `docs/EVALUATION.md` | text | — |
| `35` | `README.md`, `docs/EVALUATION.md` | `docs/EVALUATION.md` | text | — |
| `0.945` | `README.md`, `docs/STUDY.md` | `docs/STUDY.md` | text | — |
| `0.90` | `README.md`, `docs/STUDY.md` | `docs/STUDY.md` | text | — |
| `0.795` | `README.md`, `docs/STUDY.md` | `docs/STUDY.md` | text | — |
| `0.80` | `README.md`, `docs/STUDY.md` | `docs/STUDY.md` | text | — |
| `7` | `README.md`, `docs/STUDY.md` | `PROGRESS.md` | text | — |
| `33` | `README.md`, `docs/STUDY.md` | `PROGRESS.md` | text | — |
| `93` | `README.md`, `docs/STUDY.md` | `docs/STUDY.md` | text | — |
| `3` | `README.md` | `eval/results/published/summary.json` | per-class full_agent L1 seeded | R1 |
| `2` | `README.md` | `eval/results/published/summary.json` | per-class full_agent L2 seeded | R1 |
| `1` | `README.md` | `eval/results/published/summary.json` | per-class full_agent R1 seeded | R1 |
| `0` | `README.md` | `eval/results/published/summary.json` | per-class plain_llm L2 detected | R1 |
| `4` | `README.md` | `eval/results/published/summary.json` | false-alarms plain_llm control_credit_perturbed | R1 |
| `5` | `README.md`, `docs/EVALUATION.md` | `docs/EVALUATION.md` | text | — |
| `15%` | `README.md`, `docs/EVALUATION.md` | `docs/EVALUATION.md` | text | — |

## Numerals that are not measurements

A numeral that is an identifier, a date, a citation, a version or a cross-reference is not a
measurement and has no source to re-derive it from. Each pattern below is stripped from a document
before the sweep looks at what is left.

| numeral | what it is | named in |
|---|---|---|
| `re:\[\[[a-z]+:[^\]]+\]\]` | an artifact or regulatory citation: a hash and a logical name | `docs/REPORT_SCHEMA.md` |
| `re:\bSR ?\d\d?-\d\b` | an SR letter's number — `SR 11-7`, `SR 26-2` | `DECISIONS.md` D-055 |
| `re:\bD-\d{3}\b` | a reference to a numbered entry in `DECISIONS.md` | `DECISIONS.md` |
| `re:\bAmendment \d\b` | a dated amendment to the study protocol | `docs/STUDY.md` |
| `re:§\d+(\.\d+)?` | a section reference | — |
| `re:\bitem \d\b` | a numbered item inside an amendment | `docs/STUDY.md` |
| `re:20\d\d-\d\d-\d\d(T[\d:]+Z)?` | a date, or a scoring timestamp | — |
| `re:\b20\d\d\b` | a bare year | — |
| `re:\b20260918T065257Z\b` | the study run's directory name, which is its start timestamp | `eval/results/published/MANIFEST.json` |
| `re:\b[0-9a-f]{7}\b` | a commit hash | — |
| `re:claude-opus-5\[1m\]` | the model every live run named | `eval/results/published/MANIFEST.json` |
| `re:\bclaude-opus-5\b` | the same model without its context suffix | `eval/results/published/MANIFEST.json` |
| `re:\bSS1/23\b` | a UK PRA supervisory statement ValidMind names | `notes/prior-art.md` |
| `re:\bE-23\b` | an OSFI guideline ValidMind names | `notes/prior-art.md` |
| `re:\bAGPL-3\.0\b` | a licence name | `notes/prior-art.md` |
| `re:\bAGPLv3\b` | the same licence, as deepchecks spells it | `notes/prior-art.md` |
| `re:\bApache-2\.0\b` | a licence name | `notes/prior-art.md` |
| `re:\bBM25\b` | the retrieval algorithm's name | `docs/DESIGN.md` |
| `re:\bSOC 2 Type 2\b` | an audit standard's name | `notes/prior-art.md` |
| `re:\b0\.19\.1\b` | deepchecks' last released version | `notes/prior-art.md` |
| `re:\b3\.1[12]\b` | the supported Python versions | `pyproject.toml` |
| `re:\b0\.1\.0\b` | the version this release carries | `src/quaestor/__init__.py` |
| `re:https?://\S+` | a URL: an address, not a measurement | — |
| `re:\b[a-z]+__[A-Za-z0-9_]+\b` | a variant directory name, which carries its class code | `eval/variants` |
| `re:\b[LRCSMDTOEX][0-9]\b` | a defect class code | `src/quaestor/findings.py` |
| `re:threshold\.O1\.\S+` | an artifact's logical name | `src/quaestor/configs.py` |
| `re:metrics\.\S+` | an artifact's logical name | `src/quaestor/tools` |
| `re:\b46 \+ 46 \+ 1\b` | the arithmetic of D-198's miscount, shown as arithmetic | `DECISIONS.md` D-198 |
| `re:\b0/\d\d\b` | a false-verified count printed as a fraction; both halves have rows above | `eval/results/verifier-eval/verifier_eval.json` |
| `re:\b\d+ of \d+\b` | a detection count printed in prose; both halves have rows above | `eval/results/published/summary.json` |
| `re:\b38/40\b` | the judge agreement printed as a fraction; both halves have rows above | `docs/EVALUATION.md` |
| `re:\b\d+ pass / \d+ fail\b` | the label distribution; both halves have rows above | `docs/EVALUATION.md` |
| `re:\b7 failed[ ,/]+33 passed\b` | the Probatio replay status; both halves have rows above | `PROGRESS.md` |

## Which test guards which document

Every document that prints a measurement has a test that re-derives it from the file named beside
it. This table is what stops a document from being added without one.

| document | provenance test |
|---|---|
| `README.md` | `tests/test_docs_provenance.py` |
| `docs/PROVENANCE.md` | `tests/test_docs_provenance.py` |
| `docs/STUDY.md` | `tests/test_docs_provenance.py` |
| `docs/anchor/COMPARISON.md` | `tests/test_docs_provenance.py` |
| `docs/EVALUATION.md` | `tests/test_archive_fixtures.py` |

`docs/EVALUATION.md` is the one document whose figures are guarded by re-derivation rather than by
an index. Its section 1 entries are re-computed from the traces they name by
`tests/test_live_credit_attempt1.py` through `attempt5`, `tests/test_live_credit.py`,
`tests/test_live_msr.py` and `tests/test_archive_fixtures.py`, which read the committed runs and
fail when a figure in the prose drifts from the run it claims. That is a stronger check than a
table row, and it is why the file is not swept numeral by numeral: an index of 667 distinct
numerals would be a worse guarantee than six modules that recompute them.

## Documents that are not swept, and why

Naming these is the point. A document that is not swept and does not say so is a hole.

| document | why it is not swept |
|---|---|
| `CHANGELOG.md` | It is history. Every figure in it was checked by the gate of the phase that introduced it and is quoted from that phase's run log entry; re-indexing 405 distinct numerals from twelve shipped phases would restate `PROGRESS.md` rather than check anything. The `0.1.0` release section **is** swept, by `test_every_numeral_in_the_release_section_is_accounted_for_too`, because it restates the headline result; only the historical entries beneath it are exempt. |
| `docs/DESIGN.md` | It argues about choices and quotes figures the documents above already carry. It states no measurement that originates in it. |
| `docs/CHECKLIST.md` | It maps practices to checks and defect classes. Its only numerals are class codes, section references and one practice description ("28 to 12 features") which is the author's own professional history, not a computed result — there is no artifact behind it and the file says so. |
| `docs/REPORT_SCHEMA.md` | It is a schema. Its numerals are field constraints and example values, guarded by `tests/test_report_schema.py` against the schema the renderer enforces. |
| `docs/anchor/manual_credit_default.md` | It is the human's own validation, written before the copilot's report was opened and committed unedited at `225d902`. Its figures are the human's readings of the same artifacts; `docs/anchor/COMPARISON.md` is where they are set against the copilot's and checked. Editing it to match a later scoring would destroy what it is for. |

## What this file does not cover

- **Claims about third-party documentation.** `notes/prior-art.md` records what ValidMind's and
  deepchecks' pages said on 2026-09-20, with URLs. No test here can make a claim about another
  organisation's website true, and none tries; what is tested is that the note exists, carries the
  date, and gives a URL for every claim heading.
- **The two figures that are observations rather than artifacts.** `7 failed / 33 passed` and the
  grounding judge's "about one reply in ten" are the operator's readings of a run, recorded in
  `PROGRESS.md` and `docs/EVALUATION.md` at the time. They are sourced to those documents, not to a
  JSON file, and the rows above say so.
- **Anything a live run would have to produce.** No test in this repository calls a model,
  downloads data, or re-runs R1, R2 or R3. The rule is that a number must come from a *committed*
  run; checking it must not require making a new one.
