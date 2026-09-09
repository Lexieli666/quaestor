"""The sixth live validation: the run the README excerpts, and the degenerate slice it exposed.

`eval/results/first-live/credit/` is the record of the run of 2026-09-09 that rendered on
`fc33dd7`, the build carrying D-084 to D-119: 18 model calls, 17 tool calls, 210 claims, grounding
precision **1.0000 before repair and after it**, no repair round, no finding, no open item, exit 0,
$3.9739, 872.74 s. It carries no `attempt` suffix because it is the run the README excerpts, and
`report.md` is committed as produced and is never edited (DECISIONS D-120).

Two things in it are worth a test. The first is what did *not* happen: this is the first live run
whose verifier flagged nothing, so D-109's scoped re-draft path has still not been exercised live
and the pre- and post-repair claim sets are one document. The second is the defect reading found:
the bounded loop's third step asked for `delinq_count_6m above_median` on a column whose median is
its minimum, `>= median` selected every row of both splits, and the tool answered -- share 1, an
AUC gap of 0, and a paragraph of section 4 reporting the split to itself. The drafter described it
honestly and that paragraph stays in the committed report; what changed is that the same call is
refused now (D-121, D-122).

Every figure asserted here is re-derived from `trace.jsonl`, `claims.json`, `findings.json`, the 18
cassettes and the artifact index of that directory, so a number that drifts from the run fails the
suite. Nothing here calls a model.
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any, Final

import pandas as pd
import pytest

from quaestor import TraceReader
from quaestor.artifacts.store import ArtifactStore
from quaestor.tools.metrics import ComputeMetricsTool, Subpopulation, subpopulation_expression
from quaestor.tools.thresholds import (
    SLICE_GAP_BOUND,
    SLICE_SHARE_CEILING,
    SLICE_SHARE_FLOOR,
    Thresholds,
)
from quaestor.trace import EventType, TraceEvent
from quaestor.verifier.tokens import eligible_numbers

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
RUN: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit"
"""The committed record of the run this module is about."""

SLICES: Final = (
    ("limit_bal", "below_median", "limit_bal_low"),
    ("limit_bal", "above_median", "limit_bal_high"),
    ("delinq_count_6m", "above_median", "delinq_count_6m_high"),
    ("utilisation", "above_median", "utilisation_high"),
)
"""The four sub-populations the bounded loop asked for, in the order it asked."""

DEGENERATE: Final = "delinq_count_6m_high"
"""The third step's slug: the rule that selected the whole of both splits (D-121)."""

EXCERPT_EDITS: Final = (
    (
        "but refitting without the term costs -5.589e-05 "
        "[[art:e26d8112:ablation.pay_ratio_last.delta_auc]] of test AUC",
        "but refitting without the term changes test AUC by -5.589e-05 "
        "[[art:e26d8112:ablation.pay_ratio_last.delta_auc]]",
    ),
    (
        "refitting without the term costs -0.001393 "
        "[[art:99f9dd71:ablation.bill_trend_6m.delta_auc]] of test AUC",
        "refitting without the term changes test AUC by -0.001393 "
        "[[art:99f9dd71:ablation.bill_trend_6m.delta_auc]]",
    ),
    (
        "the sign reversal reflects the credit limit and billing terms absorbing",
        "the sign reversal is consistent with the credit limit and billing terms absorbing",
    ),
    (
        "the bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] the package sets for it",
        "the bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] rule O1 sets for it",
    ),
    (
        "so the fit does not depend on the sample the model was estimated on",
        "so there is no sign of overfitting to the estimation sample",
    ),
    (
        "and -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]] below it on train",
        "and by -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]] on train, that "
        "is, marginally above it",
    ),
)
"""D-120's five wording edits as `(before, after)`, with the citations the report actually carries.

Five edits and six pairs: the first edit is two sentences of the same shape. Each `before` is
asserted below to be in `report.md` exactly once, so the DECISIONS entry Phase 16 copies from
cannot drift from the file it quotes. No `after` changes a number, and none of them is applied
here: the record is the record.
"""


def _events() -> list[TraceEvent]:
    """Every event of the run's trace, in file order."""
    return list(TraceReader(RUN / "trace.jsonl"))


def _of(kind: EventType) -> list[TraceEvent]:
    """The run's events of one type."""
    return [event for event in _events() if event.type is kind]


