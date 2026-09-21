# `data/` — what a human downloads, and what this repository keeps

Nothing under `data/` is a dataset. The repository holds **no rows of anybody's data**: real data
is read from a path passed on the command line and is never committed (`CLAUDE.md`). What lives
here is the small amount of *reference* material the pipeline is built against.

## `data/regulatory/` — the section outlines

| file | what it is |
|---|---|
| `sr11-7-outline.yaml` | the section outline of SR 11-7 (2011-04-04), **superseded 2026-04-17** |
| `sr26-2-outline.yaml` | the section outline of SR 26-2 (2026-04-17), the current guidance |

Each file names the document, its issue date, its public URL and its sections, in document order,
with the `section_id` values a `[[reg:DOC:SECTION]]` citation uses. An outline is a **claim about
a document**: `quaestor.corpus.ingest` matches every heading it names against the PDF's own text
and fails, naming the heading, when one is not there. If a heading in an outline does not match
the document, the outline is corrected to the document — never the other way round
(DECISIONS D-056).

## The two PDFs, which are not committed

The ingest reads two attachments the human downloads. They are public U.S. government documents;
they are left out of the repository because the *text* is what Quaestor needs and the text is
committed, already split, under `src/quaestor/corpus/`.

| document | URL |
|---|---|
| SR 11-7 attachment | <https://www.federalreserve.gov/boarddocs/srletters/2011/sr1107a1.pdf> |
| SR 26-2 attachment | <https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf> |

SR 26-2 is interagency: the OCC issued the identical text as Bulletin 2026-13, which rescinds OCC
Bulletin 2011-12. **OCC 2011-12 is deliberately not ingested** (DECISIONS D-055).

Download both, then run the ingest once:

```bash
python -m quaestor.corpus.ingest --sr117 ~/sr1107a1.pdf --sr262 ~/sr2602a1.pdf
```

It writes `src/quaestor/corpus/sr11-7.jsonl`, `src/quaestor/corpus/sr26-2.jsonl` and
`src/quaestor/corpus/SOURCES.json`, and those three files are what gets committed. `SOURCES.json`
records each PDF's `sha256`, its page count, the outline's `sha256` and the ingest date, so the
committed text can be traced to the bytes it came from. The script is dev-time only: `pypdf` is a
development dependency, no test reads a PDF, and a validation run never opens one.

## Model data

Neither subject's data is here either. `subjects/credit_default/sample.py` builds its sample from
the UCI *Default of Credit Card Clients* dataset and `subjects/msr_prepayment/sample_freddie.py`
from Freddie Mac's single-family files; both take a path to data the human downloaded, and both
have a `--synthetic` mode that generates a small panel from a known process, which is what the
tests, CI and the demo use. See each subject's `README.md` for the source, the licence and the
sample rule.

## The two question-answering datasets, which are not committed either

The verifier component eval of `04-SEEDED-DEFECT-STUDY.md` section 6 runs on two public financial
question-answering sets. Neither is committed, no test reads either, and `quaestor verifier-eval`
takes both as paths on the command line and refuses to run without them.

| dataset | file | licence | source |
|---|---|---|---|
| FinQA | `dev.json` | MIT | <https://github.com/czyssrs/FinQA> |
| TAT-QA | `tatqa_dataset_dev.json` | CC BY 4.0 | <https://github.com/NExTplusplus/TAT-QA> |

Download both, then run the component eval once:

```bash
quaestor verifier-eval --finqa ~/finqa/dev.json --tatqa ~/tatqa/tatqa_dataset_dev.json \
  --out eval/results/verifier --llm claude-cli --model MODEL --record-cassettes DIR
```

The command samples 50 arithmetic-answer items from each dataset with the study's seed (D-194),
and writes `verifier_eval.json`. What is committed from a run is the summary, the trace and the
cassettes — never a row of either dataset. The ten items under `tests/fixtures/verifier_eval/`,
which the offline tests use, were written for this repository and quote neither dataset.
