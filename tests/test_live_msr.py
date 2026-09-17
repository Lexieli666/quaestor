"""The second live validation of the hazard subject: the run the README excerpts, and its finding.

`eval/results/first-live/msr/` is the record of the run of 2026-09-17 that rendered on `a87aa4a`,
the build carrying D-165 to D-167: 21 model calls, 19 tool calls, 298 claims at grounding precision
**0.9966 before repair and 1.0000 after it over 297**, one repair round, one finding (F-001, C1
calibration at medium, ten candidates merged) and two open items, exit 0, $6.4858, 1,373.77 s. It
carries no `attempt` suffix because it is the run the README excerpts, and `report.md` is committed
as produced and is never edited (DECISIONS D-120, D-168).

It is the first live run the README can excerpt that has a finding to show. The credit run the
README excerpts found nothing, so its section 6 says "This validation raised no finding." and its
section 1 prints a scope table of zeroes; this one publishes F-001 in section 1 under D-165 and
draws it in full in section 6 under D-156. The excerpt is sections 2 and 4 whole, the two sections
in which every claim verified before any repair -- 48 of 48 and 109 of 109 -- with the four wording
edits D-168 records and nothing else.

The one pre-repair failure is in section 3 and outside the excerpt: "its recorded SHA-256 digest"
tokenised as an unsupported claim of 256, the repair round removed the number and the drafter wrote
"cryptographic digest". That is a defect in our own tokeniser rather than a false sentence, and
D-169 is the fix; the run keeps the prose it produced.

Every figure asserted here is re-derived from `trace.jsonl`, `claims.json`, `findings.json`, the 21
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
from quaestor.tools import default_registry
from quaestor.tools.thresholds import SLICE_GAP_BOUND, SLICE_SHARE_FLOOR
from quaestor.trace import EventType, TraceEvent
from quaestor.verifier.tokens import eligible_numbers
from toolsupport import context

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
RUN: Final = REPO_ROOT / "eval" / "results" / "first-live" / "msr"
"""The committed record of the run this module is about."""

PARTITIONS: Final = (
    ("incentive", "above_median", "incentive_high"),
    ("incentive", "below_median", "incentive_low"),
    ("loan_age", "above_median", "loan_age_high"),
    ("loan_age", "below_median", "loan_age_low"),
)
"""The four sub-populations the bounded loop asked for, in the order it asked.

Two complete partitions rather than four unrelated slices, and each asked over both forward splits
at once: the loop used its four steps to ask whether the C1 level error is uniform or concentrated,
which is the question the finding raises.
"""

FORWARD_SPLITS: Final = ("out_of_time", "vintage_holdout")
"""The two splits every loop step was asked over."""

EVIDENCE: Final = (
    "20e93a8c",
    "749634ae",
    "92b5a8c4",
    "9e4c8750",
    "bab66615",
    "c12c52f7",
    "cf3a82aa",
    "d9f87bb2",
    "fd777cc4",
)
"""F-001's nine evidence artifacts, in the order `findings.json` records them.

The same nine the fake-LLM run of this subject cites: the merge is deterministic and the narrative
is the only part of the finding a model writes (D-045).
"""

REPAIRED_CLAIM: Final = "7a2768dcbeb4fed3"
"""The one claim that did not verify before repair: the 256 of "SHA-256" (D-169)."""

EXCERPT_EDITS: Final = (
    (
        "Both breaches are raised as C1 calibration findings.",
        "Both breaches are raised together as one C1 calibration finding.",
    ),
    (
        "the latter well below the lower bound of 0.8 "
        "[[art:749634ae:threshold.C1.calibration_slope.min]]",
        "the latter well below rule C1's floor of 0.8 "
        "[[art:749634ae:threshold.C1.calibration_slope.min]]",
    ),
    (
        "comfortably inside the declared gap allowance of 0.08 "
        "[[art:630f28f4:threshold.O1.auc_gap]]",
        "comfortably inside the gap allowance of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] "
        "rule O1 sets",
    ),
    (
        ", and across the loan-age partition the defect reads as a level shift rather than a "
        "seasoning-shape failure.",
        ".",
    ),
)
"""D-168's four wording edits as `(before, after)`, with the citations the report actually carries.