def _report() -> str:
    """The run's rendered report, as committed."""
    return (RUN / "report.md").read_text(encoding="utf-8")


def _claims() -> dict[str, Any]:
    """The run's `claims.json`."""
    return dict(json.loads((RUN / "claims.json").read_text(encoding="utf-8")))


def _store() -> ArtifactStore:
    """The run's own artifact store, which every figure below is read against."""
    return ArtifactStore(RUN / "artifacts")


def _index() -> dict[str, Any]:
    """The run's artifact index: every logical name it stored."""
    payload = json.loads((RUN / "artifacts" / "index.json").read_text(encoding="utf-8"))
    return dict(payload["artifacts"])


def _cassettes() -> list[dict[str, Any]]:
    """The run's 18 tapes, in file-name order."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((RUN / "cassettes").glob("*.json"))
    ]


# --- what the run did ---------------------------------------------------------------------------


def test_the_trace_is_the_run_the_evaluation_describes() -> None:
    """249 events, 18 model calls, 17 tool calls, 4 plan steps, no repair, 210 checks."""
    counts = Counter(event.type for event in _events())
    assert sum(counts.values()) == 249
    assert counts[EventType.llm_call] == 18
    assert counts[EventType.tool_call] == 17
    assert counts[EventType.plan_step] == 4
    assert counts[EventType.repair] == 0
    assert counts[EventType.claim_check] == 210


def test_eighteen_model_calls_are_four_plans_seven_drafts_and_seven_extractions() -> None:
    """Seven sections drafted and extracted once each, and no re-ask on any of the eighteen."""
    calls = _of(EventType.llm_call)
    assert Counter(str(event.payload["purpose"]) for event in calls) == {
        "draft": 7,
        "extract": 7,
        "plan": 4,
    }
    assert [event for event in calls if event.payload.get("repair")] == []
    assert {int(event.payload["attempt"]) for event in calls} == {1}, "no re-ask"
    assert {str(event.payload["model"]) for event in calls} == {"claude-opus-5[1m]"}
    assert "| LLM calls | 18 (plan 4, draft 7, extract 7) |" in _report()


def test_the_loop_ran_four_steps_and_every_one_of_them_executed() -> None:
    """The four slices, in the order the loop asked for them."""
    steps = _of(EventType.plan_step)
    assert [bool(event.payload["accepted"]) for event in steps] == [True] * 4
    assert [bool(event.payload["executed"]) for event in steps] == [True] * 4
    assert [str(event.payload["error"]) for event in steps] == [""] * 4
    asked = [dict(event.payload["args"]["subpopulation"]) for event in steps]
    assert [(item["column"], item["rule"]) for item in asked] == [
        (column, rule) for column, rule, _ in SLICES
    ]


def test_seventeen_tool_calls_and_not_one_of_them_raised() -> None:
    """Thirteen from the rule-based plan and four from the loop; no check raised a candidate."""
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
    assert Counter(bool(event.payload["ok"]) for event in tools) == {True: 17}
    assert [event.payload["candidates"] for event in tools if event.payload["candidates"]] == []
    assert sum(float(event.payload["duration_s"]) for event in tools) == pytest.approx(
        3.76, abs=5e-3
    )
    assert len(_index()) == 258


def test_the_claims_are_the_figures_the_front_matter_prints() -> None:
    """210 claims at 1.0000 before repair and 1.0000 after, and no finding at any severity."""
    claims = _claims()
    for stage in ("pre_repair", "post_repair"):
        grounding = claims["grounding"][stage]
        assert (grounding["precision"], grounding["n_claims"]) == (1.0, 210)
        assert grounding["status_counts"] == {
            "verified": 210,
            "mismatch": 0,
            "unsupported": 0,
            "dangling": 0,
            "unattributed": 0,
        }
    assert json.loads((RUN / "findings.json").read_text(encoding="utf-8"))["findings"] == []
    statuses = Counter(str(event.payload["status"]) for event in _of(EventType.claim_check))
    assert statuses == {"verified": 210}
    report = _report()
    assert "grounding_precision_pre: 1.0000" in report
    assert "grounding_precision_post: 1.0000" in report
    assert "n_claims: 210" in report
    assert "n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}" in report


def test_no_repair_round_fired_so_the_two_claim_sets_are_one_document() -> None:
    """The first live run with nothing to repair, which is why D-109 is still untested live."""
    claims = _claims()
    assert claims["pre_repair"] == claims["post_repair"]
    assert claims["repairs"] == []
    assert _of(EventType.repair) == []
    report = _report()
    assert "| repair rounds | 0 |" in report
    assert "| re-asks | 0 |" in report
    appendix = report.split("## Appendix A", 1)[1].split("## Appendix B", 1)[0]
    assert "1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose" in appendix
    assert "| repair | " not in appendix, "no repair row in the claims table"


def test_the_report_raises_no_open_item_and_says_so() -> None:
    """Every declared bound passed and every slice was inside D-102's, so section 6 asks nothing."""
    report = _report()
    findings = report.split("## 6. Findings", 1)[1].split("## 7.", 1)[0]
    assert "This validation raised no finding." in findings
    section = findings.split("### Open items", 1)[1]
    assert "recorded no observation of this kind" in section
    assert "owner: model developer" not in section
    store = _store()
    bound = store.value(SLICE_GAP_BOUND)
    floor = store.value(SLICE_SHARE_FLOOR)
    assert (bound, floor) == (0.08, 0.10)
    material = [
        slug
        for _, _, slug in SLICES
        if store.value(f"metrics.test.sub.{slug}.auc_gap") > bound
        and store.value(f"metrics.test.sub.{slug}.share") >= floor
    ]
    assert material == [], "no slice of this run is materially worse than its split"


