"""The archived live runs as offline regression fixtures.

Six live `credit_default` validations have been run against a real sample and a real model, and
every defect class this project has found was found by a person reading one of their reports at
roughly $5 and eighteen minutes a run. The runs are committed under `eval/results/first-live/`
on D-087's terms, so the same reading can be a test: this module asks of each archived run the two
questions whose answers cost the most to learn.

**Is every number in the prose a claim, and is every claim a number in the prose?** That is
`tests/test_golden_spec.py` check 7, which the Phase 1 golden has answered since it was written.
Here it is asked of every rendered live report, and -- because a repair round removes the numbers
it could not verify -- of every *first draft* those reports were repaired from, which is the only
place the tokens that provoked a round still exist. The counting is `claimsupport.cover`, shared
with check 7 rather than copied from it (DECISIONS D-118).

**May a repair round change a line nobody flagged?** D-109 says no, on the strength of one round of
one run. The archive holds six rounds over three runs, each with its previous draft quoted in its
own repair prompt, so the guarantee is replayed against all six. The sixth run adds none: it is the
first live run that repaired nothing, so what it contributes is the negative case of both questions
-- every token of every one of its first drafts is a claim of the shipped report, and its pre- and
post-repair claim sets are the same set (D-124).

Nothing here calls a model, downloads anything or trains on anything: the cassettes are read as
JSON and the reports as text.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Final

import pytest

from archivesupport import (
    ARCHIVE,
    CREDIT_VERSION,
    ArchivedRun,
    RepairRound,
    rendered_runs,
)
from claimsupport import ClaimKey, cover
from quaestor.report.repair import _round_records, scope_to_flagged_lines
from quaestor.trace import EventType
from quaestor.verifier.claim import ClaimStatus, VerifiedClaim
from quaestor.verifier.match import Match
from quaestor.verifier.tokens import eligible_numbers

RUNS: Final = rendered_runs()
"""The four archived runs that rendered a report: attempts 3, 4, 5 and the sixth, `credit`."""

ROUNDS: Final = [round_ for run in RUNS for round_ in run.repair_rounds()]
"""The six repair rounds of those runs, in run and then trace order; the sixth run has none."""

KNOWN_RESIDUE: Final = {
    ("credit-attempt3", "data_integrity"): ["9.982e-06"],
    ("credit-attempt3", "outcomes"): ["0.08"],
    ("credit-attempt4", "conceptual_soundness"): ["1.92e-05", "-5.589e-05"],
    ("credit-attempt4", "data_integrity"): ["9.982e-06"],
    ("credit-attempt5", "outcomes"): ["10160", "16210"],
}
"""Every token of a first draft that the run's post-repair claims do not account for, by section.

This table is the point of the fixture. A token in it is a number the run counted in its
denominator and then paid a model call to remove, and every entry has a decision behind it:

* the exponent literals `9.982e-06`, `1.92e-05` and `-5.589e-05` are one token each *now*, and the
  archived `claims.json` files were written by the tokenizer that split them, so their claims are
  recorded as `9.982`, `6`, `1.92`, `5` and `-5.589` and nothing matches the whole literal. That is
  D-099, seen from the other side: the same three literals in three runs.
* attempt 3's second `0.08` is the cost of the defect D-109 fixed. The round on its section 4 was
  provoked by one number on one line and the re-draft also rewrote "…the bound of 0.08
  [[art:630f28f4:threshold.O1.auc_gap]] is not breached" into "…the declared bound is not
  breached", so a verified claim left the report for a line nobody had flagged.
* attempt 5's `10160` and `16210` are counts `four_significant_figures` rounded on their way into
  the prompt, which is D-110.

The `50` of attempt 3's "under rule O1 (D-050)" was in this table when the fixture was written and
is not in it now: it is the one token class the archive found that no decision covered, and D-116
excludes it. A new entry appearing here is the next one.

