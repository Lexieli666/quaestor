"""The fourth live validation: the first run whose bounded loop did anything.

`eval/results/first-live/credit-attempt4/` is the record of the run of 2026-09-08 that rendered
with the bounded follow-up loop working: 22 model calls, 17 tool calls, 161 post-repair claims,
grounding precision 0.9641 before repair and 1.0000 after, no finding, exit 0. Its own record is
accurate for the first time -- D-093's model id, run-id stamp and input-token sum all hold -- and
what the reading of it found is one tokenizer defect behind all six of its failed claims, and six
prose defects that are all one shape: a section reasoning correctly from a brief that did not carry
the fact its sentence needed. `docs/EVALUATION.md` section 1 writes the run up; this module is the
half of the write-up a machine checks.

Every figure asserted here is re-derived from `trace.jsonl`, `claims.json`, `findings.json`, the
22 cassettes and the artifact index of that directory, so a number that drifts from the run fails
the suite. Nothing here calls a model.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Final

import pytest

from quaestor import TraceReader
from quaestor.artifacts.store import ArtifactStore
from quaestor.corpus import retrieve
from quaestor.report.renderer import _numbers_removed
from quaestor.report.repair import _pair, _skeleton
from quaestor.report.sections import (
    artifact_briefs,
    brief_for,
    follow_up_for,
    monitoring_brief,
    ordered_briefs,
    sections_for_follow_up,
)
from quaestor.tools.guidance import retrieve_per_document
from quaestor.tools.thresholds import SLICE_GAP_BOUND, SLICE_SHARE_FLOOR
from quaestor.trace import EventType, TraceEvent
from quaestor.verifier import ClaimStatus, VerifiedClaim, match_claim
from quaestor.verifier.claim import Claim
from quaestor.verifier.match import Match, written_decimals
from quaestor.verifier.tokens import numeric_tokens, token_value
from quaestor.vocab import ReportSection

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
ATTEMPT: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt4"
"""The committed record of the run this module is about."""

ROW_LEVEL: Final = (
    "run.data_train",
    "run.data_test",
    "run.predictions_train",
    "run.predictions_test",
)
"""The four artifacts whose payload the repository deliberately does not hold (D-087)."""

EXPONENT_LITERALS: Final = {
    "1.92e-05": "ablation.utilisation.delta_auc",
    "-5.589e-05": "ablation.pay_ratio_last.delta_auc",
    "9.982e-06": "csi.bill_mean_6m",
}
"""The three literals whose two halves each are the run's six failed claims (D-099)."""


def _events() -> list[TraceEvent]:
    """Every event of the attempt's trace, in file order."""
    return list(TraceReader(ATTEMPT / "trace.jsonl"))


def _of(kind: EventType) -> list[TraceEvent]:
    """The attempt's events of one type."""
    return [event for event in _events() if event.type is kind]


def _report() -> str:
    """The attempt's rendered report, as committed."""
    return (ATTEMPT / "report.md").read_text(encoding="utf-8")


def _claims() -> dict[str, Any]:
    """The attempt's `claims.json`."""
    return dict(json.loads((ATTEMPT / "claims.json").read_text(encoding="utf-8")))


def _index() -> dict[str, Any]:
    """The attempt's artifact index: every logical name the run stored."""
    payload = json.loads((ATTEMPT / "artifacts" / "index.json").read_text(encoding="utf-8"))
    return dict(payload["artifacts"])


def _store() -> ArtifactStore:
    """The attempt's own artifact store, which every figure below is read against."""
    return ArtifactStore(ATTEMPT / "artifacts")