def test_the_bill_is_what_the_evaluation_quotes() -> None:
    """74,618 output tokens, $3.9739, 872.74 s from the first traced event to the last."""
    calls = _of(EventType.llm_call)
    assert sum(int(event.payload["tokens_out"]) for event in calls) == 74_618
    assert sum(float(event.payload["cost_usd"]) for event in calls) == pytest.approx(
        3.9739, abs=5e-5
    )
    out: Counter[str] = Counter()
    cost: Counter[str] = Counter()
    for event in calls:
        purpose = str(event.payload["purpose"])
        out[purpose] += int(event.payload["tokens_out"])
        cost[purpose] += float(event.payload["cost_usd"])
    assert dict(out) == {"plan": 1_331, "draft": 30_549, "extract": 42_738}
    assert cost["extract"] == pytest.approx(1.6208, abs=5e-5)
    assert cost["draft"] == pytest.approx(2.0168, abs=5e-5)
    assert cost["plan"] == pytest.approx(0.3364, abs=5e-5)
    events = _events()
    assert (events[-1].ts - events[0].ts).total_seconds() == pytest.approx(872.74, abs=0.01)
    report = _report()
    assert "| notional cost (USD) | 3.9739 |" in report
    assert "| wall-clock (s) | 872.74 |" in report


def test_the_input_token_count_agrees_with_the_cassettes() -> None:
    """D-093's three-field sum, checked against the tapes rather than asserted."""
    tapes = _cassettes()
    assert len(tapes) == 18
    total = 0
    for tape in tapes:
        completion = tape["completion"]
        payload = ast.literal_eval(completion) if isinstance(completion, str) else completion
        usage = dict(payload["raw"]["usage"])
        total += (
            int(usage.get("input_tokens", 0))
            + int(usage.get("cache_creation_input_tokens", 0))
            + int(usage.get("cache_read_input_tokens", 0))
        )
    assert total == 207_429
    assert sum(int(event.payload["tokens_in"]) for event in _of(EventType.llm_call)) == total
    assert "| tokens in / out | 207,429 / 74,618 |" in _report()


def test_extraction_output_per_claim_check_is_the_figure_the_table_prints() -> None:
    """204 per check, the fifth reading of a series that is still n = 1 at every point."""
    extraction = sum(
        int(event.payload["tokens_out"])
        for event in _of(EventType.llm_call)
        if str(event.payload["purpose"]) == "extract"
    )
    checks = len(_of(EventType.claim_check))
    assert (extraction, checks) == (42_738, 210)
    assert round(extraction / checks) == 204