Each `before` is asserted below to be in `report.md` exactly once, so the DECISIONS entry Phase 16
copies from cannot drift from the file it quotes. No `after` changes a number, and none of them is
applied here: the record is the record. The fourth pair deletes a trailing clause, which is why its
`after` is a full stop.
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


def _section(number: int) -> str:
    """One numbered section of the report, its heading to the next heading at that level."""
    body = _report().split(f"\n## {number}. ", 1)[1]
    if number < 7:
        return body.split(f"\n## {number + 1}. ", 1)[0]
    return body.split("\n## Appendix", 1)[0]


def _claims() -> dict[str, Any]:
    """The run's `claims.json`."""
    return dict(json.loads((RUN / "claims.json").read_text(encoding="utf-8")))


def _findings() -> dict[str, Any]:
    """The run's `findings.json`."""
    return dict(json.loads((RUN / "findings.json").read_text(encoding="utf-8")))


def _store() -> ArtifactStore:
    """The run's own artifact store, which every figure below is read against."""
    return ArtifactStore(RUN / "artifacts")


def _index() -> dict[str, Any]:
    """The run's artifact index: every logical name it stored."""
    payload = json.loads((RUN / "artifacts" / "index.json").read_text(encoding="utf-8"))
    return dict(payload["artifacts"])


def _cassettes() -> list[dict[str, Any]]:
    """The run's 21 tapes, in file-name order."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((RUN / "cassettes").glob("*.json"))
    ]


# --- what the run did ---------------------------------------------------------------------------


def test_the_trace_is_the_run_the_evaluation_describes() -> None:
    """414 events, 21 model calls, 19 tool calls, 4 plan steps, one repair, 368 checks."""
    counts = Counter(event.type for event in _events())
    assert sum(counts.values()) == 414
    assert counts[EventType.llm_call] == 21
    assert counts[EventType.tool_call] == 19
    assert counts[EventType.plan_step] == 4
    assert counts[EventType.repair] == 1
    assert counts[EventType.finding] == 1
    assert counts[EventType.claim_check] == 368, "298 before repair and section 3's 70 after"


def test_twenty_one_model_calls_are_four_plans_eight_drafts_eight_extractions_and_one_reask() -> (
    None
):
    """The one re-ask is the repair round's scoped re-draft of section 3 (D-109)."""
    calls = _of(EventType.llm_call)
    assert Counter(str(event.payload["purpose"]) for event in calls) == {
        "draft": 8,
        "extract": 8,
        "plan": 4,
        "reask": 1,
    }
    assert Counter(bool(event.payload.get("repair")) for event in calls) == {True: 1, False: 20}
    assert Counter(int(event.payload["attempt"]) for event in calls) == {1: 20, 2: 1}
    assert {str(event.payload["model"]) for event in calls} == {"claude-opus-5[1m]"}
    assert "| LLM calls | 21 (plan 4, draft 8, reask 1, extract 8) |" in _report()


def test_the_loop_ran_four_steps_and_every_one_of_them_executed() -> None:
    """Two complete partitions, each asked over both forward splits at once."""
    steps = _of(EventType.plan_step)
    assert [bool(event.payload["accepted"]) for event in steps] == [True] * 4
    assert [bool(event.payload["executed"]) for event in steps] == [True] * 4
    assert [str(event.payload["error"]) for event in steps] == [""] * 4
    args = [dict(event.payload["args"]) for event in steps]
    assert [tuple(item["splits"]) for item in args] == [FORWARD_SPLITS] * 4
    asked = [dict(item["subpopulation"]) for item in args]
    assert [(item["column"], item["rule"]) for item in asked] == [
        (column, rule) for column, rule, _ in PARTITIONS
    ]
    assert "| plan steps (bounded loop) | 4 |" in _report()


