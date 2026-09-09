"""The fifth live validation: four executed steps, and the first open items the pipeline wrote.

`eval/results/first-live/credit-attempt5/` is the record of the run of 2026-09-08 that rendered on a
build carrying D-084 to D-108: 22 model calls, 17 tool calls, 285 post-repair claims, grounding
precision 0.9827 before repair and 1.0000 after, no finding, exit 0. Six of the seven defects the
fourth attempt found did not recur. What the reading of it found is one repair round that rewrote a
line nobody flagged -- the first defect a live run has produced that the verifier is structurally
unable to catch -- and four failed claims that are the pipeline's own doing rather than the
drafter's. `docs/EVALUATION.md` section 1 writes the run up; this module is the half a machine
checks.

Every figure asserted here is re-derived from `trace.jsonl`, `claims.json`, `findings.json`, the 22
cassettes and the artifact index of that directory, so a number that drifts from the run fails the
suite. Nothing here calls a model.
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any, Final

import pytest

from quaestor import TraceReader
from quaestor.artifacts.store import ArtifactStore
from quaestor.report.repair import _same_statement, scope_to_flagged_lines
from quaestor.report.sections import CHALLENGER_DELTA, four_significant_figures, prompt_value
from quaestor.tools.metrics import subpopulation_expression
from quaestor.trace import EventType, TraceEvent
from quaestor.verifier import ClaimStatus, VerifiedClaim, match_claim
from quaestor.verifier.claim import Claim
from quaestor.verifier.match import Match
from quaestor.verifier.tokens import eligible_numbers

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
ATTEMPT: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt5"
"""The committed record of the run this module is about."""

SLICES: Final = ("limit_bal_low", "delinq_last_eq_0", "delinq_last_eq_1", "utilisation_high")
"""The four sub-populations the bounded loop asked for, in the order it asked."""

DAMAGED: Final = (
    "The slice AUC falls below its split's by 0.007286 "
    "[[art:15e1edcb:metrics.test.sub.limit_bal_low.auc_gap]] on test and by -0.02732 "
    "[[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] is not the figure for this slice; "
    "on train the gap is -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]], and "
    "both splits sit within the allowance, so this slice stands as supporting evidence for the "
    "aggregate result."
)
"""The line the repair round rewrote without being asked to (D-109), as the report carries it."""

UNDAMAGED: Final = (
    "The slice AUC falls below its split's by 0.007286 "
    "[[art:15e1edcb:metrics.test.sub.limit_bal_low.auc_gap]] on test and by -0.001109 "
    "[[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]] on train, both within the allowance, "
    "so this slice stands as supporting evidence for the aggregate result."
)
"""The same line as the first draft wrote it, taken from `claims.json`'s pre-repair claims."""


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


def _store() -> ArtifactStore:
    """The attempt's own artifact store, which every figure below is read against."""
    return ArtifactStore(ATTEMPT / "artifacts")


def _index() -> dict[str, Any]:
    """The attempt's artifact index: every logical name the run stored."""
    payload = json.loads((ATTEMPT / "artifacts" / "index.json").read_text(encoding="utf-8"))
    return dict(payload["artifacts"])