The sixth run, `credit`, has no entry at all, and that is a fact about the run rather than a gap in
the table: it verified all 210 of its claims on the first pass, so every token of every one of its
seven first drafts is accounted for by a claim of the shipped report and it repaired nothing.
"""


REDRAFTED: Final = {
    ("credit-attempt3", "data_integrity"): 1,
    ("credit-attempt3", "outcomes"): 1,
    ("credit-attempt4", "conceptual_soundness"): 2,
    ("credit-attempt4", "data_integrity"): 1,
    ("credit-attempt5", "outcomes"): 4,
    ("credit-attempt5", "monitoring"): 1,
}
"""How many flagged lines each archived round's re-draft actually changed, once scoped.

Fewer than the round flagged, wherever two flagged claims sat on one line: attempt 3's
data-integrity round flagged the mantissa and the exponent of one `9.982e-06` and attempt 4's
flagged the same literal again, so a round of two claims re-drafts one line. It is the figure
`lines_redrafted` puts on the `repair` trace event (D-109).
"""


UNFLAGGED: Final = {
    ("credit-attempt3", "data_integrity"): 39,
    ("credit-attempt3", "outcomes"): 41,
    ("credit-attempt4", "conceptual_soundness"): 41,
    ("credit-attempt4", "data_integrity"): 49,
    ("credit-attempt5", "outcomes"): 52,
    ("credit-attempt5", "monitoring"): 23,
}
"""How many written lines of each round's previous draft carried no flagged claim.