def test_d_115_is_measured_against_the_fifth_run_at_the_same_four_slices() -> None:
    """Four executed slices in both runs, 210 claims against 285 and $3.97 against $6.05.

    The comparison is not a controlled one and the entry in `docs/EVALUATION.md` says so: the two
    runs sliced different columns, wrote different prose and made a different number of drafting
    calls. What it does establish is that the table form did not cost the report its numbers --
    every one of the 210 verified -- while removing the family of claims that was 72 of the fifth
    run's 285.
    """
    fifth = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt5"
    before = list(TraceReader(fifth / "trace.jsonl"))
    executed = [
        event
        for event in before
        if event.type is EventType.plan_step and event.payload["executed"] is True
    ]
    assert len(executed) == 4
    assert len([event for event in _of(EventType.plan_step) if event.payload["executed"]]) == 4
    fifth_claims = json.loads((fifth / "claims.json").read_text(encoding="utf-8"))
    assert fifth_claims["grounding"]["post_repair"]["n_claims"] == 285
    assert _claims()["grounding"]["post_repair"]["n_claims"] == 210
    fifth_cost = sum(
        float(event.payload["cost_usd"]) for event in before if event.type is EventType.llm_call
    )
    assert fifth_cost == pytest.approx(6.0535, abs=5e-5)
    assert sum(
        float(event.payload["cost_usd"]) for event in _of(EventType.llm_call)
    ) == pytest.approx(3.9739, abs=5e-5)


# --- the degenerate slice: what the run did, and what the build does now -------------------------


def test_the_third_step_s_rule_selected_the_whole_of_both_splits() -> None:
    """The defect, from the run's own artifacts: share 1, an AUC gap of 0, n equal to the split."""
    store = _store()
    for split, rows in (("train", 21_000), ("test", 9_000)):
        assert store.value(f"metrics.{split}.sub.{DEGENERATE}.share") == 1.0
        assert store.value(f"metrics.{split}.sub.{DEGENERATE}.n") == rows
        assert store.value(f"metrics.{split}.n") == rows
        assert store.value(f"metrics.{split}.sub.{DEGENERATE}.auc_gap") == 0.0
        assert store.value(f"metrics.{split}.sub.{DEGENERATE}.auc") == store.value(
            f"metrics.{split}.auc"
        )
    assert [name for name in _index() if DEGENERATE in name] != []
    assert len([name for name in _index() if DEGENERATE in name]) == 22


def test_the_step_cost_one_of_four_and_the_tool_answered_it() -> None:
    """It was a step of the budget, not a refusal: the trace records it executed and ok."""
    steps = _of(EventType.plan_step)
    third = steps[2]
    assert dict(third.payload["args"]["subpopulation"]) == {
        "column": "delinq_count_6m",
        "rule": "above_median",
    }
    assert third.payload["executed"] is True
    assert third.payload["error"] == ""
    assert "risk-concentrated delinquency slice" in str(third.payload["why"])
    follow_ups = [
        event
        for event in _of(EventType.tool_call)
        if str(event.payload["tool"]) == "compute_metrics"
    ][1:]
    assert len(follow_ups) == 4
    assert [len(event.payload["artifacts"]) for event in follow_ups] == [63] * 4
    assert all(bool(event.payload["ok"]) for event in follow_ups)


def test_the_drafter_described_the_degenerate_slice_honestly_and_that_prose_stays() -> None:
    """Why this is a tool defect and not a drafting one, asserted on the committed sentences.

    The paragraph says the rule selected the whole of each split, why that reproduces the
    split-wide numbers, and that the step carries no information about the population it was asked
    about. It is not edited -- not now and not for the README excerpt (D-120) -- because the report
    is the record of what the pipeline produced.
    """
    report = _report()
    prose = report.split("### Follow-up analyses", 1)[1].split("## 5.", 1)[0]
    paragraph = [line for line in prose.splitlines() if f"sub.{DEGENERATE}.share" in line]
    assert len(paragraph) == 1
    assert "selected the whole of each split rather than a proper subset" in paragraph[0]
    assert "which is why it reproduces the split-wide numbers" in paragraph[0]
    assert any(
        "carries no information about the delinquency-concentrated population" in line
        for line in report.splitlines()
    )