def _cassettes() -> list[dict[str, Any]]:
    """The attempt's 22 tapes, in file-name order."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ATTEMPT / "cassettes").glob("*.json"))
    ]


def _one(texts: list[str], marker: str) -> str:
    """The one flagged line carrying this marker, so the replay is keyed on the record."""
    found = [text for text in texts if marker in text]
    assert len(found) == 1, marker
    return found[0]


def _failed() -> list[dict[str, Any]]:
    """The five pre-repair claims that did not verify, in prose order."""
    return [claim for claim in _claims()["pre_repair"] if claim["status"] != "verified"]


# --- what the run did -------------------------------------------------------------------------


def test_the_trace_is_the_run_the_evaluation_describes() -> None:
    """462 events, 22 model calls, 17 tool calls, 4 plan steps, 2 repair rounds, 417 checks."""
    counts = Counter(event.type for event in _events())
    assert sum(counts.values()) == 462
    assert counts[EventType.llm_call] == 22
    assert counts[EventType.tool_call] == 17
    assert counts[EventType.plan_step] == 4
    assert counts[EventType.repair] == 2
    assert counts[EventType.claim_check] == 417


def test_twenty_two_model_calls_are_four_plans_nine_drafts_and_nine_extractions() -> None:
    """Seven sections drafted and extracted, plus the repairs of sections 4 and 7."""
    calls = _of(EventType.llm_call)
    assert Counter(str(event.payload["purpose"]) for event in calls) == {
        "draft": 9,
        "extract": 9,
        "plan": 4,
    }
    repairs = [event for event in calls if event.payload.get("repair")]
    assert [str(event.payload["section"]) for event in repairs] == ["outcomes", "monitoring"]
    assert {str(event.payload["model"]) for event in calls} == {"claude-opus-5[1m]"}


def test_the_loop_ran_four_steps_and_every_one_of_them_executed() -> None:
    """The first run in which no step of the bounded loop raised (attempt 4: one did)."""
    steps = _of(EventType.plan_step)
    assert [bool(event.payload["accepted"]) for event in steps] == [True] * 4
    assert [bool(event.payload["executed"]) for event in steps] == [True] * 4
    asked = [dict(event.payload["args"]["subpopulation"]) for event in steps]
    assert [(item["column"], item["rule"]) for item in asked] == [
        ("limit_bal", "below_median"),
        ("delinq_last", "equals:0"),
        ("delinq_last", "equals:1"),
        ("utilisation", "above_median"),
    ]


def test_the_loop_chose_different_slices_from_the_fourth_run_s() -> None:
    """Same prompt, same subject, same model: attempt 4 sliced `delinq_count_6m == 0`."""
    fourth = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt4" / "trace.jsonl"
    before = {
        str(event.payload["args"]["subpopulation"]["column"])
        for event in TraceReader(fourth)
        if event.type is EventType.plan_step
    }
    now = {
        str(event.payload["args"]["subpopulation"]["column"]) for event in _of(EventType.plan_step)
    }
    assert before == {"credit_limit", "limit_bal", "delinq_count_6m"}
    assert now == {"limit_bal", "delinq_last", "utilisation"}


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
        3.56, abs=5e-3
    )
    assert len(_index()) == 250


def test_the_claims_are_the_figures_the_front_matter_prints() -> None:
    """289 claims at 0.9827, 285 at 1.0000, and no finding at any severity."""
    claims = _claims()
    assert claims["grounding"]["pre_repair"]["precision"] == 0.9827
    assert claims["grounding"]["pre_repair"]["n_claims"] == 289
    assert claims["grounding"]["post_repair"]["precision"] == 1.0
    assert claims["grounding"]["post_repair"]["n_claims"] == 285
    assert json.loads((ATTEMPT / "findings.json").read_text(encoding="utf-8"))["findings"] == []
    statuses = Counter(str(event.payload["status"]) for event in _of(EventType.claim_check))
    assert statuses == {"verified": 412, "mismatch": 2, "unsupported": 3}
    assert "grounding_precision_post: 1.0000" in _report()
    assert "n_claims: 285" in _report()


def test_the_bill_is_what_the_evaluation_quotes() -> None:
    """123,170 output tokens, $6.0535, 1,328.47 s from the first traced event to the last."""
    calls = _of(EventType.llm_call)
    assert sum(int(event.payload["tokens_out"]) for event in calls) == 123_170
    assert sum(float(event.payload["cost_usd"]) for event in calls) == pytest.approx(
        6.0535, abs=5e-5
    )
    by_purpose: Counter[str] = Counter()
    cost: dict[str, float] = {}
    for event in calls:
        purpose = str(event.payload["purpose"])
        by_purpose[purpose] += int(event.payload["tokens_out"])
        cost[purpose] = cost.get(purpose, 0.0) + float(event.payload["cost_usd"])
    assert dict(by_purpose) == {"plan": 1_400, "draft": 45_370, "extract": 76_400}
    assert cost["extract"] == pytest.approx(2.7065, abs=5e-5)
    assert cost["draft"] == pytest.approx(3.0089, abs=5e-5)
    assert cost["plan"] == pytest.approx(0.3381, abs=5e-5)
    events = _events()
    assert (events[-1].ts - events[0].ts).total_seconds() == pytest.approx(1328.47, abs=0.01)
    longest = max(calls, key=lambda event: int(event.payload["tokens_out"]))
    assert str(longest.payload["purpose"]) == "extract"
    assert int(longest.payload["tokens_out"]) == 25_647
    assert float(longest.payload["latency_ms"]) / 1000 == pytest.approx(250.9, abs=0.05)


def test_the_input_token_count_agrees_with_the_cassettes() -> None:
    """D-093's three-field sum, checked against the tapes rather than asserted."""
    tapes = _cassettes()
    assert len(tapes) == 22
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
    assert total == 290_392
    assert sum(int(event.payload["tokens_in"]) for event in _of(EventType.llm_call)) == total