def _cassettes() -> list[dict[str, Any]]:
    """The attempt's 22 tapes, in file-name order."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ATTEMPT / "cassettes").glob("*.json"))
    ]


# --- what the run did -------------------------------------------------------------------------


def test_the_trace_is_the_run_the_evaluation_describes() -> None:
    """307 events, 22 model calls, 17 tool calls, 4 plan steps, 2 repair rounds."""
    counts = Counter(event.type for event in _events())
    assert sum(counts.values()) == 307
    assert counts[EventType.llm_call] == 22
    assert counts[EventType.tool_call] == 17
    assert counts[EventType.plan_step] == 4
    assert counts[EventType.repair] == 2
    assert counts[EventType.claim_check] == 262


def test_twenty_two_model_calls_are_four_plans_nine_drafts_and_nine_extractions() -> None:
    """Seven sections drafted and extracted, plus two repair re-drafts and their re-extractions."""
    calls = _of(EventType.llm_call)
    assert Counter(str(event.payload["purpose"]) for event in calls) == {
        "draft": 9,
        "extract": 9,
        "plan": 4,
    }
    repairs = [event for event in calls if event.payload.get("repair")]
    assert [str(event.payload["section"]) for event in repairs] == [
        "conceptual_soundness",
        "data_integrity",
    ]
    assert {str(event.payload["model"]) for event in calls} == {"claude-opus-5[1m]"}


def test_the_loop_ran_four_steps_and_the_first_named_a_column_that_does_not_exist() -> None:
    """D-107: `credit_limit` cost a model call and a tool call; the column is `limit_bal`."""
    steps = _of(EventType.plan_step)
    assert [bool(event.payload["accepted"]) for event in steps] == [True] * 4
    assert [bool(event.payload["executed"]) for event in steps] == [False, True, True, True]
    first = steps[0].payload
    assert first["args"]["subpopulation"]["column"] == "credit_limit"
    assert "has no column 'credit_limit'" in str(first["error"])
    assert "'limit_bal'" in str(first["error"])
    assert [step.payload["args"]["subpopulation"]["column"] for step in steps[1:]] == [
        "limit_bal",
        "limit_bal",
        "delinq_count_6m",
    ]


def test_seventeen_tool_calls_are_the_plan_s_thirteen_and_the_loop_s_four() -> None:
    """One of the five `compute_metrics` calls raised, and no check raised a candidate."""
    tools = _of(EventType.tool_call)
    assert Counter(str(event.payload["tool"]) for event in tools) == {
        "retrieve_guidance": 7,
        "compute_metrics": 5,
        "run_model": 1,
        "profile_data": 1,
        "check_leakage": 1,
        "check_collinearity": 1,
        "challenger_compare": 1,
    }
    assert Counter(bool(event.payload["ok"]) for event in tools) == {True: 16, False: 1}
    assert [event.payload["candidates"] for event in tools if event.payload["candidates"]] == []
    assert sum(float(event.payload["duration_s"]) for event in tools) == pytest.approx(
        3.16, abs=5e-3
    )


def test_the_claims_are_the_figures_the_front_matter_prints() -> None:
    """161 post-repair claims, 0.9641 -> 1.0000, and no finding at any severity."""
    claims = _claims()
    assert claims["grounding"]["pre_repair"]["precision"] == 0.9641
    assert claims["grounding"]["pre_repair"]["n_claims"] == 167
    assert claims["grounding"]["post_repair"]["precision"] == 1.0
    assert claims["grounding"]["post_repair"]["n_claims"] == 161
    assert json.loads((ATTEMPT / "findings.json").read_text(encoding="utf-8"))["findings"] == []
    statuses = Counter(str(event.payload["status"]) for event in _of(EventType.claim_check))
    assert statuses == {"verified": 256, "unattributed": 6}


def test_the_bill_is_what_the_evaluation_quotes() -> None:
    """77,808 output tokens, $4.1603, 908.59 s from the first traced event to the last."""
    calls = _of(EventType.llm_call)
    assert sum(int(event.payload["tokens_out"]) for event in calls) == 77_808
    assert sum(float(event.payload["cost_usd"]) for event in calls) == pytest.approx(
        4.1603, abs=5e-5
    )
    by_purpose = Counter()
    for event in calls:
        by_purpose[str(event.payload["purpose"])] += int(event.payload["tokens_out"])
    assert dict(by_purpose) == {"plan": 1_357, "draft": 31_221, "extract": 45_230}
    events = _events()
    assert (events[-1].ts - events[0].ts).total_seconds() == pytest.approx(908.59, abs=0.01)


def test_the_input_token_count_finally_agrees_with_the_cassettes() -> None:
    """D-093's three-field sum, checked against the tapes rather than asserted (attempt 3: 38)."""
    recorded = sum(int(event.payload["tokens_in"]) for event in _of(EventType.llm_call))
    assert recorded == 219_975
    tapes = _cassettes()
    assert len(tapes) == 22
    assert sum(int(tape["completion"]["tokens_in"]) for tape in tapes) == recorded


