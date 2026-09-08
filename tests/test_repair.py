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
from quaestor.report.drafter import Drafter
from quaestor.report.repair import (
    MAX_REPAIR_ROUNDS,
    UNVERIFIED_OPEN,
    DraftInputs,
    SectionDraft,
    is_wrapped,
    repair_sections,
    wrap_unverified,
    wrapped_values,
)
from quaestor.report.sections import brief_for
from quaestor.trace import TraceReader, TraceWriter
from quaestor.verifier import ClaimStatus, extract, match_claims
from quaestor.vocab import ReportSection
from reportsupport import SectionFake

SECTION = ReportSection.outcomes


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