def test_extraction_output_per_claim_check_is_the_figure_the_table_prints() -> None:
    """183 per check, against 173 on attempt 4 -- and the total is what D-115 addresses."""
    extraction = sum(
        int(event.payload["tokens_out"])
        for event in _of(EventType.llm_call)
        if str(event.payload["purpose"]) == "extract"
    )
    checks = len(_of(EventType.claim_check))
    assert extraction == 76_400
    assert checks == 417
    assert round(extraction / checks) == 183


# --- the two open items, which are the first the pipeline has produced live ---------------------


def test_both_delinquency_slices_qualify_as_open_items_and_the_other_two_do_not() -> None:
    """D-102's two bounds, on the run's own numbers."""
    store = _store()
    bound = store.value("threshold.O1.slice_auc_gap")
    floor = store.value("threshold.O1.slice_min_share")
    assert (bound, floor) == (0.08, 0.10)
    reading = {
        slug: (
            store.value(f"metrics.test.sub.{slug}.auc_gap"),
            store.value(f"metrics.test.sub.{slug}.share"),
        )
        for slug in SLICES
    }
    material = {slug for slug, (gap, share) in reading.items() if gap > bound and share >= floor}
    assert material == {"delinq_last_eq_0", "delinq_last_eq_1"}
    assert reading["delinq_last_eq_0"][0] == pytest.approx(0.1238, abs=5e-5)
    assert reading["delinq_last_eq_1"][0] == pytest.approx(0.1037, abs=5e-5)
    assert reading["limit_bal_low"][0] == pytest.approx(0.007286, abs=5e-7)
    assert reading["utilisation_high"][0] == pytest.approx(-0.02309, abs=5e-6)


def test_the_report_carries_two_open_items_and_calls_neither_a_finding() -> None:
    """Attempt 4's `### Open items` said there was nothing to list; this one asks two questions."""
    report = _report()
    section = report.split("### Open items", 1)[1].split("## 7.", 1)[0]
    items = [line for line in section.splitlines() if "owner: model developer" in line]
    assert len(items) == 2
    assert "delinq_last equal to zero" in items[0]
    assert "delinq_last equal to one" in items[1]
    assert "finding" not in "".join(items).lower()
    for slug in ("delinq_last_eq_0", "delinq_last_eq_1"):
        assert f"metrics.test.sub.{slug}.auc_gap" in section
    assert "threshold.O1.slice_auc_gap" in section
    assert "threshold.O1.slice_min_share" in section


# --- the six defects of attempt 4 that did not recur --------------------------------------------


@pytest.mark.parametrize(
    ("literal", "name"),
    [
        ("1.92e-05", "ablation.utilisation.delta_auc"),
        ("-5.589e-05", "ablation.pay_ratio_last.delta_auc"),
        ("9.982e-06", "csi.bill_mean_6m"),
    ],
)
def test_the_exponent_literals_are_one_token_each_and_all_verify(literal: str, name: str) -> None:
    """D-099 did not recur: attempt 4's six failed claims were these three literals."""
    line = next(line for line in _report().splitlines() if literal in line and name in line)
    tokens = [token.text for token in eligible_numbers(line).tokens]
    assert literal in tokens
    verified = {
        claim["citation"]: claim
        for claim in _claims()["post_repair"]
        if claim["status"] == "verified" and claim["citation"]
    }
    assert any(name in citation for citation in verified)