def test_nineteen_tool_calls_and_not_one_of_them_raised() -> None:
    """Fourteen from the rule-based plan and five `compute_metrics`; only C1 was ever raised."""
    tools = _of(EventType.tool_call)
    assert Counter(str(event.payload["tool"]) for event in tools) == {
        "retrieve_guidance": 7,
        "compute_metrics": 5,
        "run_model": 1,
        "profile_data": 1,
        "check_leakage": 1,
        "check_stability": 1,
        "check_collinearity": 1,
        "challenger_compare": 1,
        "run_scenarios": 1,
    }
    assert Counter(bool(event.payload["ok"]) for event in tools) == {True: 19}
    raised = [list(event.payload["candidates"]) for event in tools if event.payload["candidates"]]
    assert raised == [["C1"]] * 5, "every candidate of this run is C1, one per compute_metrics call"
    assert len(_index()) == 364


def test_the_claims_are_the_figures_the_front_matter_prints() -> None:
    """298 claims at 0.9966 before repair and 297 at 1.0000 after, with the per-section counts."""
    claims = _claims()
    pre = claims["grounding"]["pre_repair"]
    assert (pre["precision"], pre["n_claims"]) == (0.9966, 298)
    assert pre["status_counts"] == {
        "verified": 297,
        "mismatch": 0,
        "unsupported": 1,
        "dangling": 0,
        "unattributed": 0,
    }
    post = claims["grounding"]["post_repair"]
    assert (post["precision"], post["n_claims"]) == (1.0, 297)
    assert post["status_counts"] == {
        "verified": 297,
        "mismatch": 0,
        "unsupported": 0,
        "dangling": 0,
        "unattributed": 0,
    }
    verified = {name: item["verified"] for name, item in pre["per_section"].items()}
    counted = {name: item["n_claims"] for name, item in pre["per_section"].items()}
    assert verified == {
        "summary": 12,
        "conceptual_soundness": 48,
        "data_integrity": 70,
        "outcomes": 109,
        "sensitivity": 30,
        "findings": 21,
        "monitoring": 7,
    }
    assert counted == {**verified, "data_integrity": 71}
    report = _report()
    assert "grounding_precision_pre: 0.9966" in report
    assert "grounding_precision_post: 1.0000" in report
    assert "n_claims: 297" in report
    assert "n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}" in report
    assert "| 0.9966 → 1.0000 | 0 / 1 / 0 / 0 |" in report


def test_sections_two_and_four_verified_whole_before_any_repair() -> None:
    """Why these two are the excerpt: 48 of 48 and 109 of 109, pre-repair (D-168)."""
    per_section = _claims()["grounding"]["pre_repair"]["per_section"]
    for name in ("conceptual_soundness", "outcomes"):
        assert per_section[name]["precision"] == 1.0
        assert per_section[name]["verified"] == per_section[name]["n_claims"]
    checks = _of(EventType.claim_check)
    for name in ("conceptual_soundness", "outcomes"):
        statuses = {
            str(event.payload["status"])
            for event in checks
            if str(event.payload["section"]) == name
        }
        assert statuses == {"verified"}, name