def test_the_run_id_carries_its_own_second_and_the_front_matter_names_the_model() -> None:
    """The two halves of D-093 that this run is the first to demonstrate holding."""
    report = _report()
    assert "run_id: credit_default-full_agent-20260908T090332Z-d03b07c6" in report
    assert "model: claude-opus-5[1m]" in report
    assert "model: claude-cli" not in report


# --- one defect, six claims (D-099) -------------------------------------------------------------


def test_all_six_failed_claims_are_the_two_halves_of_three_exponent_literals() -> None:
    """1.92 and 5, -5.589 and 5, 9.982 and 6: three literals, six `unattributed` claims."""
    failed = [claim for claim in _claims()["pre_repair"] if claim["status"] != "verified"]
    assert [claim["value"] for claim in failed] == [1.92, 5.0, -5.589, 5.0, 9.982, 6.0]
    assert {claim["status"] for claim in failed} == {"unattributed"}
    for claim in failed:
        assert any(literal in str(claim["text"]) for literal in EXPONENT_LITERALS), claim["text"]


def test_the_tokenizer_of_the_day_split_each_literal_into_a_mantissa_and_an_exponent() -> None:
    """The cause, reconstructed from the run's own sentences under the old expression."""
    import re

    old = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?%?")
    assert [match.group(0) for match in old.finditer("by 1.92e-05 and")] == ["1.92", "05"]
    assert [match.group(0) for match in old.finditer("by -5.589e-05 and")] == ["-5.589", "05"]
    assert [match.group(0) for match in old.finditer("9.982e-06 ")] == ["9.982", "06"]
    for literal in EXPONENT_LITERALS:
        assert [token for _, token in numeric_tokens(f"{literal} ")] == [literal]


def test_on_this_build_each_literal_is_one_token_that_verifies_against_its_artifact() -> None:
    """The same three sentences, the same three artifacts, and no failed claim left (D-099)."""
    store = _store()
    for literal, name in EXPONENT_LITERALS.items():
        tokens = [token for _, token in numeric_tokens(f"the delta is {literal} on test")]
        assert tokens == [literal], literal
        text = f"the delta is {literal} {store.artifact(name).citation()} on test"
        claim = Claim(
            text=text,
            value=token_value(literal),
            citation=store.artifact(name).citation(),
            section=ReportSection.conceptual_soundness,
        )
        match = match_claim(claim, store)
        assert match.status is ClaimStatus.verified, (literal, match.message)


def test_the_exponent_moves_the_tolerance_rather_than_widening_it() -> None:
    """`1.920e-05` claims 10^-8, so a value one order away still does not verify (D-099)."""
    store = _store()
    assert written_decimals(1.92e-05, "the delta is 1.920e-05 on test") == 8
    citation = store.artifact("ablation.utilisation.delta_auc").citation()
    wrong = Claim(
        text=f"the delta is 1.92e-04 {citation} on test",
        value=1.92e-04,
        citation=citation,
        section=ReportSection.conceptual_soundness,
    )
    assert match_claim(wrong, store).status is ClaimStatus.mismatch