def test_the_six_defects_of_the_fourth_attempt_that_did_not_recur() -> None:
    """D-100, D-103, D-104, D-106 and D-108, each read off the report the run wrote."""
    report = _report()
    monitoring = report.split("## 7. Ongoing monitoring", 1)[1]
    findings = report.split("## 6. Findings", 1)[1].split("## 7.", 1)[0]
    # D-100: the Brier ceiling is recommended with the recomputed value beside it.
    assert "0.1385 [[art:86e93c8f:metrics.test.brier]]" in monitoring
    for forbidden in ("not carried", "no recomputed", "is not available", "uncomputed"):
        assert forbidden not in report
    # D-103: no finding, said once, with no drafted list of what was reviewed.
    assert "This validation raised no finding." in findings
    assert "Checks that ran and raised no candidate" in findings
    assert "input data lineage" not in report
    # D-104: section 7 describes the ordering section 4 actually chose.
    assert "This section reports discrimination first and calibration second." in report
    assert "presented discrimination before calibration" in monitoring
    # D-106: a count is spelled as a count.
    assert "0.0 features" not in report
    # D-108: sections 3 and 5 open on the current guidance.
    assert "[[reg:SR26-2:IV.1]]" in report.split("## 3. Data integrity", 1)[1].split("## 4.", 1)[0]
    assert "[[reg:SR26-2:V.1.a]]" in report.split("## 5. Sensitivity", 1)[1].split("## 6.", 1)[0]


def test_the_challenger_this_run_compared_is_in_its_own_store() -> None:
    """D-114's premise: section 7 called benchmarking absent on a run that ran one."""
    assert CHALLENGER_DELTA in _store()
    monitoring = _report().split("## 7. Ongoing monitoring", 1)[1]
    assert "was not part of this validation" in monitoring, "the sentence D-114 is about"


# --- the five failed claims, and the line nothing flagged ---------------------------------------


def test_the_five_failed_claims_are_the_five_the_evaluation_names() -> None:
    """Two rounded counts, two slice-rule parameters and one section reference."""
    failed = _failed()
    assert [claim["status"] for claim in failed] == [
        "mismatch",
        "unsupported",
        "mismatch",
        "unsupported",
        "unsupported",
    ]
    assert [claim["value"] for claim in failed] == [10160.0, 0.0, 16210.0, 1.0, 4.0]


def test_the_two_mismatched_counts_are_what_the_prompt_rounded(tmp_path: Path) -> None:
    """D-110: 10158 reached the drafter as 10160, and the matcher holds a count to half a unit."""
    store = _store()
    for name, written in (
        ("metrics.train.sub.limit_bal_low.n", 10160.0),
        ("metrics.train.sub.delinq_last_eq_0.n", 16210.0),
    ):
        held = store.value(name)
        assert four_significant_figures(held) == written, "the prompt's own rounding"
        assert prompt_value(held) == held, "and what it shows now"
        assert held != written
    assert store.value("metrics.train.sub.limit_bal_low.n") == 10158
    assert store.value("metrics.train.sub.delinq_last_eq_0.n") == 16207


def test_the_three_unsupported_tokens_are_not_claims_at_all() -> None:
    """D-112: two slice-rule parameters and one reference to a section of this report."""
    failed = _failed()
    zero, one, section = failed[1], failed[3], failed[4]
    assert zero["text"].startswith("**delinq_last equals 0.**")
    assert one["text"].startswith("**delinq_last equals 1.**")
    assert section["text"].startswith("Section 4 of this report")
    # As the loop asked for them, and as the drafter is now asked to write them.
    assert subpopulation_expression("delinq_last", "equals:0") == "delinq_last == 0"
    assert subpopulation_expression("delinq_last", "equals:1") == "delinq_last == 1"
    # The tokenizer excludes both forms now: inline code since D-015, the reference since D-112.
    assert eligible_numbers("**`delinq_last == 0`.** Metrics were recomputed.").tokens == []
    reference = eligible_numbers(section["text"])
    assert [token.text for token in reference.tokens] == ["0.05"], "the bound stays a claim"
    assert "Section 4" in [token.text for token in reference.excluded]