def test_one_repair_round_removed_the_two_hundred_and_fifty_six_of_sha_256() -> None:
    """The run's single pre-repair failure, and D-097's empty `repairs` list beside it."""
    events = _of(EventType.repair)
    assert len(events) == 1
    payload = dict(events[0].payload)
    assert str(payload["section"]) == "data_integrity"
    assert int(payload["round"]) == 1
    assert list(payload["flagged"]) == [REPAIRED_CLAIM]
    assert list(payload["repaired"]) == []
    assert list(payload["removed"]) == [256.0]
    assert int(payload["lines_redrafted"]) == 1
    assert bool(payload["scoped"]) is True
    assert list(payload["still_failing"]) == []
    claims = _claims()
    assert claims["repairs"] == [], "a removal is not a rewritten claim (D-097)"
    failed = [item for item in claims["pre_repair"] if item["status"] != "verified"]
    assert [item["id"] for item in failed] == [REPAIRED_CLAIM]
    assert failed[0]["value"] == 256.0
    assert failed[0]["citation"] is None
    assert "SHA-256 digest" in str(failed[0]["text"])
    ids_pre = {item["id"] for item in claims["pre_repair"]}
    ids_post = {item["id"] for item in claims["post_repair"]}
    assert ids_pre - ids_post == {REPAIRED_CLAIM}
    assert ids_post - ids_pre == set(), "the re-draft added no claim"
    report = _report()
    assert "| repair rounds | 1 |" in report
    assert "| re-asks | 1 |" in report
    assert "1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose" in report
    assert "its recorded cryptographic digest before any split was read" in report
    assert "recorded SHA-256 digest" not in report, "the number and its words both went"


def test_the_one_finding_is_a_medium_c1_that_merged_ten_candidates() -> None:
    """F-001, its nine evidence artifacts and the section it was routed to (D-156)."""
    findings = _findings()["findings"]
    assert len(findings) == 1
    finding = dict(findings[0])
    assert (finding["id"], finding["defect_class"], finding["severity"]) == (
        "F-001",
        "C1",
        "medium",
    )
    assert finding["suggested_severity"] == "medium"
    assert finding["severity_reason"] is None
    assert finding["tool"] == "compute_metrics"
    assert finding["section"] == "outcomes"
    assert int(finding["candidates_merged"]) == 10
    assert tuple(finding["evidence"]) == EVIDENCE
    store = _store()
    for hash8 in EVIDENCE:
        assert store.get(hash8).short_hash == hash8
    assert _findings()["candidates_not_promoted"] == []
    assert _findings()["illustrative"] is False
    events = _of(EventType.finding)
    assert len(events) == 1
    emitted = dict(events[0].payload)
    assert str(emitted["finding_id"]) == "F-000", (
        "the promotion is unnumbered; the document numbers"
    )
    assert (emitted["defect_class"], emitted["severity"]) == ("C1", "medium")
    assert bool(emitted["severity_changed"]) is False
    assert tuple(emitted["evidence"]) == EVIDENCE
    assert int(emitted["candidates_merged"]) == 10


def test_section_one_publishes_the_finding_and_section_six_draws_it() -> None:
    """D-165 in section 1 and D-156 in section 6, on the committed prose."""
    summary = _section(1)
    assert "F-001" in summary
    assert "a C1 calibration finding at medium severity" in summary
    assert "No findings" not in summary
    assert "raised no finding" not in summary
    findings = _section(6)
    assert "### F-001 · C1 calibration · severity **medium**" in findings
    assert "Candidates raised and not promoted: none." in findings


def test_the_three_developer_claims_of_the_package_all_verify() -> None:
    """The package's own `claims` block, checked against the recomputed artifacts (D-061)."""
    developer = _claims()["developer_claims"]
    assert [claim["status"] for claim in developer] == ["verified"] * 3
    assert [claim["metric"] for claim in developer] == ["auc", "brier", "calibration_slope"]
    assert [claim["split"] for claim in developer] == ["test"] * 3
    assert (
        "Developer claims: 3 of 3 declared in `package.yaml` verify against this run's artifacts."
        in _report()
    )