def test_the_same_column_now_partitions_instead_of_degenerating() -> None:
    """D-122 against the run's own shape, on a count whose median is its minimum.

    `delinq_count_6m` on the real sample has a median of 0. Under the build the run was made on,
    `above_median` resolved to `>= 0` and selected every row while `below_median` selected none;
    under this one the median's rows are the lower half, so the never-delinquent segment is
    reachable and the two rules partition the split. The share ceiling that would have refused the
    run's step is D-121's, and it is a stored threshold rather than an exact 1.0.
    """
    frame = pd.DataFrame({"delinq_count_6m": [0] * 60 + [1] * 25 + [2] * 10 + [3] * 5})
    masks = {
        rule: ComputeMetricsTool._mask(frame, Subpopulation(column="delinq_count_6m", rule=rule))
        for rule in ("below_median", "above_median")
    }
    assert int(masks["below_median"].sum()) == 60, "the never-delinquent segment, now reachable"
    assert int(masks["above_median"].sum()) == 40
    assert int((masks["below_median"] & masks["above_median"]).sum()) == 0
    assert int((masks["below_median"] | masks["above_median"]).sum()) == len(frame)
    assert subpopulation_expression("delinq_count_6m", "above_median") == (
        "delinq_count_6m > median(delinq_count_6m)"
    )
    assert Thresholds()[SLICE_SHARE_CEILING] == 0.95
    assert Thresholds()[SLICE_SHARE_CEILING] < 1.0, "a ceiling, not exact degeneracy (D-121)"


def test_the_never_delinquent_segment_this_run_did_not_test() -> None:
    """Slice choice is the model's: attempts 4 and 5 found the segment and this run did not.

    Attempt 4 sliced `delinq_count_6m == 0` and reached test AUC 0.5875 on it; attempt 5 sliced
    `delinq_last == 0` and reached 0.6312, against a split-wide 0.755. This run's four steps went
    nowhere near it -- its `delinq_count_6m above_median` step was the whole split -- so no open
    item was raised, which is a property of the run and not of the package.
    """
    store = _store()
    assert store.value("metrics.test.auc") == pytest.approx(0.755, abs=5e-4)
    archive = REPO_ROOT / "eval" / "results" / "first-live"
    fourth = ArtifactStore(archive / "credit-attempt4" / "artifacts")
    fifth = ArtifactStore(archive / "credit-attempt5" / "artifacts")
    assert fourth.value("metrics.test.sub.delinq_count_6m_eq_0.auc") == pytest.approx(
        0.5875, abs=5e-5
    )
    assert fifth.value("metrics.test.sub.delinq_last_eq_0.auc") == pytest.approx(0.6312, abs=5e-5)
    assert "delinq_count_6m_eq_0" not in "".join(_index())
    assert "delinq_last_eq_0" not in "".join(_index())


def test_the_slug_the_degenerate_step_stored_under_is_the_one_the_rule_gives() -> None:
    """The link between the run's artifact names and the rule its trace records."""
    assert Subpopulation(column="delinq_count_6m", rule="above_median").slug == DEGENERATE


# --- D-120: the excerpt's five wording edits, checked against the file they quote ----------------


@pytest.mark.parametrize(("before", "after"), EXCERPT_EDITS, ids=[str(i) for i in range(6)])
def test_each_excerpt_edit_quotes_a_sentence_the_report_carries_exactly_once(
    before: str, after: str
) -> None:
    """D-120's entry cannot drift from `report.md`, because this reads one against the other.

    The `before` string has to be in the committed report exactly once -- otherwise Phase 16 has
    no unambiguous place to apply the edit -- and the `after` string has to be absent from it,
    because the edits live in the excerpt and never in the record.
    """
    report = _report()
    assert report.count(before) == 1, before
    assert after not in report, after


def test_no_excerpt_edit_changes_a_number() -> None:
    """The one property of the five that makes them wording edits (D-120).

    Each pair is tokenized by the pipeline's own definition of an eligible number, and the two
    sides must produce the same numbers in the same order. A citation is not a number -- its hash
    is an exclusion -- so moving one within the sentence is invisible here, which is the point.
    """
    for before, after in EXCERPT_EDITS:
        was = [token.value for token in eligible_numbers(before, package_version="1.0").tokens]
        now = [token.value for token in eligible_numbers(after, package_version="1.0").tokens]
        assert was == now, before