def test_appendix_a_reports_a_rewrite_the_round_did_not_make() -> None:
    """D-111: the flagged 10160 was paired with another slice's verified 10500."""
    repairs = _claims()["repairs"]
    assert len(repairs) == 1
    assert (repairs[0]["before"]["value"], repairs[0]["after"]["value"]) == (10160.0, 10500.0)
    assert "10160 (mismatch) | 10500 (verified)" in _report()
    assert "1 claim(s) rewritten and 4 number(s) removed" in _report()
    events = _of(EventType.repair)
    assert [list(event.payload["removed"]) for event in events] == [[0.0, 16210.0, 1.0], [4.0]]
    assert sum(len(event.payload["removed"]) for event in events) == 4, "the trace's own count"


def test_the_pairing_that_produced_that_row_is_refused_now() -> None:
    """The two claims, as `claims.json` carries them, through `_same_statement` (D-111)."""
    flagged = _failed()[0]
    replacement = next(
        claim
        for claim in _claims()["post_repair"]
        if claim["value"] == 10500.0 and "utilisation_high.n" in (claim["citation"] or "")
    )
    before = Match(claim=VerifiedClaim(**flagged))
    after = Match(claim=VerifiedClaim(**replacement))
    assert _same_statement(before, after) is False
    assert before.claim.text.count("[[art:") == after.claim.text.count("[[art:")


def test_the_repair_round_rewrote_a_line_nobody_flagged() -> None:
    """D-109: the damaged line is in the report and every citation in it resolves."""
    report = _report()
    assert DAMAGED in report
    assert UNDAMAGED in {claim["text"] for claim in _claims()["pre_repair"]}
    assert UNDAMAGED not in report
    store = _store()
    for claim in _claims()["post_repair"]:
        if claim["text"] == DAMAGED:
            rebuilt = Claim(
                **{key: claim[key] for key in ("text", "value", "unit", "section")},
                citation=claim["citation"],
                source=claim["source"],
            )
            assert match_claim(rebuilt, store).claim.status is ClaimStatus.verified
    assert "is not the figure for this slice" in DAMAGED, "which no claim-level check can see"


def test_scoping_the_round_to_its_flagged_lines_keeps_the_damaged_line_out() -> None:
    """The run's own section 4, replayed: four lines re-drafted and every other line untouched.

    Keeping the damaged line out is the half this run's reading found. The other half is the
    guarantee D-109 actually makes, which is about *all* the rest of the section and not one
    sentence of it: every line of the previous draft that carried no flagged claim comes back
    byte-identical. Both are asserted here.
    """
    report = _report().splitlines()
    start = report.index("## 4. Outcomes analysis")
    end = report.index("## 5. Sensitivity and scenario analysis")
    after = report[start:end]
    flagged = [claim["text"] for claim in _failed() if claim["section"] == "outcomes"]
    reverted = {
        "On train the slice holds 0.4837": _one(flagged, "limit_bal_low.share"),
        "On train the slice holds 0.7718": _one(flagged, "delinq_last_eq_0.share"),
        "**delinq_last equal to zero.**": _one(flagged, "**delinq_last equals 0."),
        "**delinq_last equal to one.**": _one(flagged, "**delinq_last equals 1."),
    }
    previous: list[str] = []
    for line in after:
        if line == DAMAGED:
            previous.append(UNDAMAGED)
            continue
        opening = next((text for head, text in reverted.items() if line.startswith(head)), None)
        previous.append(opening or line)
    assert len(flagged) == 4
    assert sum(1 for line in previous if line in flagged) == 4
    failures = [Match(claim=VerifiedClaim(**claim)) for claim in _failed()[:4]]
    result = scope_to_flagged_lines("\n".join(previous), "\n".join(after), failures)
    scoped = result.markdown
    assert result.lines_redrafted == 4
    assert result.scoped is True, "the round found its flagged lines and did not fall back"
    assert UNDAMAGED in scoped.splitlines()
    assert DAMAGED not in scoped
    for text in flagged:
        assert text not in scoped, "the flagged lines still take their re-drafted text"
    kept = set(scoped.splitlines())
    written = [line for line in previous if line.strip()]
    unflagged = [line for line in written if line not in flagged]
    assert len(unflagged) == len(written) - 4, "the four flagged lines and everything else"
    missing = [line for line in unflagged if line not in kept]
    assert missing == [], "every unflagged line of the previous section 4 is kept verbatim"