def test_the_bill_is_what_the_evaluation_quotes() -> None:
    """122,054 output tokens, $6.4858, 1,373.77 s from the first traced event to the last."""
    calls = _of(EventType.llm_call)
    assert sum(int(event.payload["tokens_out"]) for event in calls) == 122_054
    assert sum(float(event.payload["cost_usd"]) for event in calls) == pytest.approx(
        6.4858, abs=5e-5
    )
    out: Counter[str] = Counter()
    cost: Counter[str] = Counter()
    for event in calls:
        purpose = str(event.payload["purpose"])
        out[purpose] += int(event.payload["tokens_out"])
        cost[purpose] += float(event.payload["cost_usd"])
    assert dict(out) == {"plan": 1_757, "draft": 46_664, "reask": 6_216, "extract": 67_417}
    assert cost["plan"] == pytest.approx(0.4180, abs=5e-5)
    assert cost["draft"] == pytest.approx(3.0149, abs=5e-5)
    assert cost["reask"] == pytest.approx(0.6244, abs=5e-5)
    assert cost["extract"] == pytest.approx(2.4284, abs=5e-5)
    events = _events()
    assert (events[-1].ts - events[0].ts).total_seconds() == pytest.approx(1373.77, abs=0.01)
    report = _report()
    assert "| notional cost (USD) | 6.4858 |" in report
    assert "| wall-clock (s) | 1373.77 |" in report


def test_the_input_token_count_agrees_with_the_cassettes() -> None:
    """D-093's three-field sum, checked against the 21 tapes rather than asserted."""
    tapes = _cassettes()
    assert len(tapes) == 21
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
    assert total == 333_584
    assert sum(int(event.payload["tokens_in"]) for event in _of(EventType.llm_call)) == total
    assert "| tokens in / out | 333,584 / 122,054 |" in _report()


def test_appendix_c_records_the_manifest_check_and_appendix_d_has_one_row() -> None:
    """D-162's row, on a run whose data mode is real, and the one thing not checked."""
    report = _report()
    trace = report.split("## Appendix C", 1)[1].split("## Appendix D", 1)[0]
    assert "| data manifest | verified: 5 file(s) against package.yaml (see data.manifest) |" in (
        trace
    )
    assert "| provider adapter | claude-cli |" in trace
    assert "| run id | msr_prepayment-full_agent-20260917T044453Z-e98677a9 |" in trace
    not_checked = report.split("## Appendix D", 1)[1]
    rows = [
        line
        for line in not_checked.splitlines()
        if line.startswith("|") and not set(line) <= set("|- ")
    ]
    assert len(rows) == 2, "a header row and one item"
    assert "developer documentation" in rows[1]
    assert "data_mode: real" in report
    assert "illustrative: false" in report


# --- the bounded loop's result: which half of each partition raised an open item -----------------


def test_the_two_open_items_are_the_incentive_slices_and_the_loan_age_slices_raised_none() -> None:
    """The loop's substantive answer, re-derived from the run's own artifacts.

    Three of the four incentive slices are past `threshold.O1.slice_auc_gap` on a segment holding
    more than the minimum share -- `incentive_high` out of time and `incentive_low` on both forward
    splits -- and the report raises the two open items those three belong to. Neither loan-age half
    is past the bound on either split, so the seasoning partition raised nothing: it is the half of
    the loop that answered the C1 question without adding an open item.
    """
    store = _store()
    bound = store.value(SLICE_GAP_BOUND)
    floor = store.value(SLICE_SHARE_FLOOR)
    assert (bound, floor) == (0.08, 0.10)
    material = {
        (split, slug)
        for split in FORWARD_SPLITS
        for _, _, slug in PARTITIONS
        if store.value(f"metrics.{split}.sub.{slug}.auc_gap") > bound
        and store.value(f"metrics.{split}.sub.{slug}.share") >= floor
    }
    assert material == {
        ("out_of_time", "incentive_high"),
        ("out_of_time", "incentive_low"),
        ("vintage_holdout", "incentive_low"),
    }
    for split in FORWARD_SPLITS:
        for slug in ("loan_age_high", "loan_age_low"):
            gap = store.value(f"metrics.{split}.sub.{slug}.auc_gap")
            assert gap < bound, f"{split}.{slug} at {gap}"
            assert gap < 0.08
    open_items = _report().split("### Open items", 1)[1].split("\n## 7.", 1)[0]
    paragraphs = [line for line in open_items.splitlines() if line.strip()]
    assert len(paragraphs) == 2
    assert "`incentive > median(incentive)`" in paragraphs[0]
    assert "`incentive <= median(incentive)`" in paragraphs[1]
    assert "loan_age" not in open_items
    assert "owner" not in open_items or "model developer is asked" in open_items