def test_attempt_three_s_two_removals_were_the_same_defect_a_run_earlier() -> None:
    """`9.982` and `6` of attempt 3: one literal, recorded there as two extraction misses."""
    third = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt3"
    rounds = [
        event
        for event in TraceReader(third / "trace.jsonl")
        if event.type is EventType.repair and event.payload["section"] == "data_integrity"
    ]
    assert [list(event.payload["removed"]) for event in rounds] == [[9.982, 6.0]]
    claims = json.loads((third / "claims.json").read_text(encoding="utf-8"))
    lines = {str(claim["text"]) for claim in claims["pre_repair"] if claim["status"] != "verified"}
    assert any("9.982e-06" in line for line in lines), (
        "attempt 3's two failures were one literal, and its entry called them two omissions"
    )


# --- the section the loop's work never reached (D-101, D-102) ----------------------------------


def test_the_loop_computed_a_segment_the_report_never_mentions() -> None:
    """AUC 0.5875 and Gini 0.1749 on 6,048 of 9,000 test rows, and not a word about it."""
    store = _store()
    assert store.value("metrics.test.sub.delinq_count_6m_eq_0.n") == 6048
    assert store.value("metrics.test.n") == 9000
    assert store.value("metrics.test.sub.delinq_count_6m_eq_0.auc") == pytest.approx(
        0.5875, abs=5e-5
    )
    assert store.value("metrics.test.sub.delinq_count_6m_eq_0.gini") == pytest.approx(
        0.1749, abs=5e-5
    )
    assert store.value("metrics.test.auc") == pytest.approx(0.7550, abs=5e-5)
    report = _report()
    assert "delinq_count_6m_eq_0" not in report
    assert "0.5875" not in report and "0.587" not in report


def test_the_twenty_four_slice_scalars_were_all_selected_for_section_four() -> None:
    """The drafter was shown every one of them: the brief did not ask, so it wrote none."""
    index = _index()
    slices = [name for name in index if ".sub." in name]
    assert len(slices) == 24
    shown = {item.name for item in artifact_briefs(_store(), brief_for(ReportSection.outcomes))}
    assert set(slices) <= shown


def test_the_step_s_own_reason_is_in_the_trace_and_was_in_no_prompt() -> None:
    """The half D-101 restores: `PlannedCall.why` never reached the drafter."""
    steps = _of(EventType.plan_step)
    assert "never-delinquent majority segment" in str(steps[3].payload["why"])
    for tape in _cassettes():
        assert "never-delinquent majority segment" not in tape["request"]["prompt"]


def test_on_this_build_the_segment_is_an_open_item_and_the_halves_are_not() -> None:
    """The run's own three slices against D-102's two bounds, at their shipped values."""
    store = _store()
    segment = "metrics.test.sub.delinq_count_6m_eq_0.auc"
    gap = store.value("metrics.test.auc") - store.value(segment)
    assert gap == pytest.approx(0.1676, abs=5e-5)
    share = store.value("metrics.test.sub.delinq_count_6m_eq_0.n") / store.value("metrics.test.n")
    assert share == pytest.approx(0.672, abs=5e-4)
    for slug, want, expected_gap in (
        ("delinq_count_6m_eq_0", True, 0.1676),
        ("limit_bal_high", False, 0.0436),
        ("limit_bal_low", False, 0.0073),
    ):
        stem = f"metrics.test.sub.{slug}"
        measured = store.value("metrics.test.auc") - store.value(f"{stem}.auc")
        assert measured == pytest.approx(expected_gap, abs=5e-5), slug
        follow_up = _follow_up_of(stem, measured, store.value(f"{stem}.n") / 9000.0)
        assert follow_up.material is want, slug


def _follow_up_of(stem: str, gap: float, share: float) -> Any:
    """Build the follow-up D-102 would produce for one of the run's slices, on this build."""
    import tempfile

    from quaestor.artifacts import ArtifactKind

    store = ArtifactStore(Path(tempfile.mkdtemp()) / "artifacts")
    store.put(SLICE_GAP_BOUND, 0.08, ArtifactKind.scalar, "the slice gap bound")
    store.put(SLICE_SHARE_FLOOR, 0.10, ArtifactKind.scalar, "the slice size floor")
    store.put(f"{stem}.auc_gap", gap, ArtifactKind.scalar, "the gap")
    store.put(f"{stem}.share", share, ArtifactKind.scalar, "the share")
    return follow_up_for(store, "compute_metrics", {}, "why", sorted(store.names()))


