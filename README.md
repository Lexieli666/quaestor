# Quaestor

SR 11-7-shaped, not a compliance product, no bank data.

Quaestor is an agentic model-validation copilot: it takes a model package — the subject's code, a
reference to its data, its fitted artifacts and the developer's own claims — runs a fixed set of
deterministic checks over it in a capped subprocess, and drafts a validation report shaped after
the sections of SR 11-7, in which every quantitative claim carries a machine-checked citation to a
computed artifact, every finding is a structured object that cannot be constructed without evidence
artifacts, and the report prints its own grounding precision before and after repair. What makes it
worth reading rather than another wrapper is the open evaluation: defects are seeded into the
author's own rebuilt models, and detection precision and recall, the false-alarm rate and
per-report grounding precision are published, misses included.

## Quick start

Offline, with no API key, no network and no data to download: both shipped subjects generate a
small panel from a known process, and `--llm fake` is a deterministic offline provider that ships
with the package.

```bash
pip install -e .
quaestor validate subjects/credit_default --synthetic --llm fake --out /tmp/quaestor-demo
head -20 /tmp/quaestor-demo/report.md
```

That writes `report.md`, `claims.json`, `findings.json`, `trace.jsonl` and the content-addressed
artifact store under `--out`. The report's front matter carries its grounding precision before and
after repair; Appendix A lists every numeric claim with its citation, its status and the artifact
value it was checked against; Appendix B is the artifact index every citation resolves into.

`quaestor validate --help` names the rest: `--data DIR` instead of `--synthetic` for a real
sample, `--llm anthropic` or `--llm claude-cli` for a live run, `--config rules_only|plain_llm` for
the two comparison arms of the study, and `--record-cassettes DIR` to keep every model call a live
run made so it can be replayed with `--llm replay`. `quaestor tool NAME --pkg PKG --run-dir DIR`
runs one check on its own.

No number from a run is quoted in this file yet: the study that produces them is Phase 12, and
`PROGRESS.md` is the build order.