def test_the_loan_age_partition_is_a_level_shift_only_in_absolute_terms() -> None:
    """Why D-168 cuts edit 4's closing clause, from the four sub-population artifacts.

    The absolute shortfalls are alike -- 0.0091 on the seasoned half out of time against 0.0082 on
    the newer half -- and the relative ones are not: about 3.8 times on the seasoned half against
    1.5 times on the newer. A sentence that resolves the ambiguity towards "a level shift" resolves
    it in the direction the evidence does not support, so the excerpt drops the clause rather than
    replacing it with a ratio the artifacts do not carry (D-168, and the pre-flight item it names).
    """
    store = _store()
    gaps: dict[str, tuple[float, float]] = {}
    for slug in ("loan_age_high", "loan_age_low"):
        predicted = store.value(f"metrics.out_of_time.sub.{slug}.mean_predicted")
        observed = store.value(f"metrics.out_of_time.sub.{slug}.event_rate")
        gaps[slug] = (observed - predicted, observed / predicted)
    assert gaps["loan_age_high"][0] == pytest.approx(0.0091, abs=5e-5)
    assert gaps["loan_age_low"][0] == pytest.approx(0.0082, abs=5e-5)
    assert abs(gaps["loan_age_high"][0] - gaps["loan_age_low"][0]) < 0.001
    assert gaps["loan_age_high"][1] == pytest.approx(3.82, abs=0.01)
    assert gaps["loan_age_low"][1] == pytest.approx(1.49, abs=0.01)
    assert gaps["loan_age_high"][1] > 2 * gaps["loan_age_low"][1]