def test_on_this_build_section_four_is_the_section_asked_to_report_the_step() -> None:
    """Section 1's selector matches the slice scalars too and is excluded by the rule (D-101)."""
    store = _store()
    follow_up = follow_up_for(
        store,
        "compute_metrics",
        {"splits": ["test"]},
        "why",
        [name for name in _index() if ".sub." in name],
    )
    sections = sections_for_follow_up(ordered_briefs(store), follow_up)
    assert sections == [ReportSection.outcomes]
    assert brief_for(ReportSection.summary).matches("metrics.test.sub.limit_bal_low.auc")


# --- the four prose defects, quoted from the committed report ----------------------------------


def test_section_seven_said_a_number_three_other_sections_cited_was_not_carried() -> None:
    """D-100, and the selector that made it possible, read off the attempt's own index."""
    report = _report()
    assert "no recomputed test Brier value is carried in this report's artifact store" in report
    assert "metrics.test.brier" in _index()
    assert "[[art:86e93c8f:metrics.test.brier]]" in report, "sections 1, 2 and 4 did cite it"
    brief = brief_for(ReportSection.monitoring)
    assert not brief.matches("metrics.test.brier")
    assert "metrics.test.brier" in {item.name for item in artifact_briefs(_store(), brief)}


def test_section_six_enumerated_reviews_appendix_d_says_did_not_happen() -> None:
    """D-103: "input data lineage" and "documentation of intended use" on a package with no docs."""
    report = _report()
    assert "The validation instead reviewed input data lineage and quality" in report
    assert "the documentation of intended use and known limitations" in report
    assert "| developer documentation | package has no `docs/` directory |" in report
    assert "Checks that ran and raised no candidate:" in report
    brief = brief_for(ReportSection.findings)
    assert "Do **not** describe what\nwas reviewed" in brief.brief


def test_section_seven_said_the_report_led_with_calibration_and_section_four_did_not() -> None:
    """D-104, both sentences quoted from the same committed report."""
    report = _report()
    assert "This section reports discrimination first and calibration second." in report
    assert (
        "the monitoring report should order calibration evidence ahead of discrimination "
        "evidence, as this report does" in report
    )
    from quaestor.report.sections import OrderReason, SectionOrder

    told = monitoring_brief(
        brief_for(ReportSection.monitoring), SectionOrder(False, OrderReason.event_rate)
    ).brief
    assert "**discrimination before calibration**" in told
    assert "do **not** write that this report led with" in told


def test_the_prose_reads_zero_point_zero_features(tmp_path: Path) -> None:
    """D-106: an integral count reached the drafter as `0.0`, and the sentence copied it."""
    assert "The timing screen flags 0.0 " in _report()
    brief = brief_for(ReportSection.data_integrity)
    payloads = {item.name: item.to_payload() for item in artifact_briefs(_store(), brief)}
    assert payloads["leakage.timing.n_flagged"]["value"] == 0
    assert isinstance(payloads["leakage.timing.n_flagged"]["value"], int)


# --- Appendix A's arithmetic (D-105) -----------------------------------------------------------


def test_the_appendix_reported_one_rewrite_of_a_round_that_rewrote_nothing() -> None:
    """1 rewritten / 5 removed against a truth of 0 / 6, and the false row that produced it."""
    report = _report()
    assert "after 1 claim(s) rewritten and 5 number(s) removed from the prose" in report
    repairs = _claims()["repairs"]
    assert len(repairs) == 1
    assert repairs[0]["before"]["value"] == 1.92
    assert repairs[0]["after"]["value"] == 2.0
    rounds = _of(EventType.repair)
    assert [list(event.payload["removed"]) for event in rounds] == [
        [5.0, -5.589, 5.0],
        [9.982, 6.0],
    ]
    assert _numbers_removed(_events()) == 5
    assert sum(len(event.payload["flagged"]) for event in rounds) == 6


