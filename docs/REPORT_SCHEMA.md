# REPORT_SCHEMA.md — report structure, claim grammar and citation syntax

The prose form of the three schemas in `examples/golden_report/`. Every field below is either fixed
by `02-SPEC.md` §3.9–3.11 or is an addition this project made in Phase 1; the additions are
collected in §10 with the `DECISIONS.md` entry that records each. Precedence: `CLAUDE.md`, then
`02-SPEC.md`, then this file.

The machine-readable forms are `examples/golden_report/REPORT_SCHEMA.json` (front matter and the
`x-quaestor-*` structural rules), `CLAIMS_SCHEMA.json` (`Claim`, `VerifiedClaim`, the `claims.json`
envelope) and `FINDINGS_SCHEMA.json` (`Finding`, the `findings.json` envelope). Where this document
and a schema disagree, the schema is what runs: `tests/test_golden_spec.py` validates the golden
files against all three.

## 1. What a report is

`report.md` = YAML front matter + a fixed sequence of level-2 sections (seven drafted, four
appendices rendered). The drafter (LLM) writes the prose of sections 1–7, one `structured()` call
per section. The renderer writes the front matter, the *renderer blocks* inside sections, and the
four appendices from `claims.json`, `findings.json`, the artifact index and `trace.jsonl`. Claim
extraction and verification run over the drafted prose only.

Under `rules_only` the "drafter" is a template; under `plain_llm` one call writes all seven sections
and the same renderer wraps them. The schema is identical across configurations.

## 2. Front matter (validated by `REPORT_SCHEMA.json`)

| key | type | source | spec |
|---|---|---|---|
| `schema_version` | const 1 | renderer | addition: every persisted file carries one, as `trace.jsonl` does |
| `quaestor_version` | string | `quaestor.__version__` | addition: provenance |
| `package`, `version` | string | `package.yaml` `name`, `version` | §3.11 |
| `model_type` | enum | `package.yaml` | addition: lets a reader know why §5 has or lacks scenarios |
| `configuration` | enum | CLI | §3.11 |
| `model` | string | the model id off the completions the run received (`claude-opus-5[1m]`, `fake-1`); the adapter's `name` where nothing answered; `illustrative` in the golden | §3.11, narrowed by D-093 |
| `run_id` | string | trace | addition: joins the report to `trace.jsonl` |
| `data_mode`, `synthetic_n` | enum, int | CLI | addition: the report must say when it ran on synthetic data |
| `grounding_precision_pre`, `_post` | number in [0,1] | verifier | §3.11 |
| `n_claims` | int | verifier | addition: the denominator, so the two precisions are interpretable |
| `n_findings_by_severity` | object high/medium/low/info | findings | §3.11 |
| `generated` | date-time | renderer | §3.11; the only timestamp outside the trace |
| `illustrative` | bool | `true` only in `examples/golden_report/` | §7 |

## 3. Sections and headings

Exactly the eleven level-2 headings in `REPORT_SCHEMA.json` `x-quaestor-required-headings`, in
that order, none other. Each drafted section opens with a sentence that anchors it to the guidance
with a `[[reg:...]]` citation (anchors from `data/regulatory/sr11-7-outline.yaml`). Findings are
level-3 headings under section 6: `### F-NNN · <class> <name> · severity **<severity>**`.

Section 6 also carries `### Open items`, always, findings or none (D-096). Under it go the
observations this validation made that are **not** defects under any rule but that need a
developer response, each citing the artifact it rests on and each naming an owner (`model
developer` by default). The drafter is asked for it and the renderer supplies the heading when the
drafter omits it, on the same argument as a finding's heading (D-071); `check_structure` refuses a
report whose section 6 has no such heading, so "no findings" cannot quietly mean "no questions".

Section 4 orders itself by two rules, in this order, and **says in the report which one applied**
(D-098):