def test_the_excerpt_is_sections_two_and_four_whole() -> None:
    """What Phase 16 excerpts, so the sections the edits sit in are the sections it takes."""
    report = _report()
    conceptual = report.split("## 2. Conceptual soundness", 1)[1].split("## 3.", 1)[0]
    outcomes = report.split("## 4. Outcomes analysis", 1)[1].split("## 5.", 1)[0]
    assert "### Follow-up analyses" in outcomes
    assert f"sub.{DEGENERATE}.share" in outcomes
    for index in (0, 1, 2):
        assert EXCERPT_EDITS[index][0] in conceptual
    for index in (3, 4, 5):
        assert EXCERPT_EDITS[index][0] in outcomes


# --- the defect classes earlier runs named, none of which recurred -------------------------------


def test_the_two_token_classes_that_cost_earlier_runs_claims_are_excluded_here() -> None:
    """D-099's exponents verify and D-112's section references are excluded, from the record."""
    exclusions = {item["pattern"]: list(item["examples"]) for item in _claims()["exclusions"]}
    assert "Section 4" in exclusions["section_number"]
    assert "Section 2" in exclusions["section_number"]
    assert exclusions["package_version"] == ["1.0"]
    report = _report()
    for literal in ("1.92e-05", "-5.589e-05", "-0.001393"):
        line = next(line for line in report.splitlines() if literal in line)
        assert literal in [token.text for token in eligible_numbers(line).tokens]
    verified = {claim["value"] for claim in _claims()["post_repair"]}
    assert {1.92e-05, -5.589e-05, -0.001393} <= verified


def test_the_two_developer_claims_of_the_package_both_verify() -> None:
    """The package's own `claims` block, checked against the recomputed artifacts (D-061)."""
    developer = _claims()["developer_claims"]
    assert [claim["status"] for claim in developer] == ["verified", "verified"]
    assert [claim["metric"] for claim in developer] == ["auc", "brier"]


def test_the_deciles_and_the_calibration_bin_no_rule_reads() -> None:
    """The known limitation `docs/EVALUATION.md` records, on the run's own tables.

    The test event rate is non-monotone at deciles 4/5 and 8/9 and calibration bin 6 predicts
    0.1416 against 0.1767 observed. Both are in the rendered tables and neither is remarked on in
    the prose, because no rule this build ships reads within-decile ordering. It is listed under
    "What the excerpt does not show" rather than fixed here.
    """
    store = _store()
    deciles = {int(row["decile"]): float(row["event_rate"]) for row in store.load("deciles.test")}
    assert deciles[4] < deciles[5], "the event rate rises where the score falls"
    assert deciles[8] < deciles[9]
    assert deciles[4] == pytest.approx(0.1711, abs=5e-5)
    assert deciles[5] == pytest.approx(0.1767, abs=5e-5)
    assert deciles[8] == pytest.approx(0.09667, abs=5e-6)
    assert deciles[9] == pytest.approx(0.1, abs=5e-5)
    calibration = {
        int(row["bin"]): (float(row["mean_predicted"]), float(row["observed"]))
        for row in store.load("calibration.test")
    }
    assert calibration[6][0] == pytest.approx(0.1416, abs=5e-5)
    assert calibration[6][1] == pytest.approx(0.1767, abs=5e-5)
    assert "non-monotone" not in _report()


def test_the_sign_disagreement_is_a_qualification_and_not_an_open_item() -> None:
    """The other known limitation: D-095's family is section 2 prose, and nothing routes it."""
    report = _report()
    conceptual = report.split("## 2. Conceptual soundness", 1)[1].split("## 3.", 1)[0]
    assert "sign_check.n_disagreements" in conceptual
    assert "bill_trend_6m" in conceptual
    assert "the disagreement that matters most of the three" in conceptual
    findings = report.split("## 6. Findings", 1)[1].split("## 7.", 1)[0]
    assert "bill_trend_6m" not in findings
    assert "nothing in this section is carried forward to the findings section" in conceptual


def test_the_guidance_citations_mix_two_corpora_where_one_had_no_span() -> None:
    """The last of the known limitations, read off the report's own regulatory citations."""
    report = _report()
    assert "[[reg:SR26-2:" in report
    assert "[[reg:SR11-7:V.1.b]]" in report
    exclusions = {item["pattern"]: list(item["examples"]) for item in _claims()["exclusions"]}
    ids = exclusions["regulatory_section_id"]
    assert [item for item in ids if item.startswith("SR11-7")] == ["SR11-7:V.1.a", "SR11-7:V.1.b"]
    assert [item for item in ids if item.startswith("SR26-2")] != []