def test_on_this_build_that_pairing_is_refused_and_the_number_counts_as_removed() -> None:
    """The two sentences the fallback joined, and the two grounds neither of them meets (D-105)."""
    before_text, after_text = _the_two_sentences()
    assert _skeleton(before_text) != _skeleton(after_text)
    before = Match(
        claim=VerifiedClaim(
            text=before_text,
            value=1.92,
            section=ReportSection.conceptual_soundness,
            status=ClaimStatus.unattributed,
        )
    )
    after = Match(
        claim=VerifiedClaim(
            text=after_text,
            value=2.0,
            citation="[[art:792cb79c:run.features#at_origination]]",
            section=ReportSection.conceptual_soundness,
            status=ClaimStatus.verified,
        )
    )
    assert abs(after.claim.value - before.claim.value) / before.claim.value < 0.1
    assert _pair(before, [after], set()) is None


def _the_two_sentences() -> tuple[str, str]:
    """The flagged claim's line and the verified line it was paired with, from `claims.json`."""
    claims = _claims()
    before = next(
        claim["text"] for claim in claims["pre_repair"] if claim["id"] == "60a89495d068e44f"
    )
    after = next(
        claim["text"]
        for claim in claims["post_repair"]
        if claim["value"] == 2.0 and claim["section"] == "conceptual_soundness"
    )
    return str(before), str(after)


# --- the guidance the retrieval never offered (D-108) ------------------------------------------


def test_two_of_the_run_s_retrievals_held_no_span_of_the_current_guidance() -> None:
    """The defect: sections 3 and 5 could only open on text superseded in April 2026."""
    store = _store()
    retrieved: dict[str, list[tuple[str, str]]] = {}
    for name in _index():
        if not name.startswith("guidance."):
            continue
        payload = store.load(name)
        retrieved[str(payload["query"])] = [
            (str(span["doc"]), str(span["section_id"])) for span in payload["spans"]
        ]
    for query in (
        "data quality accuracy completeness and representativeness",
        "sensitivity analysis stability benchmarking alternative models",
    ):
        assert {doc for doc, _ in retrieved[query]} == {"SR11-7"}, query
        assert [span.doc for span in retrieve(query, 3, None)] == ["SR11-7"] * 3, query


def test_on_this_build_both_queries_offer_the_revision_and_the_superseded_text() -> None:
    """D-108: `k` per document, the revision first, and the choice left to the drafter."""
    for query, wanted in (
        ("data quality accuracy completeness and representativeness", "IV.1"),
        ("sensitivity analysis stability benchmarking alternative models", "V.1.a"),
    ):
        spans = retrieve_per_document(query, 3, None)
        assert [span.doc for span in spans] == ["SR26-2"] * 3 + ["SR11-7"] * 3, query
        assert wanted in {span.section_id for span in spans if span.doc == "SR26-2"}, query


# --- what is committed, and what is not (D-087) ------------------------------------------------


def test_the_row_level_artifacts_are_listed_and_their_payloads_are_not_here() -> None:
    """The index is the run's inventory; the four largest payloads are deliberately absent."""
    index = _index()
    assert len(index) == 192
    for name in ROW_LEVEL:
        assert name in index, name
        assert not (ATTEMPT / "artifacts" / f"{index[name]['hash']}.csv").exists()


def test_no_committed_file_of_the_attempt_is_row_sized() -> None:
    """`find eval/results/first-live/credit-attempt4 -size +20k` over the CSVs, as D-087 asks."""
    big = [path for path in ATTEMPT.rglob("*.csv") if path.stat().st_size > 20 * 1024]
    assert big == [], f"row-level files are committed: {big}"