1. `package.yaml` declares `use: probability` or `use: both` — calibration before discrimination,
   whatever the event rate is, because the level of the probability is what the model is used for.
   `rule.calibration_first_event_rate` is not cited for it, and is not even offered to the drafter
   of that section.
2. otherwise the rare-event rule of §3.11 decides: calibration first when the observed event rate
   on the evaluation split is below `rule.calibration_first_event_rate`, discrimination first
   otherwise. Either way the report cites the event rate and the rule, because either way the rule
   is what decided it.

Section identifiers used in `claims.json` and `findings.json` (`section` field):
`summary`, `conceptual_soundness`, `data_integrity`, `outcomes`, `sensitivity`, `findings`,
`monitoring`.

## 4. Renderer blocks

```
<!-- quaestor:renderer:begin scope -->      one, required, first thing under section 1
<!-- quaestor:renderer:begin table <logical_name> -->   zero or more, where the drafter placed a directive
... markdown ...
<!-- quaestor:renderer:end -->
```

The drafter never writes numbers it would have to retype from a table artifact. It writes the
directive `[[table:<logical_name>]]` on its own line; the renderer replaces it with the artifact's
caption (the artifact `summary`), the table's own citation, and the rows, inside a renderer block.
Everything inside a renderer block is excluded from claim extraction and from the grounding
denominator: no LLM produced it, so there is nothing to verify. The scope block is how the two
grounding figures reach "the report's first page" (§3.10) without the drafter having to state a
number that does not exist until after extraction.

Why not let the drafter write the table: 80 of the golden report's numbers would be table cells,
the grounding precision would measure the LLM's transcription of ten-row tables rather than its
prose, and a real drafter would make transcription errors that a renderer cannot. The rejected
alternative is recorded in `docs/DESIGN.md`, Phase 1.

Tables the drafter *does* write (the metrics-by-split table, the threshold table) are prose in
table layout: every cell carries its own inline citation and is an ordinary claim.

## 5. Citation syntax

| form | resolves when | example |
|---|---|---|
| `[[art:<hash8>:<logical_name>]]` | `hash8` prefixes a stored artifact and `logical_name` is in its index entry; the artifact is a scalar | `[[art:4bb1344e:metrics.test.auc]]` |
| `[[art:<hash8>:<logical_name>#<row_key>.<column>]]` | as above and the artifact is a table with a row whose first-column value is `row_key`, or a JSON artifact with that dotted path (list elements addressed by their `feature` value, or by their `name` when they carry no `feature`: DECISIONS D-026) | `[[art:20368492:deciles.test#1.lift]]`, `[[art:843f4548:run.model_summary#coefficients.utilisation.value]]` |
| `[[art:…]][[art:…]]` (two, adjacent) | both resolve; only valid on a claim with `comparison` `delta` or `ratio` | `0.0126 [[art:…:metrics.test.auc]][[art:…:metrics.train.auc]]` |
| `[[reg:<doc>:<section_id>]]` | `section_id` exists in the corpus JSONL for `doc` ∈ {SR11-7, SR26-2} — the superseded 2011 guidance, kept so historical citations resolve, and the current 2026 revision the drafter cites by default (DECISIONS D-055) | `[[reg:SR26-2:V.1.b]]`, `[[reg:SR11-7:V.1.c]]` |
| `[[table:<logical_name>]]` | drafter output only; the renderer expands it or, if the name is not a table artifact, leaves a `⟦unverified: table <name>⟧` marker | |

Logical names: lowercase-initial dotted segments; class codes keep their case
(`threshold.E1.delta_auc`). Every threshold a check uses is stored under `threshold.<package|class>.…`
so the prose can cite the rule it applied (§3.7). Report-level constants the renderer or planner
applies (the 5% calibration-first rule) are stored under `rule.*` for the same reason.

The renderer turns every citation into a footnote link to Appendix B. Raw `report.md` keeps the
citations inline so that `claims.json` and the report are checkable with `grep`.

## 6. `Claim` (pydantic; §3.10) and `VerifiedClaim`