The figures `docs/EVALUATION.md` section 1 prints for what D-109's guarantee is over: 245 lines
across the six rounds, every one of which comes back byte-identical.
"""


def _tokens(text: str) -> list[str]:
    """The eligible numeric tokens of a piece of drafted prose, in prose order."""
    return [token.text for token in eligible_numbers(text, package_version=CREDIT_VERSION).tokens]


def _ids(items: list[ArchivedRun]) -> list[str]:
    """Test ids for the archived runs."""
    return [run.name for run in items]


def _round_ids(items: list[RepairRound]) -> list[str]:
    """Test ids for the archived repair rounds: the run and the section it re-drafted."""
    return [f"{round_.run.name}:{round_.section.value}" for round_ in items]


# --- check 7, generalised from the golden to every rendered live run ----------------------------


@pytest.mark.parametrize("run", RUNS, ids=_ids(RUNS))
def test_every_number_of_a_rendered_report_is_covered_by_a_post_repair_claim(
    run: ArchivedRun,
) -> None:
    """Check 7 over a live report: every eligible token claimed, and every claim in the prose.

    This is the renderer's own third refusal rule, re-derived from the committed bytes by today's
    tokenizer rather than by the one the run shipped with. It passing on all four runs is what
    says a change to `tokens.py` has not silently changed what those reports mean: a widened
    exclusion would leave a claim with no token, and a narrowed one a token with no claim.
    """
    coverage = cover(_tokens(run.body()), run.claim_keys("post_repair"))
    assert coverage.uncovered == [], f"{run.name}: numbers in the prose with no claim"
    assert coverage.unclaimed == [], f"{run.name}: claims with no token in the prose"


@pytest.mark.parametrize(
    ("run", "claims"), list(zip(RUNS, (159, 161, 285, 210), strict=True)), ids=_ids(RUNS)
)
def test_the_report_s_own_claim_count_is_the_number_of_eligible_tokens(
    run: ArchivedRun, claims: int
) -> None:
    """One eligible token, one claim: the denominator is the prose and not the model's answer.

    The four counts are the ones `docs/EVALUATION.md` section 1 prints for the four runs.
    """
    assert len(_tokens(run.body())) == len(run.claims()["post_repair"]) == claims


@pytest.mark.parametrize("run", RUNS, ids=_ids(RUNS))
def test_no_first_draft_holds_an_uncovered_number_the_archive_does_not_name(
    run: ArchivedRun,
) -> None:
    """Every token a run counted and could not keep is one of the classes `KNOWN_RESIDUE` names.

    `report.md` cannot answer this. A repair round's answer to a number it could not verify is
    often to delete it, so the tokens that provoked the rounds -- the population every new token
    class has come out of -- survive only in the drafters' own completions. Those are read back
    from the cassettes and checked against the same post-repair claims.
    """
    post = run.claim_keys("post_repair")
    residue = {
        call.section.value: cover(_tokens(call.markdown), post).uncovered
        for call in run.first_drafts()
    }
    found = {section: tokens for section, tokens in residue.items() if tokens}
    expected = {
        section: tokens for (name, section), tokens in KNOWN_RESIDUE.items() if name == run.name
    }
    assert found == expected, f"{run.name}: an unnamed uncovered number in a first draft"


def test_the_decision_reference_of_the_third_run_is_no_longer_a_claim() -> None:
    """D-116, on the sentence it was found in: `(D-050)` is not a claim of fifty.

    The third live run's section 4 drafted "The declared bound on the train-to-test AUC gap under
    rule O1 (D-050) is 0.08 [[art:630f28f4:threshold.O1.auc_gap]]". The `50` was counted in the
    denominator, reported as `unattributed`, and removed by a repair round that also cost the
    section a verified `0.08` on a neighbouring line. The declared bound is still a claim.
    """
    draft = next(
        call
        for call in ArchivedRun("credit-attempt3").first_drafts()
        if call.section.value == "outcomes"
    )
    sentence = next(line for line in draft.markdown.split("\n") if "(D-050)" in line)
    eligible = eligible_numbers(sentence, package_version=CREDIT_VERSION)
    assert [token.text for token in eligible.tokens] == ["0.08"]
    assert ("decisions_reference", "D-050") in [
        (token.pattern, token.text) for token in eligible.excluded
    ]
    flagged = [
        claim
        for claim in ArchivedRun("credit-attempt3").claims()["pre_repair"]
        if claim["value"] == 50.0
    ]
    assert len(flagged) == 1 and flagged[0]["status"] == "unattributed"
    assert flagged[0]["text"] == sentence


def test_the_first_and_third_runs_sent_one_prompt_and_only_one_copied_the_reference() -> None:
    """Why D-116 needs both halves, from the archive: writing `(D-050)` is a choice, not a copy.

    The cassette key is a hash of the request, and both runs stored a section-4 draft under
    `a3a5316ac0480158`, so the two prompts are the same bytes. Attempt 1's completion does not
    carry the reference and attempt 3's does. A fix to the caption alone would therefore leave the
    tokenizer unable to read a form a live model may still write -- which is D-099's argument, and
    the reason the exclusion is not redundant.
    """
    shared = "a3a5316ac0480158.json"
    prompts = {}
    for name in ("credit-attempt1", "credit-attempt3"):
        tape = dict(
            json.loads(
                (ARCHIVE / name / "cassettes" / shared).read_text(encoding="utf-8"),
            )
        )
        prompts[name] = str(tape["request"]["prompt"])
        markdown = str(json.loads(tape["completion"]["text"])["markdown"])
        assert ("D-050" in markdown) is (name == "credit-attempt3"), name
    assert prompts["credit-attempt1"] == prompts["credit-attempt3"]
    assert "(D-050)" in prompts["credit-attempt3"], "the caption the prompt showed both runs"


def test_the_summary_that_taught_the_drafter_to_write_it_no_longer_does() -> None:
    """The other half of D-116: the reference came from an artifact caption the prompt showed.

    Attempt 3's own artifact index still carries `"O1: the train-to-test AUC gap (D-050)"` -- the
    archive is the record of what that build did and is not edited -- so the fixture reads the
    caption out of the run and asserts that the shipped table no longer writes one like it.
    """
    from quaestor.tools.thresholds import THRESHOLD_SUMMARIES

    index = json.loads(
        (ARCHIVE / "credit-attempt3" / "artifacts" / "index.json").read_text(encoding="utf-8")
    )
    archived = index["artifacts"]["threshold.O1.auc_gap"]["summary"]
    assert archived == "O1: the train-to-test AUC gap (D-050)"
    assert THRESHOLD_SUMMARIES["threshold.O1.auc_gap"] == "O1: the train-to-test AUC gap"
    assert not [
        name for name, text in THRESHOLD_SUMMARIES.items() if re.search(r"\bD-\d{3}\b", text)
    ]


@pytest.mark.parametrize(
    ("run_name", "literal"),
    [
        ("credit-attempt3", "9.982e-06"),
        ("credit-attempt4", "9.982e-06"),
        ("credit-attempt4", "1.92e-05"),
        ("credit-attempt4", "-5.589e-05"),
    ],
)
def test_an_exponent_literal_a_run_wrote_is_one_token_now(run_name: str, literal: str) -> None:
    """D-099 over the drafts that wrote the form, in both the runs that wrote it.

    Each of these literals cost its run two failed claims -- a mantissa the artifact does not hold
    and an invented claim of the exponent's digits -- and the archived `claims.json` still records
    them that way, which is why `KNOWN_RESIDUE` names the whole literal as uncovered. What is
    asserted here is the reading: one token, and its value is the number the drafter meant.
    """
    run = ArchivedRun(run_name)
    line = next(
        line for call in run.first_drafts() for line in call.markdown.split("\n") if literal in line
    )
    tokens = [token for token in eligible_numbers(line).tokens if token.text == literal]
    assert len(tokens) == 1
    assert tokens[0].value == float(literal)
    assert str(abs(float(literal.split("e")[0]))) not in [
        token.text for token in eligible_numbers(line).tokens if token.text != literal
    ]


def test_the_section_reference_of_the_first_run_would_not_be_a_claim_now() -> None:
    """D-112 arrived at attempt 5 and attempt 1 had already paid for it.

    The first live run's section 3 wrote "the contamination finding in section 3.3", and `3.3` was
    counted, reported as `unsupported` and re-drafted -- one of the three flagged claims of the one
    repair round that run made, which was on that same section. Attempt 1 committed no
    `claims.json`, so the failure is read off the `claim_check` events of its trace instead, and
    the exclusion is checked against the sentence the cassette holds.
    """
    run = ArchivedRun("credit-attempt1")
    failed = [
        event
        for event in run.events(EventType.claim_check)
        if event.payload["status"] != "verified"
    ]
    assert [event.payload["value"] for event in failed] == [9.982, 6.0, 3.3]
    sentence = next(
        line
        for call in run.first_drafts()
        for line in call.markdown.split("\n")
        if "finding in section 3.3" in line
    )
    eligible = eligible_numbers(sentence, package_version=CREDIT_VERSION)
    assert "3.3" not in [token.text for token in eligible.tokens]
    assert ("section_number", "section 3.3") in [
        (token.pattern, token.text) for token in eligible.excluded
    ]


# --- the repair rounds, replayed from the prompts that quoted their own previous drafts ---------


def test_the_archive_holds_six_repair_rounds_one_per_section_that_had_one() -> None:
    """What the replay below is over, and the assumption that lets a cassette be found by section.

    A re-draft is located by the section its prompt names, which is unambiguous only because no
    archived section went to a second round: every `repair` event of every run is `round: 1`. A
    future archive with two rounds on one section needs the pairing done on the prompt's quoted
    previous draft instead, and this assertion is what will say so. Six rounds over four rendered
    runs, because the sixth repaired nothing.
    """
    assert len(ROUNDS) == 6
    assert [round_.event.payload["round"] for round_ in ROUNDS] == [1] * 6
    assert Counter((round_.run.name, round_.section) for round_ in ROUNDS).most_common(1)[0][1] == 1


@pytest.mark.parametrize("round_", ROUNDS, ids=_round_ids(ROUNDS))
def test_a_round_keeps_every_unflagged_line_of_its_previous_draft_byte_identical(
    round_: RepairRound,
) -> None:
    """D-109's guarantee, over all six archived rounds and every line of each.

    The previous draft is the one the prompt quoted, so this is the round the run actually made.
    The assertion is not that the damaged sentence survives -- that is the fifth run's own case,
    in `tests/test_live_credit_attempt5.py` -- but the whole of what D-109 promises: *every* line
    of the previous draft that carried no flagged claim comes back exactly as it was.

    What the cassettes cannot give is the other half of a round. The re-extraction that followed
    each of these rounds was performed on the run's own unscoped re-draft, so no tape holds the
    extraction of the scoped text and the claims a scoped round would have produced cannot be
    replayed. This asserts the text, and `tests/test_repair.py` asserts the claims on fixtures.
    """
    result = scope_to_flagged_lines(round_.previous, round_.redraft, list(round_.failures))
    kept = set(result.markdown.split("\n"))
    unflagged = round_.unflagged_lines()
    assert len(unflagged) == UNFLAGGED[(round_.run.name, round_.section.value)]
    missing = [line for line in unflagged if line not in kept]
    assert missing == [], f"{round_.run.name}:{round_.section.value} lost an unflagged line"
    assert result.scoped is True, "the round found the lines its flagged claims sit on"
    assert result.lines_redrafted == REDRAFTED[(round_.run.name, round_.section.value)]


@pytest.mark.parametrize("round_", ROUNDS, ids=_round_ids(ROUNDS))
def test_the_re_draft_each_round_actually_returned_changed_a_line_nobody_flagged(
    round_: RepairRound,
) -> None:
    """The measurement that says the scoping is worth having, run by run.

    D-109 was decided on one round of one run. Replaying the other five shows the drafter changing
    lines it was not asked about in five of the six: attempt 3's outcomes round rewrote two,
    attempt 4's two rounds two and one, attempt 5's outcomes and monitoring rounds two and three,
    and only attempt 3's data-integrity round returned every unflagged line untouched. Ten lines
    across the archive that the current build discards.
    """
    returned = set(round_.redraft.split("\n"))
    drifted = [line for line in round_.unflagged_lines() if line not in returned]
    expected = {
        ("credit-attempt3", "data_integrity"): 0,
        ("credit-attempt3", "outcomes"): 2,
        ("credit-attempt4", "conceptual_soundness"): 2,
        ("credit-attempt4", "data_integrity"): 1,
        ("credit-attempt5", "outcomes"): 2,
        ("credit-attempt5", "monitoring"): 3,
    }
    assert len(drifted) == expected[(round_.run.name, round_.section.value)]


@pytest.mark.parametrize(
    ("run_name", "rewritten", "removed"),
    [("credit-attempt3", 0, 3), ("credit-attempt4", 0, 6), ("credit-attempt5", 0, 5)],
)
def test_the_pairing_over_a_run_s_own_repair_records(
    run_name: str, rewritten: int, removed: int
) -> None:
    """D-111 over the real records: what Appendix A would say of each archived run now.

    `_round_records` is given each round's flagged claims and the claims of the section after the
    round -- which for these runs is the post-repair set, because no archived section went to a
    second round -- and the split it returns is the one `docs/EVALUATION.md` states: attempt 4's
    round rewrote none and removed six, attempt 5's rewrote none and removed five. Both runs
    reported one rewrite at the time, because D-105's two pairing grounds were read as
    alternatives and a slice paragraph's siblings share its sentence skeleton.
    """
    run = ArchivedRun(run_name)
    post = run.claims()["post_repair"]
    rows_total = 0
    removed_total = 0
    for round_ in run.repair_rounds():
        after = [
            Match(claim=VerifiedClaim(**claim))
            for claim in post
            if claim["section"] == round_.section.value
        ]
        rows, gone = _round_records(round_.section, list(round_.failures), after)
        rows_total += len(rows)
        removed_total += len(gone)
    assert (rows_total, removed_total) == (rewritten, removed)
    rounds = run.repair_rounds()
    traced_removed = sum(len(round_.event.payload["removed"]) for round_ in rounds)
    traced_rewritten = sum(len(round_.event.payload["repaired"]) for round_ in rounds)
    assert traced_removed + traced_rewritten == removed_total, (
        "the same claims, split the other way: what the run reported as a rewrite is a removal"
    )
    assert traced_rewritten == (0 if run_name == "credit-attempt3" else 1)


@pytest.mark.parametrize("round_", ROUNDS, ids=_round_ids(ROUNDS))
def test_every_flagged_claim_of_every_round_sits_on_a_line_of_its_previous_draft(
    round_: RepairRound,
) -> None:
    """Why no archived round would take the unscoped fallback, asserted rather than assumed.

    `scope_to_flagged_lines` returns the whole re-draft when it can find no line of the previous
    draft carrying a flagged claim, and that path is now recorded as `scoped: false` (D-117). None
    of the six rounds takes it, and the reason is D-085's: `Claim.text` *is* the line, so a flagged
    claim of a draft is always findable in it.
    """
    lines = {" ".join(line.split()) for line in round_.previous.split("\n") if line.strip()}
    assert all(line in lines for line in round_.flagged_lines())
    assert all(match.claim.status is not ClaimStatus.verified for match in round_.failures), (
        "a round is provoked only by claims that did not verify"
    )


def test_no_first_draft_of_any_archived_run_wrote_an_unwrapped_claim_of_a_decision() -> None:
    """The `D-\\d{3}` exclusion over the whole archive, so its blast radius is visible.

    An exclusion lowers the grounding denominator, which is the failure mode D-015's audit list
    exists for, so this names every token the new class actually removes across five committed
    runs: one, attempt 3's `(D-050)`. A pattern that quietly excluded more than it was decided for
    would show up here as a second run.
    """
    found: dict[str, list[str]] = {}
    for name in ("credit-attempt1", *[run.name for run in RUNS]):
        run = ArchivedRun(name)
        excluded = [
            token.text
            for call in run.draft_calls()
            for token in call.eligible().excluded
            if token.pattern == "decisions_reference"
        ]
        if excluded:
            found[name] = excluded
    assert found == {"credit-attempt3": ["D-050"]}


def test_the_calls_the_archive_is_read_through_are_the_calls_the_traces_counted() -> None:
    """The fixture reads every drafting call each run made, and no more than that.

    A reader that silently skipped a cassette would make every check above vacuous on the section
    it skipped, so the count of recovered draft calls is asserted against the `llm_call` events
    the trace recorded with `purpose: draft`.
    """
    for run in RUNS:
        drafts = [
            event for event in run.events(EventType.llm_call) if event.payload["purpose"] == "draft"
        ]
        assert len(run.draft_calls()) == len(drafts), run.name
        assert len(run.first_drafts()) == 7, run.name
        assert sum(1 for call in run.draft_calls() if call.is_repair) == len(run.repair_rounds())


def test_a_draft_call_recovered_from_a_cassette_is_the_prose_the_report_carries() -> None:
    """The recovered markdown is the run's own text, not a re-serialisation of it.

    One line of each run's last first draft is looked for in the rendered report. It is the check
    that keeps the cassette reader honest: a reader that returned the prompt, or a truncated
    completion, would pass every coverage assertion above by having nothing in it.
    """
    for run in RUNS:
        report = run.report()
        for call in run.first_drafts():
            longest = max(call.markdown.split("\n"), key=len)
            assert len(longest) > 80, (run.name, call.cassette)
            if call.section.value in {round_.section.value for round_ in run.repair_rounds()}:
                continue
            assert longest in report, (run.name, call.cassette)


def test_the_known_residue_table_names_only_sections_the_archive_has() -> None:
    """A table of expectations that has drifted from the archive is not a test of it."""
    sections = {(run.name, call.section.value) for run in RUNS for call in run.first_drafts()}
    assert set(KNOWN_RESIDUE) <= sections


def test_every_residue_token_is_a_number_the_run_wrote_and_the_report_does_not_carry() -> None:
    """Each entry of `KNOWN_RESIDUE` is checked to be what it claims: written, then gone."""
    for (name, section), tokens in KNOWN_RESIDUE.items():
        run = ArchivedRun(name)
        draft = next(call for call in run.first_drafts() if call.section.value == section)
        for token in tokens:
            assert token in draft.markdown, (name, section, token)
        post = Counter(ClaimKey(claim["value"], False) for claim in run.claims()["post_repair"])
        for token in tokens:
            key = ClaimKey(float(token), False)
            drafted = Counter(
                ClaimKey(item.value, False)
                for item in eligible_numbers(draft.markdown, package_version=CREDIT_VERSION).tokens
            )
            assert drafted[key] > post[key], (name, section, token)


# --- the sixth run, which repaired nothing ------------------------------------------------------


def test_the_sixth_run_carries_no_repair_event_and_no_round_to_replay() -> None:
    """D-124: the first live run with no repair round, asserted from three places at once.

    The trace has no `repair` event, `claims.json` counts zero repairs and lists no repair row, and
    the report's own Appendix C prints `repair rounds | 0`. All three have to agree, because the
    absence of a round is what the two assertions below are conditional on: a run that had repaired
    something would answer the coverage questions about its re-drafts and not about its drafts.

    It is also the reason D-109's scoped re-draft path has still not run live. Six archived rounds
    are replayed above and every one of them was made by a build without the scoping in it.
    """
    run = ArchivedRun("credit")
    assert run.events(EventType.repair) == []
    assert run.repair_rounds() == []
    assert run.claims()["repairs"] == [], "no repair row in Appendix A"
    assert [call.cassette for call in run.draft_calls() if call.is_repair] == []
    assert "| repair rounds | 0 |" in run.report()
    assert "| re-asks | 0 |" in run.report()
    assert not [round_ for round_ in ROUNDS if round_.run.name == "credit"]


def test_the_sixth_run_s_claim_set_is_the_same_before_and_after_repair() -> None:
    """The other half of the same fact: nothing was flagged, so nothing moved.

    Both stages hold 210 claims at precision 1.0000 and the two lists are identical documents, so
    every check this module makes against the post-repair set is a check against what the drafters
    actually wrote. On attempts 3, 4 and 5 the two sets differ by exactly the numbers their rounds
    removed, which is what `KNOWN_RESIDUE` is a table of.
    """
    run = ArchivedRun("credit")
    claims = run.claims()
    assert claims["pre_repair"] == claims["post_repair"]
    assert len(claims["pre_repair"]) == 210
    for stage in ("pre_repair", "post_repair"):
        grounding = claims["grounding"][stage]
        assert (grounding["precision"], grounding["n_claims"]) == (1.0, 210)
        assert grounding["status_counts"]["verified"] == 210
    assert [event.payload["status"] for event in run.events(EventType.claim_check)].count(
        "verified"
    ) == 210


def test_every_token_of_every_first_draft_of_the_sixth_run_is_a_claim_of_its_report() -> None:
    """The negative case of `KNOWN_RESIDUE`, which only a run that repaired nothing can give.

    On the other three runs a first draft's uncovered tokens are the population every new defect
    class has come out of. Here there are none in any of the seven, which is the strongest form the
    coverage question has been answered in: the drafters wrote 210 numbers, the extractor found the
    same 210, and the report carries all of them.
    """
    run = ArchivedRun("credit")
    post = run.claim_keys("post_repair")
    drafts = run.first_drafts()
    assert len(drafts) == 7
    for call in drafts:
        coverage = cover(_tokens(call.markdown), post)
        assert coverage.uncovered == [], (call.cassette, call.section.value)
    assert ("credit", "outcomes") not in KNOWN_RESIDUE


def test_the_sixth_run_s_drafts_are_the_prose_its_report_carries_line_for_line() -> None:
    """Cassette-to-report agreement with no round in the way, so it holds for every written line.

    The general check above skips the sections a run repaired, because a repaired section's first
    draft is not what the report carries. Nothing was repaired here, so every written line of every
    one of the seven completions has to be in `report.md` -- except a `[[table:<name>]]` line,
    which is a directive the renderer replaces with the table itself (D-013, D-115).
    """
    run = ArchivedRun("credit")
    report = run.report()
    directive = re.compile(r"^\s*\[\[table:[^\]]+\]\]\s*$")
    tables = 0
    for call in run.first_drafts():
        lines = [line for line in call.markdown.split("\n") if line.strip()]
        assert len(lines) > 3, call.cassette
        tables += sum(1 for line in lines if directive.match(line))
        missing = [line for line in lines if line not in report and not directive.match(line)]
        assert missing == [], (call.cassette, missing[:1])
    assert tables == 11, "eight slice tables and the three the plan's own metrics wrote"
