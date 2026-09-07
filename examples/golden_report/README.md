# `examples/golden_report/` — the executable design specification

This directory is the shape of a Quaestor validation report, written in Phase 1 **before any
`src/quaestor/` code existed** (`02-SPEC.md` §7). It fixes the report's structure, the claim
grammar and the citation syntax so that the renderer, the verifier and the findings model are built
against a target rather than towards one. `tests/test_golden_spec.py` is the assertion that the
target still holds.

| file | what it is |
|---|---|
| `report.md` | the golden report: YAML front matter, seven drafted sections, four appendices, an `[[art:...]]` citation on every number |
| `claims.json` | the verifier's output: pre- and post-repair `VerifiedClaim` lists, the two grounding figures, the repair records, the exclusion list |
| `findings.json` | one `E1` finding, the candidates that were not promoted, and the checks that raised nothing |
| `REPORT_SCHEMA.json` | JSON Schema 2020-12 over the front matter, plus the `x-quaestor-*` structural rules (required headings in order, renderer blocks, citation patterns, forbidden patterns) that JSON Schema cannot express over Markdown |
| `CLAIMS_SCHEMA.json` | JSON Schema 2020-12 over `claims.json`: `Claim`, `VerifiedClaim`, the envelope |
| `FINDINGS_SCHEMA.json` | JSON Schema 2020-12 over `findings.json`: `Finding`, the envelope |
| `MANIFEST.json` | `sha256` of each of the six files above; the pin that makes a silent edit impossible |

## Every number here is illustrative

The front matter says `illustrative: true`, and it is the only report in this repository that ever
will. Every value in `report.md` was chosen by hand to be internally consistent — the Gini equals
2·AUC − 1, the deciles sum to the event count, the delta equals the difference of the two metrics it
cites — and **not one of them was produced by running anything**. Every artifact hash is
`sha256(logical_name)[:8]`, so every citation in this report resolves to nothing at all.

This directory is therefore never quoted as a result. `README.md`, `docs/` and
`docs/PROVENANCE.md` take their numbers from committed runs under `eval/results/`; if a number in
this repository has no run behind it, it is a defect. What the golden report *is* quoted for is
shape: a reader who wants to know what Quaestor emits reads `report.md`, and a session that is
about to write the renderer reads `REPORT_SCHEMA.json`.

## The directory is frozen

`CLAUDE.md`'s quality gate, condition 5: these files are byte-identical to the commit that
introduced them, except for edits `DECISIONS.md` sanctions. The freeze is what makes the
specification executable — a schema that drifts to match its implementation is a description, not a
specification.

**A sanctioned edit is made in this order, and the order is the whole point:**

1. Make the edit locally and compute the new `MANIFEST.json` (the six file hashes, then the
   `sha256` of `MANIFEST.json` itself).
2. **First** commit the `DECISIONS.md` entry: a numbered `Q / A / Why` that says what changes and
   why, with a new row in the D-011 table giving the date, the new `MANIFEST.json` `sha256` and the
   reason.
3. **Then** commit the files, so that the pin in `DECISIONS.md` is what the new bytes have to
   satisfy.

`tests/test_golden_spec.py` compares the six files against `MANIFEST.json` and `MANIFEST.json`
against the hash pinned in D-011, so an edit made in the other order — files first, decision
afterwards — leaves the suite red in between and cannot pass unnoticed. The test fails, and does
not skip, when the D-011 pin is missing.

## `make_golden.py` is not here

The generator that produced `report.md`, `claims.json` and `findings.json` from a single table of
values lives in the Cowork package folder (`phase1-draft/make_golden.py`), outside this repository,
together with the `check_golden.py` whose nine checks became `tests/test_golden_spec.py`. It is not
committed here on purpose: a generator inside a frozen directory invites regeneration, and
regeneration is exactly what the freeze forbids without a `DECISIONS.md` entry. When a sanctioned
edit is large enough to want the generator, it is run in the package folder and its output copied
in, which is how these files arrived in the first place.