| field | type | meaning |
|---|---|---|
| `text` | str | the sentence (or table row) as drafted, citations included |
| `value` | float | the number as written, after removing thousands separators and the `%` sign; `22.0%` → `22.0` with `unit: percent` |
| `unit` | `ratio` \| `percent` \| `count` \| `currency` \| `bp` \| `months` | how to normalise before matching; `ratio` covers every dimensionless quantity that is not written with `%` (AUC, PSI, VIF, coefficients) |
| `metric` | str \| null | what the number measures, from the artifact's logical name when cited (`auc`, `psi`, `vif`, `calibration_slope`, `delta_auc`, `coefficient`, …); null for bare counts |
| `split` | str \| null | `train`, `test`, `out_of_time`, `vintage_holdout`, or null |
| `comparison` | `eq` \| `delta` \| `ratio` | `eq`: value ≈ artifact. `delta`: value ≈ second − first. `ratio`: value ≈ second ÷ first. The two artifacts are the two adjacent citations, in order |
| `citation` | str \| null | the citation text carried by the number: one `[[art:…]]`, or two adjacent for `delta`/`ratio`; null when the sentence has none |
| `rounding` | int \| null | an explicit precision override, in decimals; the matcher narrows the tolerance to `0.5·10^-rounding` and can never widen past the applied tolerance below. Spec §0: "a claim may declare its own rounding" |
| `section` | enum (§3) | where the sentence lives |
| `id` | str | `stable_hash([section, text, value])`, so the repair loop and the trace can name a claim |
| `source` | `report` \| `developer` | report prose, or a `claims:` entry from `package.yaml` |

`VerifiedClaim` = `Claim` + the matcher's verdict:

| field | type | meaning |
|---|---|---|
| `status` | `verified` \| `mismatch` \| `unsupported` \| `dangling` \| `unattributed` | §3.10 |
| `artifact_value` | float \| null | the resolved scalar (or computed delta/ratio); null unless the citation resolved |
| `tolerance` | float | the absolute tolerance actually applied, so a reader can see why a 0.74 verified against 0.7412 |

**Tolerance (§0, made precise; DECISIONS D-069 amends D-014).** A claim verifies when the
artifact value rounds to the value as written, at the precision the prose used: `0.74` verifies
against `0.7412`, `0.021` does not verify against `0.0175`, and `22.0%` does not verify against
`0.2212`. The applied tolerance is therefore

```
tolerance = min(0.5 · 10^-decimals_written · scale,          the precision the prose chose
                default_for_unit,                            spec §0, the ceiling
                0.5 · 10^-rounding · scale)                   the explicit override, if declared
```

where `decimals_written` is read from the claim's own sentence — the first numeric token in `text`
whose value is `value`, so `22.0%` declares one decimal and `22%` declares none though both parse
to the same float — and `scale` is the factor that carries a tolerance stated in the units the
prose wrote into the units the artifact is held in (`0.01` for a `percent` against a unit-interval
artifact, `0.0001` for `bp` against a rate, `1` otherwise). When the sentence holds no matching
token, the float's own shortest decimal form is used instead.