def test_the_relative_gap_is_stored_by_the_build_after_this_run_and_not_by_this_one(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    """D-171: the run above had to divide by hand, and a slice computed today does not.

    Two runs, one assertion each. The first half reads the **committed** run of 2026-09-17 in
    `eval/results/first-live/msr/`, whose artifact index carries no `.sub.*.mean_rel_gap`: the
    ratios the test above derives -- about 3.8 against 1.5 times -- were computed in the test
    from two stored scalars because the run that produced them predates D-171, which is exactly
    why the report could not state them. The second half reads a **fresh** offline run of the
    synthetic hazard subject (`msr_run_dir`, no model and no real data), sliced today by the same
    `loan_age` partition, and the quotient is in its store as an artifact a sentence can cite.

    The committed half keeps passing for as long as the run stays committed, because it is a
    statement about that run and not about the code.
    """
    committed = [name for name in _index() if ".sub." in name]
    assert committed, "the committed run did slice, so the absence below is a fact about it"
    assert not [name for name in committed if name.endswith(".mean_rel_gap")], (
        "the run of 2026-09-17 predates D-171, so no sub-population artifact of it is relative"
    )

    ctx = context(tmp_path, REPO_ROOT / "subjects" / "msr_prepayment", msr_run_dir)
    default_registry().call(
        "compute_metrics",
        {"splits": ["test"], "subpopulation": {"column": "loan_age", "rule": "above_median"}},
        ctx,
    )
    stem = "metrics.test.sub.loan_age_high"
    predicted = ctx.store.value(f"{stem}.mean_predicted")
    observed = ctx.store.value(f"{stem}.event_rate")
    assert ctx.store.value(f"{stem}.mean_rel_gap") == pytest.approx(
        abs(predicted - observed) / observed
    )


def test_the_finding_s_narrative_reads_the_absolute_gap_and_the_relative_one_disagrees() -> None:
    """The known limitation D-168 records for section 6, on the out-of-time calibration table.

    "widens as predicted risk rises" is true of the absolute gap -- bin 1 at 0.009 against bin 10
    at 0.015 -- and false of the relative one, which falls from about 37 times to about 1.5. The
    sentence is not edited: it is in section 6 and the excerpt is sections 2 and 4.
    """
    rows = {
        int(row["bin"]): (float(row["mean_predicted"]), float(row["observed"]))
        for row in _store().load("calibration.out_of_time")
    }
    assert len(rows) == 10
    first, last = rows[1], rows[10]
    assert last[1] - last[0] > first[1] - first[0], "the absolute gap does widen"
    assert first[1] / first[0] > last[1] / last[0], "the relative one collapses"
    assert (last[1] - last[0]) == pytest.approx(0.015, abs=5e-4)
    assert (first[1] - first[0]) == pytest.approx(0.009, abs=5e-4)
    assert first[1] / first[0] == pytest.approx(37.7, abs=0.1)
    assert last[1] / last[0] == pytest.approx(1.46, abs=0.01)
    narrative = str(_findings()["findings"][0]["narrative"])
    assert "widens as predicted risk rises" in narrative
    assert "widens as predicted risk rises" in _section(6)
    assert "widens as predicted risk rises" not in _section(4)


# --- D-168: the excerpt's four wording edits, checked against the file they quote ----------------


@pytest.mark.parametrize(("before", "after"), EXCERPT_EDITS, ids=[str(i) for i in range(4)])
def test_each_excerpt_edit_quotes_a_sentence_the_report_carries_exactly_once(
    before: str, after: str
) -> None:
    """D-168's entry cannot drift from `report.md`, because this reads one against the other.

    The `before` string has to be in the committed report exactly once -- otherwise Phase 16 has no
    unambiguous place to apply the edit -- and, where the `after` string is a sentence rather than a
    fragment of punctuation, it has to be absent from it, because the edits live in the excerpt and
    never in the record.
    """
    report = _report()
    assert report.count(before) == 1, before
    if len(after) > 1:
        assert after not in report, after


def test_no_excerpt_edit_changes_a_number() -> None:
    """The one property of the four that makes them wording edits (D-168).

    Each pair is tokenized by the pipeline's own definition of an eligible number, and the two
    sides must produce the same numbers in the same order. A citation is not a number -- its hash
    is an exclusion -- so moving one within the sentence is invisible here, which is the point, and
    the fourth edit deletes a clause that carries none.
    """
    for before, after in EXCERPT_EDITS:
        was = [token.value for token in eligible_numbers(before, package_version="1.0").tokens]
        now = [token.value for token in eligible_numbers(after, package_version="1.0").tokens]
        assert was == now, before


def test_the_excerpt_is_sections_two_and_four_whole() -> None:
    """What Phase 16 excerpts, so the sections the edits sit in are the sections it takes."""
    conceptual = _section(2)
    outcomes = _section(4)
    for heading in (
        "### Design and inputs",
        "### Coefficient magnitudes and signs",
        "### Sign agreement and the sensitivity of the model to each feature",
        "### Effective challenge",
    ):
        assert heading in conceptual, heading
    for heading in (
        "### Calibration",
        "### Discrimination",
        "### Declared thresholds",
        "### Follow-up analyses",
    ):
        assert heading in outcomes, heading
    for before, _ in EXCERPT_EDITS:
        assert before in outcomes, before
    assert all(before not in conceptual for before, _ in EXCERPT_EDITS), "all four are in §4"
    assert "SHA-256" not in conceptual and "SHA-256" not in outcomes
    assert "cryptographic digest" not in outcomes, "the repair is in §3, outside the excerpt"
