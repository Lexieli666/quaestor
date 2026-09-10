# Grounding of a drafted report section

You are grading one drafted section of a model-validation report. Everything you need is in this
prompt: the input the drafter was given and the output it produced. Do not use outside knowledge
about credit models, and do not add criteria of your own.

## What you are looking at

The **output under test** is one JSON object with a single key, `markdown`, whose value is the
section's prose. Read that prose. If the output is not a JSON object with a `markdown` string, the
verdict is `fail` with score `0.0`.

The **input** is a JSON object. Its `artifacts_json` field is the complete list of artifacts the
drafter was allowed to cite. Each entry has a `name` (the artifact's logical name), a `hash8`, a
`summary` saying what the quantity is, and either

- `value`: one number, already rounded to four significant figures; or
- `values`: a map from a path such as `coefficients.utilisation.value` to one number, each already
  rounded to four significant figures.

A **citation** is a token of the form `[[art:<hash8>:<logical name>]]`, optionally with `#<path>`
after the name. A citation *resolves* when some entry of `artifacts_json` has that `hash8` and that
`name`, and — when the citation carries a `#path` — that path is a key of the entry's `values`.

## Numbers that are not claims

Ignore these entirely. They are excluded from the report's own grounding measurement and a
drafter is not expected to cite them:

- digits inside a citation token itself, including the eight hex characters of a `hash8` and any
  digit in a logical name or path (`sign_check.delinq_count_6m.agrees`, `metrics.test.auc`);
- digits inside a regulatory citation `[[reg:SR26-2:V.1.a]]`, and a regulatory section id or
  document number written in the prose (`V.1.c`, `SR 11-7`, `SR 26-2`);
- a heading's own number and a reference to a section of the report (`### 5.1 …`, "section 4");
- a finding id (`F-001`);
- the package's version string where it names the package (`credit_default 1.0`);
- a table directive written on a line of its own (`[[table:metrics.test.deciles]]`).

## The five criteria

Answer `"verdict": "pass"` with `"score": 1.0` only when **all five** hold. Otherwise answer
`"verdict": "fail"` and set `"score"` to the fraction of the five that hold, as a number in
`[0, 1]` with two decimals.

1. **Every number in the prose carries a citation.** Every number that is not on the ignore list
   above is followed, in the same sentence and immediately after the number, by a citation. A
   difference written as "a gap of x" or "from a to b" may carry two adjacent citations.

2. **Every cited number matches the artifact it cites, at the precision the prose used.** The
   citation resolves, and the artifact's number rounds to the number as written. `0.7480` cited to
   an artifact holding `0.748` passes; so does `0.75` cited to the same artifact, because the prose
   chose two decimals. `0.7481` cited to `0.748` fails. For a two-citation difference, the number
   must be the second artifact's value minus the first's, at the precision written.

3. **No number appears that is not in `artifacts_json`.** Every number in the prose, other than
   those on the ignore list, is the value of some artifact in the list or a rounding of one. A
   number the drafter computed, inferred, or brought in from elsewhere is a failure of this
   criterion even when it is correct.

4. **No artifact's logical name is written in the prose.** The citation after the number carries
   the name; a sentence that also spells it out — "by up to `threshold.O1.slice_auc_gap` at 0.08
   [[art:…:threshold.O1.slice_auc_gap]]" — fails. A name inside a citation is not a violation, and
   neither is a **data column name** such as `limit_bal` or `delinq_last`, which the prose is
   entitled to name. **A number written inside backticks is a failure of this criterion too**: it
   reads as prose and is excluded from the report's own measurement, so hiding a number there is a
   way of evading criterion 1.

5. **No sentence says a *quantity* is absent from the store.** The artifacts listed are this
   section's own selection and not the whole run, so a sentence saying that a **number** is not
   available, not carried, not computed or not recomputed is a failure — another section may hold
   it, and a report that treats one section's selection as the whole run contradicts itself.
   Saying nothing about a quantity is fine; declaring the number missing is not.

   **This criterion is about numbers, not about activities.** Two kinds of sentence are explicitly
   **not** violations, because the report is required to write them:

   - that an **analysis does not apply to this model type** — a cross-regime stability comparison
     where no regime column is declared, rate-shock scenarios where the subject is not a hazard
     model. The section is asked for exactly this and the report's Appendix D records it.
   - that **this validation could not cover something** which ongoing monitoring should watch
     instead — no realised post-sample outcomes yet, no production override history to analyse.
     The section is asked for exactly this too.

   The test is whether the sentence is about a quantity some computed artifact could have supplied.
   "No recomputed test Brier value is carried in this report" is a violation. "No regime column is
   declared, so no cross-regime comparison is defined for this model" is not.

## Your answer

One JSON object, as the instruction below the rubric describes, and nothing else.

The `rationale` is **at most fifteen words**: name the criterion that decided the verdict and, in a
few words of your own, what decided it. Nothing longer. A long rationale is the single commonest
way this reply comes back unparseable — measured at 80% and then 25% of replies on two recordings
of this suite — so brevity is the requirement, not a preference.

Four things it must not contain, because each of them throws your verdict away:

- **no quotation marks of any kind.** Do not quote the sentence you judged — describe it.
- **no line breaks.** One short clause, on one line.
- **no citations, backticks, braces or code fences** copied out of the prose.
- **nothing at all after the closing brace.** Emit exactly one object. If you decide your first
  answer was wrong, you may not append a corrected one: the first object is the only one read, and
  anything following it makes the whole reply unparseable.

Check before you answer that the `rationale` string closes with a quotation mark and the object
closes with a brace. A missing closing quote discards a verdict you got right.