`default_for_unit` is D-014's mapping, unchanged, and is now a **ceiling** rather than the
tolerance itself: `count` → 0.5 (integers match exactly, and a count stays exact however it was
written; stricter than the spec's 1% default, because "3,500 rows" is either right or wrong);
`ratio`/`percent` with |artifact| ≤ 1 → abs 0.005 after percent→ratio normalisation; `percent` on a
0–100 scale → abs 0.5; everything else → rel 1%. `rounding` can only narrow, never widen.

The golden report's 92 post-repair claims all still verify under this rule and its pre-repair
`0.0136` still mismatches; 60 of the 92 record a narrower `tolerance` than the Phase 1 file does.

## 7. `claims.json`

```
schema_version: 1
package, version, configuration, run_id, illustrative
tolerances:        the defaults applied
grounding:         {pre_repair: G, post_repair: G}   G = {precision, n_claims, status_counts, per_section}
repairs:           [{section, claim_id, before: {value, status}, after: {value, status}, instruction}]
pre_repair:        [VerifiedClaim]   every claim as first extracted and matched
post_repair:       [VerifiedClaim]   every claim after the last repair round (Appendix A renders this)
developer_claims:  [VerifiedClaim with source: developer]   status may also be not_evaluated (below)
exclusions:        [{pattern, examples}]   the numeric tokens the pre-pass deliberately ignored
```

`eval/score.py` reads `grounding` and never the prose. Both lists are kept so that the pre-repair
figure is recomputable, not remembered.

**Excluded numeric tokens** (the allow-list, §3.10), each listed with examples in the report:
section and finding numbering (`1.`, `§6`, `F-001`); regulatory section ids; the eight hex
characters of a citation; the package version string from the front matter; anything inside
inline code (`` `bill_mean_6m` ``); renderer blocks. Inline code is a loophole a drafter could
abuse; the count of excluded tokens is printed, and the Probatio grounding judge (Phase 11) is
told that a number hidden in backticks is a failure.

**Developer claims in synthetic mode.** `package.yaml` `claims:` describe the real fit. Under
`--synthetic` they are not evaluated (a synthetic AUC has nothing to do with the declared one)
and appear in Appendix D; under `--data` each becomes a `VerifiedClaim` with `source: developer`,
and a `mismatch` is the claim channel of a T1 finding. Two-line rule, one `DESIGN.md` paragraph, no
schema branch.

## 8. `Finding` (§3.9) and `findings.json`

| field | type | meaning |
|---|---|---|
| `id` | `F-NNN` | severity-ordered numbering at render time |
| `defect_class` | `DefectClass` | one of the twelve codes |
| `severity` | `high` \| `medium` \| `low` \| `info` | the severity the agent set |
| `suggested_severity` | same enum | what the check suggested; equal to `severity` unless the agent changed it |
| `severity_reason` | str \| null | the one-sentence reason, required when the two differ; also a trace event |
| `tool` | str | the tool whose candidate(s) became this finding |
| `title`, `narrative` | str | drafted; every number in them is also a claim in section 6 |
| `evidence` | list[str], non-empty | artifact hashes; `Finding` construction fails if any is not in the store |
| `section` | enum | the section whose material the finding rests on |
| `candidates_merged` | int ≥ 1 | how many candidates of the class were merged |

`findings.json`: `schema_version, package, version, configuration, run_id, illustrative,
findings: [Finding], candidates_not_promoted: [{defect_class, tool, evidence, reason}],
checks_without_candidates: {tool: [classes]}`. The last two exist so that the study's miss list can
say what the report did instead of raising the seeded class, from structured data rather than prose.

## 9. What the golden report deliberately shows

One finding, `E1` at low severity, on a clean subject: the synthetic generating process is a
logistic model with one interaction term (`utilisation × delinq_last`) the additive champion cannot
represent, so a boosted challenger legitimately wins by more than 0.03. This keeps the golden
faithful to a clean package while pinning the `Finding` shape. One repair round with one
`mismatch` (a delta written wrong) and one `unsupported` (a count written without its citation),
so `repairs`, `pre_repair` and the two grounding figures are all non-trivial. One planner follow-up
(metrics on `limit_bal` halves) so the bounded loop's output has a shape. Appendix D lists what a
classifier without a regime column cannot be checked for.

## 10. Additions to `02-SPEC.md` §3.9–3.11

Everything this document adds to the spec, and where the decision is recorded. Nothing below
contradicts the spec; each row either names a field the spec's prose implies without listing, or
makes a spec tolerance precise enough to implement.

| addition | where | why | decision |
|---|---|---|---|
| `schema_version`, `quaestor_version`, `model_type`, `run_id`, `data_mode`, `synthetic_n`, `n_claims` in the front matter | §2 | a persisted file carries its schema version; the report must be joinable to its trace and must say when it ran on synthetic data; `n_claims` is the denominator of the two printed precisions | D-012 |
| `Claim.rounding` | §6 | spec §0 says "a claim may declare its own rounding" but gives the field no home | D-012 |
| `Claim.id` | §6 | the repair loop, the trace and `repairs` all have to name one claim | D-012 |
| `Claim.source` | §6 | report prose and `package.yaml` `claims:` share one grammar and must stay distinguishable | D-012 |
| `VerifiedClaim.status`, `.artifact_value`, `.tolerance` | §6 | spec §3.10 names the five statuses and says the artifact value is recorded, without naming the object that carries them | D-012 |
| two adjacent `[[art:…]]` tokens on a `delta` or `ratio` claim | §5 | spec §3.10 defines the comparison kinds but not how a sentence cites both operands | D-012 |
| `claims.json` keeps both `pre_repair` and `post_repair` | §7 | the pre-repair precision must be recomputable rather than remembered | D-012 |
| `findings.json` carries `candidates_not_promoted` and `checks_without_candidates` | §8 | the study's miss list has to be readable from structured data, not from prose | D-012 |
| `Finding.suggested_severity`, `.severity_reason`, `.tool`, `.candidates_merged` | §8 | spec §3.9 permits the agent to re-severitise and to merge candidates; the record of what it did needs fields | D-012 |
| renderer blocks and the `[[table:…]]` directive; table cells and the scope block excluded from extraction | §4 | grounding precision must measure the drafter's prose, not its transcription of ten-row tables | D-013 |
| tolerances made precise per unit | §6 | spec §0 gives three defaults and leaves the mapping from `unit` to default unstated | D-014 |
| tolerance is the precision the prose used, with §0's default as a ceiling and `rounding` narrowing only | §6 | a flat 0.005 verifies `0.021` against `0.0175` and `22.0%` against `0.2212`, which is not what either sentence claims | D-069 (amends D-014) |
| the exclusion list, its appearance in `claims.json` and its count in Appendix A | §7 | spec §3.10 requires the exclusions to be auditable; inline code is the loophole that needs naming | D-015 |
| developer claims not evaluated under `--synthetic`, listed in Appendix D | §7 | a synthetic AUC cannot verify a declared real one, and a schema branch would be worse than a status | D-016 |
| `package.yaml` `use: ranking \| probability \| both`, optional and nullable | §3 | spec §3.11 orders section 4 by the event rate alone, which asks the data what the model is for; a servicing model whose probabilities are multiplied by a balance is judged on calibration at any event rate | D-098 |
| `### Open items` under section 6, required | §3 | a validation that raised no finding still made observations a developer must answer for, and without somewhere to put them "no findings" reads as "no questions" | D-096 |
| the front matter's `model` is the model id, and Appendix C carries the adapter beside it | §2 | `claude-cli` is the adapter and not the model; a report that records only the adapter cannot say which model wrote it | D-093 |
| `run_id` carries the UTC second the run began | §2 | two runs of one package and configuration shared an identifier, which is a joining key that does not join | D-093 |
| the `thresholds.evaluation` table artifact, written by `compute_metrics` and placed by a `[[table:…]]` directive | §4 | section 4's developer-threshold table was assembled by the drafter from loose scalars and disagreed with the rest of the report about what had been recomputed | D-092 |
| a rule that derives its bound stores it as `<declared>.<rule>_effective` | §5 | a report that compares a value against a bound no artifact holds is a comparison nothing can check, and the drafter cited the declared bound instead | D-091 |
| renderer tables print measures at four significant figures and integral cells as integers | §4 | the drafter is shown four figures and writes them; a renderer block printing ten digits of the same number shows the reader two spellings of it | D-094 |
| Appendix A's repair sentence counts claims rewritten and numbers removed separately | §7 | only rewrites become `repairs` rows, so a loop that removed three numbers and rewrote none printed "after 0 repaired claim(s)" | D-097 |

