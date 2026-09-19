"""Phase 8: the repair loop and the wrapper, over hand-built sections rather than a whole run.

`tests/test_pipeline.py` exercises the loop end to end; this module exercises the parts a whole
run cannot reach reliably -- a number the drafter removes instead of citing, a claim that moves too
far to be the same claim repaired, a token that must not be wrapped because it is inside a
citation's hash.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.llm import FakeLLM, ScriptedLLM
from quaestor.report.drafter import Drafter, template_section
from quaestor.report.repair import (
    MAX_REPAIR_ROUNDS,
    UNVERIFIED_OPEN,
    DraftInputs,
    SectionDraft,
    is_wrapped,
    repair_sections,
    scope_to_flagged_lines,
    wrap_unverified,
    wrapped_values,
)
from quaestor.report.schema import check_structure, malformed_citations
from quaestor.report.sections import artifact_briefs, brief_for
from quaestor.trace import TraceReader, TraceWriter
from quaestor.verifier import ClaimStatus, extract, match_claims
from quaestor.verifier.extract import extraction_from
from quaestor.vocab import Configuration, ReportSection
from reportsupport import SectionFake

SECTION = ReportSection.outcomes

MINIMAL_REPORT_FOR_TOKENS = "\n".join(
    ["---", "schema_version: 1", "---", "", "# Validation report", "", "BODY"]
)
"""Enough of a report for the token check; the heading rules fail and are not what is asserted."""


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with the one artifact these sections cite."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar, "auc on test")
    return store


def verify_with(store: ArtifactStore):  # noqa: ANN201 - a closure, typed by its use
    """Return a `verify` callable that extracts with the shared fake and matches for real."""
    extractor = SectionFake()

    def verify(section: ReportSection, markdown: str) -> tuple[object, list[object]]:
        extraction = extract(section, markdown, extractor)
        return extraction, match_claims(
            extraction.claims, store, unattributed=extraction.unattributed_ids
        )

    return verify


def draft_of(store: ArtifactStore, markdown: str) -> SectionDraft:
    """Extract and match one section of prose, with no model anywhere."""
    extraction, matches = verify_with(store)(SECTION, markdown)
    return SectionDraft(
        brief=brief_for(SECTION), markdown=markdown, extraction=extraction, matches=matches
    )


def drafter_returning(*answers: str) -> Drafter:
    """A drafter whose model returns these markdown answers, in order."""
    scripted = ScriptedLLM([json.dumps({"markdown": answer}) for answer in answers])
    return Drafter(scripted, package="credit_default", version="1.0")


# --- the wrapper ----------------------------------------------------------------------------


def test_only_the_numbers_that_did_not_verify_are_wrapped(store: ArtifactStore) -> None:
    citation = store.artifact("metrics.test.auc").citation()
    markdown = f"The AUC is 0.7412 {citation}.\nThe Brier score is 0.68."
    draft = draft_of(store, markdown)
    wrapped = wrap_unverified(draft.markdown, draft.claims)
    assert f"{UNVERIFIED_OPEN}0.68⟧" in wrapped
    assert "0.7412 [[art:" in wrapped
    assert wrapped_values(wrapped) == [0.68]


def test_a_token_inside_a_citation_is_never_wrapped(store: ArtifactStore) -> None:
    """A claim of 6 must not turn `[[art:6bff3109:...]]` into something that is not a citation."""
    artifact = store.artifact("metrics.test.auc")
    markdown = f"The AUC is 0.7412 {artifact.citation()}, and 6 is unsupported."
    draft = draft_of(store, markdown)
    wrapped = wrap_unverified(draft.markdown, draft.claims)
    assert artifact.citation() in wrapped
    assert f"and {UNVERIFIED_OPEN}6⟧ is unsupported" in wrapped


def test_a_number_inside_inline_code_is_not_wrapped_either(store: ArtifactStore) -> None:
    markdown = "The feature `bill_mean_6m` is retained, and 0.68 is unsupported."
    draft = draft_of(store, markdown)
    wrapped = wrap_unverified(draft.markdown, draft.claims)
    assert "`bill_mean_6m`" in wrapped
    assert wrapped_values(wrapped) == [0.68]


def test_two_failing_claims_of_one_value_wrap_two_occurrences(store: ArtifactStore) -> None:
    markdown = "The first number is 0.68.\nThe second number is 0.68."
    draft = draft_of(store, markdown)
    wrapped = wrap_unverified(draft.markdown, draft.claims)
    assert wrapped.count(UNVERIFIED_OPEN) == 2
    assert wrapped_values(wrapped) == [0.68, 0.68]


def test_a_section_with_nothing_to_wrap_comes_back_unchanged(store: ArtifactStore) -> None:
    markdown = f"The AUC is 0.7412 {store.artifact('metrics.test.auc').citation()}."
    draft = draft_of(store, markdown)
    assert wrap_unverified(draft.markdown, draft.claims) == markdown


def test_is_wrapped_and_wrapped_values_read_the_marker_the_schema_defines() -> None:
    text = f"a {UNVERIFIED_OPEN}0.68⟧ b 0.74 c"
    assert is_wrapped(text, text.index("0.68"))
    assert not is_wrapped(text, text.index("0.74"))
    assert wrapped_values(text) == [0.68]
    assert wrapped_values(f"{UNVERIFIED_OPEN}no number here⟧") == []
    assert wrapped_values(f"{UNVERIFIED_OPEN}0.68 with no close") == []


# --- the loop -------------------------------------------------------------------------------


def test_a_section_that_verifies_is_not_re_drafted(store: ArtifactStore) -> None:
    markdown = f"The AUC is 0.7412 {store.artifact('metrics.test.auc').citation()}."
    llm = FakeLLM(default=json.dumps({"markdown": "should never be asked for"}))
    outcome = repair_sections(
        [draft_of(store, markdown)],
        drafter=Drafter(llm, package="p", version="1.0"),
        verify=verify_with(store),
        inputs={},
    )
    assert outcome.rounds == 0
    assert outcome.repairs == []
    assert llm.call_count == 0


def test_one_round_when_the_re_draft_cites_the_number(store: ArtifactStore, tmp_path: Path) -> None:
    citation = store.artifact("metrics.test.auc").citation()
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="repair")
    outcome = repair_sections(
        [draft_of(store, "The AUC is 0.7412.")],
        drafter=drafter_returning(f"The AUC is 0.7412 {citation}."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
    )
    assert outcome.rounds == 1
    assert [repair.before.status for repair in outcome.repairs] == [ClaimStatus.unsupported]
    assert [repair.after.status for repair in outcome.repairs] == [ClaimStatus.verified]
    assert outcome.drafts[0].rounds == 1
    events = TraceReader(trace.path).events("repair")
    assert len(events) == 1
    assert events[0].payload["flagged"] == [outcome.repairs[0].claim_id]
    assert events[0].payload["removed"] == []
    assert events[0].payload["still_failing"] == []


def test_a_corrected_value_is_paired_with_the_claim_it_replaced(store: ArtifactStore) -> None:
    citation = store.artifact("metrics.test.auc").citation()
    outcome = repair_sections(
        [draft_of(store, f"The AUC gap is 0.7512 {citation}.")],
        drafter=drafter_returning(f"The AUC gap is 0.7412 {citation}."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
    )
    assert outcome.rounds == 1
    assert len(outcome.repairs) == 1
    assert outcome.repairs[0].before.value == 0.7512
    assert outcome.repairs[0].after.value == 0.7412
    assert "0.7412" in outcome.repairs[0].instruction


def test_a_number_the_drafter_removed_is_recorded_on_the_trace_and_not_in_the_repairs(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """ "cite or remove" allows removing; a claim that is gone has no `after` side (D-073)."""
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="removed")
    outcome = repair_sections(
        [draft_of(store, "The AUC is 0.68.")],
        drafter=drafter_returning("The AUC is not stated here."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
    )
    assert outcome.rounds == 1
    assert outcome.repairs == []
    assert TraceReader(trace.path).events("repair")[0].payload["removed"] == [0.68]
    assert outcome.drafts[0].failures == []


def test_the_loop_stops_after_two_rounds_and_leaves_the_claim_failing(
    store: ArtifactStore, tmp_path: Path
) -> None:
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="stubborn")
    outcome = repair_sections(
        [draft_of(store, "The AUC is 0.68.")],
        drafter=drafter_returning("The AUC is 0.68.", "The AUC is 0.68."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
    )
    assert outcome.rounds == MAX_REPAIR_ROUNDS
    assert outcome.drafts[0].rounds == MAX_REPAIR_ROUNDS
    assert [claim.status for claim in outcome.drafts[0].claims] == [ClaimStatus.unsupported]
    assert len(TraceReader(trace.path).events("repair")) == MAX_REPAIR_ROUNDS
    wrapped = wrap_unverified(outcome.drafts[0].markdown, outcome.drafts[0].claims)
    assert f"{UNVERIFIED_OPEN}0.68⟧" in wrapped


def test_the_repair_prompt_carries_the_verifier_s_own_sentence(store: ArtifactStore) -> None:
    scripted = ScriptedLLM([json.dumps({"markdown": "The AUC is 0.68."})])
    repair_sections(
        [draft_of(store, "The AUC is 0.68.")],
        drafter=Drafter(scripted, package="p", version="1.0"),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        max_rounds=1,
    )
    prompt = scripted.calls[0].prompt
    assert "you wrote 0.68 with no citation" in prompt
    assert "The AUC is 0.68." in prompt


def test_a_claim_is_not_paired_with_a_replacement_that_did_not_verify_either(
    store: ArtifactStore,
) -> None:
    """The pairing looks for the claim that was *repaired*, not merely the one nearest to it."""
    citation = store.artifact("metrics.test.auc").citation()
    outcome = repair_sections(
        [draft_of(store, "The AUC is 0.7500.")],
        drafter=drafter_returning(f"The AUC is 0.7480.\nThe AUC is 0.7412 {citation}."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        max_rounds=1,
    )
    assert len(outcome.repairs) == 1
    assert outcome.repairs[0].after.value == 0.7412
    assert outcome.repairs[0].after.status is ClaimStatus.verified


def test_a_value_that_is_already_wrapped_is_not_wrapped_twice(store: ArtifactStore) -> None:
    markdown = f"An earlier {UNVERIFIED_OPEN}0.68⟧ stands.\nThe Brier score is 0.68."
    draft = draft_of(store, markdown)
    wrapped = wrap_unverified(draft.markdown, draft.claims)
    assert wrapped.count(UNVERIFIED_OPEN) == 2
    assert f"{UNVERIFIED_OPEN}{UNVERIFIED_OPEN}" not in wrapped


def test_a_section_draft_reports_its_failures_and_their_messages(store: ArtifactStore) -> None:
    draft = draft_of(store, "The AUC is 0.68.")
    assert draft.section is SECTION
    assert len(draft.failures) == 1
    assert draft.problems and "no citation" in draft.problems[0]


# --- nearness is not identity (DECISIONS D-105) -------------------------------------------------


def test_the_fourth_live_run_s_pairing_is_a_removal_and_not_a_repair(tmp_path: Path) -> None:
    """The attempt-4 case: `1.92` removed, and the unrelated verified `2` left where it was.

    The flagged claim is the `1.92` of "changes test AUC by 1.92e-05" -- an exponent literal the
    tokenizer of the day split in two (D-099) -- and the re-draft dropped the sentence. The `2` of
    "2 are known at origination" survived it, verified, two per cent away, and the nearest-value
    fallback paired the two: Appendix A reported one claim rewritten and five numbers removed of a
    round that rewrote none and removed six, and the repairs table joined two unrelated sentences.
    """
    store = ArtifactStore(tmp_path / "attempt4")
    store.put("ablation.utilisation.delta_auc", 1.9204697640939905e-05, ArtifactKind.scalar, "d")
    store.put("run.features", {"at_origination": 2}, ArtifactKind.json, "features by timing")
    delta = store.artifact("ablation.utilisation.delta_auc").citation()
    timing = "[[art:" + store.artifact("run.features").hash[:8] + ":run.features#at_origination]]"
    before = (
        f"Refitting without utilisation changes test AUC by ⟦x⟧1.92 {delta}, a term barely used.\n"
        f"Of these, 2 {timing} are known at origination."
    ).replace("⟦x⟧", "")
    after = f"Of these, 2 {timing} are known at origination."

    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="attempt4")
    outcome = repair_sections(
        [draft_of(store, before)],
        drafter=drafter_returning(after),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
        max_rounds=1,
    )
    assert outcome.rounds == 1
    assert outcome.repairs == [], "the 1.92 was removed; nothing replaced it"
    event = TraceReader(tmp_path / "trace.jsonl").events("repair")[0]
    assert event.payload["removed"] == [1.92]
    assert event.payload["repaired"] == []


def test_a_number_the_re_draft_corrects_in_place_is_still_paired(store: ArtifactStore) -> None:
    """D-105 restricts the fallback and must not switch it off: this is what it exists for."""
    citation = store.artifact("metrics.test.auc").citation()
    outcome = repair_sections(
        [draft_of(store, f"The AUC is 0.7500 {citation}.")],
        drafter=drafter_returning(f"The AUC is 0.7412 {citation}."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        max_rounds=1,
    )
    assert [repair.after.value for repair in outcome.repairs] == [0.7412]


def test_a_reworded_sentence_pairs_by_the_logical_name_it_still_cites(
    store: ArtifactStore,
) -> None:
    """The second ground: the re-draft rewrote the sentence and kept the citation (D-105).

    The line is not the same line any more -- with its numbers and citations taken out it reads
    differently -- so the skeleton cannot pair the two, and the cited name is what does. Under
    D-109 the rewrite stays on the line it was flagged on, which is where the sentence a repair
    round rewrites now stays.
    """
    citation = store.artifact("metrics.test.auc").citation()
    outcome = repair_sections(
        [draft_of(store, f"Discrimination reaches 0.7500 {citation} on the held-out split.")],
        drafter=drafter_returning(
            f"Discrimination reaches 0.7412 {citation} on the held-out test split, comfortably."
        ),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        max_rounds=1,
    )
    assert [repair.before.status for repair in outcome.repairs] == [ClaimStatus.mismatch]
    assert [repair.after.value for repair in outcome.repairs] == [0.7412]


def test_a_re_draft_that_leaves_no_link_at_all_is_recorded_as_a_removal(
    store: ArtifactStore,
) -> None:
    """The boundary D-105 accepts: no shared line, no shared name, so no repairs row.

    The number is still in the prose, and the round is counted as a removal. That is the direction
    that cannot invent a row joining two unrelated sentences, which is the failure the fourth live
    run's Appendix A actually shipped.
    """
    citation = store.artifact("metrics.test.auc").citation()
    outcome = repair_sections(
        [draft_of(store, "Discrimination on the held-out split reaches 0.7500.")],
        drafter=drafter_returning(f"Held out, the model reaches an AUC of 0.7412 {citation}."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        max_rounds=1,
    )
    assert outcome.repairs == []


# --- Phase 9 follow-up 5: the re-draft is taken line by line (D-109, D-111) --------------------


def _scoped(store: ArtifactStore, previous: str, redraft: str, path: Path) -> tuple[str, int, bool]:
    """Run one repair round over `previous`; return the section, the line count and `scoped`."""
    trace = TraceWriter(path / "trace.jsonl", run_id="scoped")
    outcome = repair_sections(
        [draft_of(store, previous)],
        drafter=drafter_returning(redraft),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
        max_rounds=1,
    )
    event = TraceReader(trace.path).events("repair")[0]
    return (
        outcome.drafts[0].markdown,
        int(event.payload["lines_redrafted"]),
        bool(event.payload["scoped"]),
    )


def test_a_re_draft_that_alters_an_unrelated_line_leaves_that_line_alone(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """D-109: the round flagged one number and the model rewrote the paragraph around it.

    The unflagged line of the fifth live run's section 4 came back with a clause about another
    slice spliced into it, every citation resolving, so nothing downstream could see it was wrong.
    """
    citation = store.artifact("metrics.test.auc").citation()
    keep = f"On the whole split the AUC is 0.7412 {citation}, which is the headline."
    previous = f"{keep}\nOn the low-limit half the AUC is 0.68."
    redraft = (
        f"On the whole split the AUC is 0.7412 {citation}, which is not the figure for this slice."
        f"\nOn the low-limit half the AUC is 0.7412 {citation}."
    )
    markdown, redrafted, scoped = _scoped(store, previous, redraft, tmp_path)
    assert markdown.split("\n")[0] == keep
    assert markdown.split("\n")[1] == f"On the low-limit half the AUC is 0.7412 {citation}."
    assert redrafted == 1
    assert scoped is True, "the round was scoped to its flagged lines"


def test_the_flagged_line_is_still_replaced_by_its_re_draft(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """Scoping the round must not switch the round off: the flagged line takes the new text."""
    citation = store.artifact("metrics.test.auc").citation()
    previous = "An opening sentence with no number in it.\nThe AUC is 0.7500.\nA closing sentence."
    redraft = (
        "An opening sentence with no number in it.\n"
        f"The AUC is 0.7412 {citation}.\nA closing sentence."
    )
    markdown, redrafted, scoped = _scoped(store, previous, redraft, tmp_path)
    assert markdown == (
        "An opening sentence with no number in it.\n"
        f"The AUC is 0.7412 {citation}.\nA closing sentence."
    )
    assert redrafted == 1
    assert scoped is True, "the round was scoped to its flagged lines"


def test_a_flagged_line_the_re_draft_dropped_is_dropped(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """Removing the number by removing the sentence is still one of the three answers."""
    previous = "An opening sentence with no number in it.\nThe AUC is 0.7500."
    markdown, redrafted, scoped = _scoped(
        store, previous, "An opening sentence with no number in it.", tmp_path
    )
    assert markdown == "An opening sentence with no number in it."
    assert redrafted == 1
    assert scoped is True, "the round was scoped to its flagged lines"


def test_the_repair_event_records_how_many_lines_were_re_drafted(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """Two flagged lines, one of them returned unchanged: one line re-drafted."""
    citation = store.artifact("metrics.test.auc").citation()
    previous = "The first AUC is 0.7500.\nThe second AUC is 0.68."
    redraft = f"The first AUC is 0.7412 {citation}.\nThe second AUC is 0.68."
    _, redrafted, scoped = _scoped(store, previous, redraft, tmp_path)
    assert redrafted == 1
    assert scoped is True, "the round was scoped to its flagged lines"


def test_a_replacement_citing_another_artifact_is_a_removal_not_a_rewrite(
    tmp_path: Path,
) -> None:
    """D-111, and it is the fifth live run's own case: 10160 must not pair with 10500.

    Two sub-population paragraphs written to one sentence skeleton. The flagged count cites
    `metrics.train.sub.limit_bal_low.n`; the verified 10500 beside it cites another slice's `n`
    and sits inside the relative window of 10160. Under D-105 read as two alternative grounds the
    skeleton paired them and Appendix A reported a rewrite; the name is what decides.

    The flagged count is written 10161 rather than the run's own 10160 because the live extractor
    called it a `count` and held it to half a unit, while the offline fake calls every unmarked
    token a `ratio` -- and 10160's trailing zero is a place value under D-069, so the fake reads
    it as a claim of ten thousand one hundred and sixty to the nearest ten and verifies it. The
    pairing this test is about is the same either way.
    """
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.train.sub.limit_bal_low.n", 10158, ArtifactKind.scalar, "rows in the slice")
    store.put("metrics.train.sub.utilisation_high.n", 10500, ArtifactKind.scalar, "rows")
    low = store.artifact("metrics.train.sub.limit_bal_low.n").citation()
    high = store.artifact("metrics.train.sub.utilisation_high.n").citation()
    previous = (
        f"On train the slice holds n of 10161 {low}.\nOn train the slice holds n of 10500 {high}."
    )
    redraft = f"On train the slice holds many rows.\nOn train the slice holds n of 10500 {high}."
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="named")
    outcome = repair_sections(
        [draft_of(store, previous)],
        drafter=drafter_returning(redraft),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
        max_rounds=1,
    )
    assert outcome.repairs == []
    event = TraceReader(trace.path).events("repair")[0]
    assert event.payload["repaired"] == []
    assert event.payload["removed"] == [10161.0]


def test_a_re_draft_of_a_section_whose_lines_carry_no_flagged_claim_is_taken_whole(
    store: ArtifactStore,
) -> None:
    """The scoping needs a line to scope to: with none, the round is the round it always was.

    And it says so. D-109 left this fallback returning the whole re-draft with nothing on the
    trace to distinguish it from a round that happened to re-draft every line, so a live run that
    took it would look like a scoped round in the record. `scoped` is that distinction (D-117).
    """
    previous = "The AUC is 0.68."
    failures = draft_of(store, "A sentence from another draft entirely, holding 0.68.").failures
    assert failures
    result = scope_to_flagged_lines(previous, "A wholly new line.", failures)
    assert result.markdown == "A wholly new line."
    assert result.lines_redrafted == 1
    assert result.scoped is False


def test_the_repair_event_says_when_the_round_was_not_scoped_at_all(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """D-117: the fallback fired, and the trace event carries `scoped: false` rather than nothing.

    The round is provoked here by a claim whose text is a line of no draft at all, which is the
    only way `_flagged_line_numbers` comes back empty: the section is then replaced wholesale, and
    that is a fact about the run a reader of the trace should not have to infer.
    """
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="unscoped")
    draft = draft_of(store, "The AUC is 0.68.")
    stranger = draft_of(store, "A sentence from another draft entirely, holding 0.68.")
    draft.matches = stranger.matches
    repair_sections(
        [draft],
        drafter=drafter_returning("A wholly new line."),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
        max_rounds=1,
    )
    event = TraceReader(trace.path).events("repair")[0]
    assert event.payload["scoped"] is False
    assert event.payload["lines_redrafted"] == 1


# --- D-178: the wrapper lands on the claim's own sentence, not on the first equal number --------


def test_the_wrapper_lands_on_the_sentence_whose_number_failed(store: ArtifactStore) -> None:
    """The second symptom of the `msr__L1__eom_balance` defect, reduced to two lines.

    Section 2 of that run carried eleven verified claims at 0 and one failed claim at the same
    value, and the wrapper took the first token it found -- marking a sentence that verified.
    """
    citation = store.artifact("metrics.test.auc").citation()
    markdown = f"The verified number is 0.7412 {citation}.\nThe unsupported number is 0.7412."
    draft = draft_of(store, markdown)
    wrapped = wrap_unverified(draft.markdown, draft.claims)
    assert f"The verified number is 0.7412 {citation}." in wrapped, (
        "the sentence whose number verified must come through untouched"
    )
    assert f"The unsupported number is {UNVERIFIED_OPEN}0.7412⟧." in wrapped
    assert wrapped_values(wrapped) == [0.7412]


def test_a_failed_claim_whose_sentence_was_reworded_still_gets_wrapped(
    store: ArtifactStore,
) -> None:
    """The fallback: a claim whose text is no longer in the prose is paired on its value alone."""
    markdown = "The second number is 0.68."
    draft = draft_of(store, markdown)
    reworded = [
        claim.model_copy(update={"text": "a sentence this section no longer carries"})
        for claim in draft.claims
    ]
    wrapped = wrap_unverified(markdown, reworded)
    assert wrapped_values(wrapped) == [0.68]


def test_a_near_zero_and_a_true_zero_in_one_section_both_verify(tmp_path: Path) -> None:
    """The `msr__L1__eom_balance` defect end to end, in the arm whose grounding must be 1.0.

    Both symptoms need both numbers in one section: the near-zero is what the old formatter erased
    into a token reading zero, and the true zero beside it is what the wrapper then landed on. The
    template writes its own claims, so a single unattributed token here is the whole defect.
    """
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("challenger.brier", 3.2264600208103315e-13, ArtifactKind.scalar, "challenger brier")
    store.put("challenger.delta_auc", 0.0, ArtifactKind.scalar, "challenger minus champion")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar, "auc on test")
    section = ReportSection.conceptual_soundness
    brief = brief_for(section)
    markdown, declared = template_section(brief, artifacts=artifact_briefs(store, brief))
    assert "0.0000000000003226" in markdown, "the near-zero keeps its significant figures"
    assert "is 0 [[art:" in markdown, "the true zero is still written as a bare zero"
    extraction = extraction_from(section, markdown, declared)
    matches = match_claims(extraction.claims, store, unattributed=extraction.unattributed_ids)
    assert [m for m in matches if m.status is not ClaimStatus.verified] == []
    assert wrap_unverified(markdown, matches) == markdown, "nothing to wrap, so nothing is wrapped"


# --- a malformed citation is a repairable problem (D-189) -------------------------------------


BRACE = "[[art:22858a09:run.model_summary#vif_threshold}]]"
"""The token that cost a `full_agent` cell $6.6781: a JSON brace that leaked into a citation."""

CLEAN = "[[art:22858a09:run.model_summary#vif_threshold]]"
"""The same citation as the model wrote it correctly elsewhere in the same run."""


def test_the_repair_loop_and_the_renderer_read_one_grammar(store: ArtifactStore) -> None:
    """`malformed_citations` is the renderer's own check, so the two cannot disagree.

    A repair that "fixed" a token the renderer still refuses would cost a paid call and the cell
    as well, which is the whole failure this closes.
    """
    assert malformed_citations(f"a {BRACE} b") == [BRACE]
    assert malformed_citations(f"a {CLEAN} b") == []
    problems = check_structure(
        MINIMAL_REPORT_FOR_TOKENS.replace("BODY", BRACE), configuration=Configuration.rules_only
    )
    assert any(BRACE in problem for problem in problems)
    assert not [
        problem
        for problem in check_structure(
            MINIMAL_REPORT_FOR_TOKENS.replace("BODY", CLEAN),
            configuration=Configuration.rules_only,
        )
        if "well-formed citations" in problem
    ]


def test_a_table_directive_is_well_formed_in_a_draft_and_not_in_a_report() -> None:
    """The one deliberate difference; flagging it would make the loop unsatisfiable."""
    assert malformed_citations("[[table:calibration.test]]") == []
    assert malformed_citations("[[reg:SR26-2:III.1.a]]") == []


def test_a_section_whose_only_problem_is_a_malformed_citation_is_re_drafted(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """Every claim verifies, so before D-189 the loop had nothing to say and the report died."""
    citation = store.artifact("metrics.test.auc").citation()
    markdown = f"The AUC is 0.7412 {citation}.\nThe VIF screen is described there {BRACE}."
    draft = draft_of(store, markdown)
    assert not draft.failures, "the malformed line carries no number, so it yields no claim"
    assert draft.malformed == [BRACE]
    assert draft.needs_repair
    assert any("not well-formed" in problem for problem in draft.problems)

    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="repair")
    outcome = repair_sections(
        [draft],
        drafter=drafter_returning(
            f"The AUC is 0.7412 {citation}.\nThe VIF screen is described there {CLEAN}."
        ),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
        trace=trace,
    )
    assert outcome.rounds == 1
    assert outcome.drafts[0].malformed == []
    assert CLEAN in outcome.drafts[0].markdown and BRACE not in outcome.drafts[0].markdown
    event = TraceReader(trace.path).events("repair")[0]
    assert event.payload["malformed"] == [BRACE]
    assert event.payload["still_malformed"] == []
    assert event.payload["flagged"] == []


def test_the_round_is_scoped_to_the_malformed_line_and_changes_nothing_else(
    store: ArtifactStore,
) -> None:
    """A malformed citation produces no claim, so without this the scoping sees no line at all."""
    citation = store.artifact("metrics.test.auc").citation()
    previous = f"Untouched line.\nThe AUC is 0.7412 {citation}.\nSee the VIF screen {BRACE}."
    redraft = f"Rewritten elsewhere.\nThe AUC is 0.7412 {citation}.\nSee the VIF screen {CLEAN}."
    scoped = scope_to_flagged_lines(previous, redraft, [], malformed=[BRACE])
    assert scoped.scoped
    assert scoped.lines_redrafted == 1
    assert scoped.markdown.startswith("Untouched line.")
    assert CLEAN in scoped.markdown and BRACE not in scoped.markdown


def test_with_no_malformed_token_the_scoping_is_what_it_was(store: ArtifactStore) -> None:
    """D-109's guarantee is untouched on every section that has no malformed citation."""
    citation = store.artifact("metrics.test.auc").citation()
    previous = f"The AUC is 0.7412 {citation}.\nThe Brier score is 0.68."
    draft = draft_of(store, previous)
    assert draft.failures and not draft.malformed
    redraft = f"The AUC is 0.7412 {citation}.\nThe Brier score is 0.68 {citation}."
    assert scope_to_flagged_lines(previous, redraft, draft.failures) == scope_to_flagged_lines(
        previous, redraft, draft.failures, malformed=[]
    )


def test_a_malformed_citation_the_re_draft_does_not_fix_stops_after_two_rounds(
    store: ArtifactStore,
) -> None:
    """The bound is the same two rounds; a model that will not fix it does not cost a third."""
    citation = store.artifact("metrics.test.auc").citation()
    markdown = f"The AUC is 0.7412 {citation}.\nThe VIF screen is described there {BRACE}."
    outcome = repair_sections(
        [draft_of(store, markdown)],
        drafter=drafter_returning(markdown, markdown, markdown),
        verify=verify_with(store),
        inputs={SECTION: DraftInputs()},
    )
    assert outcome.rounds == 2
    assert outcome.drafts[0].malformed == [BRACE]
