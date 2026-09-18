"""Phase 8: the section plan -- which artifacts each section may cite, and how it is shown them.

The selectors here are the only thing standing between a drafter and every number a run produced,
because the rule the drafter is held to is "write no number that is not in the JSON" and the JSON
is what this module builds. A selector that let a table through would print four calibration
tables; one that let every metric through would make a summary that wanders.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.findings import DefectClass, open_items
from quaestor.package import PackageSpec, Use, load_package
from quaestor.report.schema import FOLLOW_UPS_HEADING, OPEN_ITEMS_HEADING
from quaestor.report.sections import (
    CALIBRATION_FIRST_RULE,
    CHALLENGER_DELTA,
    DEFECT_CLASS_NAMES,
    MAX_JSON_PATHS,
    SECTION_BRIEFS,
    ArtifactBrief,
    OrderReason,
    SectionOrder,
    artifact_briefs,
    as_written,
    brief_for,
    calibration_before_discrimination,
    flatten_json,
    follow_up_for,
    four_significant_figures,
    monitoring_brief,
    ordered_briefs,
    prompt_value,
    recomputed_for_declared_bounds,
    section_four_order,
    section_heading,
    sections_for_follow_up,
    written_number,
)
from quaestor.tools.leakage import FEATURE_OVERLAP_BOUND
from quaestor.tools.metrics import THRESHOLD_TABLE, metric_artifact_name
from quaestor.tools.run import MAX_SECONDS_NAME
from quaestor.tools.thresholds import DEFAULT_THRESHOLDS, SLICE_GAP_BOUND, SLICE_SHARE_FLOOR
from quaestor.verifier import ClaimStatus, match_claim
from quaestor.verifier.claim import Claim, ClaimSource, Unit
from quaestor.vocab import SECTION_ORDER, ReportSection

REPO_ROOT = Path(__file__).resolve().parents[1]
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with one artifact of each kind the sections select over."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.74801204, ArtifactKind.scalar, "auc on test")
    store.put("metrics.test.event_rate", 0.2246, ArtifactKind.scalar, "event rate on test")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rare-event rule")
    store.put("psi.max", 0.011, ArtifactKind.scalar, "the largest PSI")
    store.put("calibration.test", [{"bin": 1, "observed": 0.05}], ArtifactKind.table, "calibration")
    store.put(
        "run.model_summary",
        {
            "coefficients": [{"feature": "utilisation", "value": 0.4871234}],
            "removed": [{"name": "bill_last", "vif": 41.7}],
            "note": "not a number",
        },
        ArtifactKind.json,
        "the subject's model_summary.json",
    )
    return store


def test_every_section_has_a_brief_a_heading_and_a_guidance_query() -> None:
    assert list(SECTION_BRIEFS) == list(SECTION_ORDER)
    for section in SECTION_ORDER:
        brief = brief_for(section)
        assert brief.heading.startswith("## ")
        assert brief.guidance_query
        assert brief.brief.strip()
        assert section_heading(section) == brief.heading


def test_every_defect_class_has_a_human_name_for_its_finding_heading() -> None:
    assert set(DEFECT_CLASS_NAMES) == set(DefectClass)
    assert DEFECT_CLASS_NAMES[DefectClass.E1] == "effective challenge"


def test_four_significant_figures_is_what_the_drafter_is_shown() -> None:
    assert four_significant_figures(0.74801204) == 0.748
    assert four_significant_figures(1500) == 1500
    assert four_significant_figures(-1129931.65) == -1130000.0


def test_written_number_never_uses_an_exponent() -> None:
    """`format(1e-05, "g")` writes `1e-05`, whose first numeric token is 1: a different claim."""
    assert written_number(1e-05) == "0.00001"
    assert written_number(1500.0) == "1500"
    assert written_number(0.748) == "0.748"
    assert written_number(-0.0672) == "-0.0672"


def test_a_value_too_small_for_twelve_decimals_keeps_its_significant_figures() -> None:
    """D-178: the fixed `.12f` was a precision ceiling, and below it a number was erased.

    `challenger.brier` on the `msr__L1__eom_balance` variant is 3.2264600208103315e-13 -- the
    seeded leakage makes the challenger near-perfect -- and the template wrote "is 0.0" of it.
    That is prose asserting a value the artifact does not hold, in the one configuration whose
    grounding precision is meant to be 1.0 by construction.
    """
    assert written_number(3.2264600208103315e-13) == "0.0000000000003226"
    assert written_number(-3.2264600208103315e-13) == "-0.0000000000003226"


def test_a_true_zero_and_a_near_zero_are_written_as_different_numbers() -> None:
    """The pairing failure behind the defect: both rendered as a number reading zero.

    A true zero is `0` and a value below the old ceiling was `0.0`, and the two tokenize to the
    same float -- so the template's declared claim, which carries the artifact's own value, could
    not be paired with the token in the prose, and the number landed as `unattributed`.
    """
    assert written_number(0.0) == "0"
    assert written_number(3.2264600208103315e-13) != written_number(0.0)
    assert float(written_number(3.2264600208103315e-13)) != 0.0


def test_no_number_written_before_this_fix_moves() -> None:
    """Twelve decimals stays the floor, so only a value too small for it gets more."""
    for value in (1e-05, 1500.0, 0.748, -0.0672, 0.0004999, 0.1 + 0.2, 10158.0, 0.5):
        assert written_number(value) == _twelve_decimals(value), value


def _twelve_decimals(value: float) -> str:
    """`written_number` exactly as it stood before D-178, for the no-regression case above."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.12f}".rstrip("0")
    return text if not text.endswith(".") else f"{text}0"


def test_flatten_json_addresses_list_elements_the_way_a_citation_does() -> None:
    payload = {
        "coefficients": [{"feature": "utilisation", "value": 0.487}],
        "removed": [{"name": "bill_last", "vif": 41.7}],
        "n": 12,
        "note": "not a number",
        "flag": True,
        "anonymous": [{"value": 1.0}],
    }
    flat = flatten_json(payload)
    assert flat["coefficients.utilisation.value"] == 0.487
    assert flat["removed.bill_last.vif"] == 41.7
    assert flat["n"] == 12
    assert "note" not in flat
    assert "flag" not in flat
    assert not [path for path in flat if path.startswith("anonymous")]


def test_flatten_json_stops_at_the_cap() -> None:
    payload = {"values": [{"name": f"f{i}", "value": float(i)} for i in range(MAX_JSON_PATHS + 10)]}
    assert len(flatten_json(payload)) == MAX_JSON_PATHS


def test_a_section_is_shown_scalars_its_own_tables_and_nothing_else(store: ArtifactStore) -> None:
    briefs = artifact_briefs(store, brief_for(ReportSection.outcomes))
    kinds = {item.name: item.kind.value for item in briefs}
    assert kinds["metrics.test.auc"] == "scalar"
    assert kinds["calibration.test"] == "table"
    assert kinds["run.metrics"] if "run.metrics" in kinds else True
    data = artifact_briefs(store, brief_for(ReportSection.data_integrity))
    assert "calibration.test" not in {item.name for item in data}
    assert "psi.max" in {item.name for item in data}


def test_the_extra_names_are_how_the_findings_section_is_given_its_evidence(
    store: ArtifactStore,
) -> None:
    briefs = artifact_briefs(
        store, brief_for(ReportSection.findings), extra=["metrics.test.auc", "not.in.the.store"]
    )
    assert [item.name for item in briefs] == ["metrics.test.auc"]


def test_the_payload_a_scalar_a_table_and_a_json_artifact_reach_the_prompt_as(
    store: ArtifactStore,
) -> None:
    briefs = {item.name: item for item in artifact_briefs(store, brief_for(ReportSection.outcomes))}
    scalar = briefs["metrics.test.auc"].to_payload()
    assert scalar["value"] == 0.748
    assert scalar["citation"].startswith("[[art:") and scalar["citation"].endswith(
        ":metrics.test.auc]]"
    )
    table = briefs["calibration.test"].to_payload()
    assert table["directive"] == "[[table:calibration.test]]"
    assert "value" not in table
    summary = artifact_briefs(store, brief_for(ReportSection.conceptual_soundness))
    json_brief = next(item for item in summary if item.name == "run.model_summary")
    payload = json_brief.to_payload()
    assert payload["values"]["coefficients.utilisation.value"] == 0.4871
    assert payload["citation_form"] == f"[[art:{json_brief.hash8}:run.model_summary#<path>]]"
    assert json_brief.path_citation("removed.bill_last.vif").endswith(
        "run.model_summary#removed.bill_last.vif]]"
    )


def test_a_truncated_json_artifact_says_so(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    store.put(
        "run.model_summary",
        {"coefficients": [{"feature": f"f{i}", "value": float(i)} for i in range(MAX_JSON_PATHS)]},
        ArtifactKind.json,
        "many coefficients",
    )
    brief = artifact_briefs(store, brief_for(ReportSection.conceptual_soundness))[0]
    assert brief.truncated is True
    assert brief.to_payload()["truncated"] is True


def test_a_figure_is_not_an_artifact_a_section_can_cite(tmp_path: Path) -> None:
    """A figure is evidence a reader looks at; there is no number in it to cite or to match."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("psi.max", 0.011, ArtifactKind.scalar, "the largest PSI")
    store.put("psi.figure", b"\x89PNG\r\n\x1a\n", ArtifactKind.figure, "a drift chart")
    brief = brief_for(ReportSection.data_integrity)
    assert [item.name for item in artifact_briefs(store, brief)] == ["psi.max"]
    # Even named outright -- which is how a finding's evidence reaches section 6 -- it is dropped.
    named = artifact_briefs(store, brief, extra=["psi.figure"])
    assert [item.name for item in named] == ["psi.max"]


def test_calibration_comes_first_only_on_a_rare_event(tmp_path: Path) -> None:
    """Spec 3.11's rule, read from the artifacts rather than from a constant in the prose."""
    store = ArtifactStore(tmp_path / "artifacts")
    assert calibration_before_discrimination(store) is False
    store.put("metrics.test.event_rate", 0.2246, ArtifactKind.scalar, "event rate")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    assert calibration_before_discrimination(store) is False
    rare = ArtifactStore(tmp_path / "rare")
    rare.put("metrics.test.event_rate", 0.0084, ArtifactKind.scalar, "event rate")
    rare.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    assert calibration_before_discrimination(rare) is True


def test_the_outcomes_brief_swaps_when_calibration_comes_first(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.event_rate", 0.0084, ArtifactKind.scalar, "event rate")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    briefs = {brief.section: brief for brief in ordered_briefs(store)}
    assert "calibration before discrimination" in briefs[ReportSection.outcomes].brief
    plain = {brief.section: brief for brief in ordered_briefs(ArtifactStore(tmp_path / "plain"))}
    assert "discrimination before calibration" in plain[ReportSection.outcomes].brief
    assert [brief.section for brief in ordered_briefs(store)] == list(SECTION_ORDER)


def test_a_brief_matches_exact_names_and_dotted_prefixes() -> None:
    brief = brief_for(ReportSection.data_integrity)
    assert brief.matches("psi.utilisation")
    assert brief.matches("leakage.overlap")
    assert not brief.matches("challenger.auc")
    assert brief_for(ReportSection.summary).matches("psi.max")
    assert not brief_for(ReportSection.summary).matches("psi.utilisation")


def test_an_artifact_brief_is_frozen_and_carries_its_own_citation() -> None:
    brief = ArtifactBrief(
        name="metrics.test.auc",
        hash8="4bb1344e",
        kind=ArtifactKind.scalar,
        value=0.7412,
        summary="auc",
    )
    assert brief.citation == "[[art:4bb1344e:metrics.test.auc]]"
    with pytest.raises(ValidationError):
        brief.value = 1.0  # type: ignore[misc]


# --- section 4's ordering: the declared use, then the event rate (D-098) ------------------------


def _rare(tmp_path: Path, name: str, rate: float) -> ArtifactStore:
    """A store carrying one event rate and the rule it is read against."""
    store = ArtifactStore(tmp_path / name)
    store.put("metrics.test.event_rate", rate, ArtifactKind.scalar, "event rate")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    return store


def _spec(use: Use | None) -> PackageSpec:
    """The credit package with one `use` declaration swapped in."""
    spec = load_package(CREDIT).spec
    return spec.model_copy(update={"use": use})


@pytest.mark.parametrize(
    ("use", "rate", "calibration_first", "reason"),
    [
        (Use.probability, 0.2246, True, OrderReason.declared_use),
        (Use.both, 0.2246, True, OrderReason.declared_use),
        (Use.ranking, 0.2246, False, OrderReason.event_rate),
        (Use.ranking, 0.0084, True, OrderReason.event_rate),
        (None, 0.2246, False, OrderReason.event_rate),
        (None, 0.0084, True, OrderReason.event_rate),
    ],
)
def test_the_declared_use_outranks_the_event_rate_and_the_reason_is_returned(
    tmp_path: Path, use: Use | None, rate: float, calibration_first: bool, reason: OrderReason
) -> None:
    """A common-rate model used for its probabilities leads with calibration; ranking does not."""
    store = _rare(tmp_path, f"{use}-{rate}", rate)
    order = section_four_order(store, _spec(use))
    assert order == SectionOrder(calibration_first=calibration_first, reason=reason)
    assert calibration_before_discrimination(store, _spec(use)) is calibration_first


def test_the_rule_artifact_is_withheld_from_the_section_the_declared_use_ordered(
    tmp_path: Path,
) -> None:
    """The surest way not to be cited as a reason is not to be handed to the drafter (D-098)."""
    store = _rare(tmp_path, "declared", 0.2246)
    by_use = {b.section: b for b in ordered_briefs(store, _spec(Use.probability))}[
        ReportSection.outcomes
    ]
    assert "rule." not in by_use.scalars
    assert CALIBRATION_FIRST_RULE not in {item.name for item in artifact_briefs(store, by_use)}
    assert "package.yaml declares" in by_use.brief
    assert f"do not cite {CALIBRATION_FIRST_RULE}" in by_use.brief

    by_rate = {b.section: b for b in ordered_briefs(store, _spec(Use.ranking))}[
        ReportSection.outcomes
    ]
    assert "rule." in by_rate.scalars
    assert CALIBRATION_FIRST_RULE in {item.name for item in artifact_briefs(store, by_rate)}
    assert CALIBRATION_FIRST_RULE in by_rate.brief


def test_both_shipped_subjects_declare_what_their_output_is_used_for() -> None:
    """`credit_default` ranks applicants; `msr_prepayment`'s hazard is multiplied by a balance."""
    assert load_package(CREDIT).spec.use is Use.ranking
    assert load_package(MSR).spec.use is Use.probability


def test_a_package_may_leave_use_undeclared_or_null() -> None:
    """Optional and nullable, so every pre-D-098 package keeps the Phase 8 behaviour."""
    spec = load_package(CREDIT).spec
    assert spec.model_copy(update={"use": None}).use is None
    assert PackageSpec.model_validate({**spec.model_dump(mode="json"), "use": None}).use is None


# --- section 4 points at the threshold table rather than assembling one (D-092) -----------------


def test_section_four_is_offered_every_threshold_and_psi_scalar_and_the_threshold_table() -> None:
    """The selector that made PSI invisible to the section that reports the declared bounds."""
    brief = brief_for(ReportSection.outcomes)
    assert brief.matches("threshold.L2.overlap")
    assert brief.matches("threshold.package.psi.max")
    assert brief.matches("psi.max")
    assert brief.matches("psi.age")
    assert THRESHOLD_TABLE in brief.tables
    assert f"[[table:{THRESHOLD_TABLE}]]" in brief.brief
    assert "do **not** assemble that table yourself" in brief.brief


def test_the_runtime_cap_is_citable_from_the_summary_and_from_no_threshold_family() -> None:
    """`runtime.max_seconds` left `threshold.*`; section 1 still states the cap (D-092)."""
    assert brief_for(ReportSection.summary).matches(MAX_SECONDS_NAME)
    assert not brief_for(ReportSection.outcomes).matches(MAX_SECONDS_NAME)


def test_section_two_is_offered_the_sign_check_and_the_ablation(store: ArtifactStore) -> None:
    """The evidence for the paragraph section 2 wrote from inference alone (D-095)."""
    brief = brief_for(ReportSection.conceptual_soundness)
    assert brief.matches("sign_check.utilisation.agrees")
    assert brief.matches("sign_check.n_disagreements")
    assert brief.matches("ablation.utilisation.delta_auc")
    assert "univariate direction" in brief.brief
    assert "ablation delta" in brief.brief
    assert "do not\ndescribe anything here as a finding" in brief.brief


def test_section_three_is_told_which_bound_each_overlap_arm_is_read_against() -> None:
    """The instruction that D-091's new artifact exists to make followable."""
    brief = brief_for(ReportSection.data_integrity)
    assert brief.matches(FEATURE_OVERLAP_BOUND)
    assert FEATURE_OVERLAP_BOUND in brief.brief
    assert "do not compare a feature-vector overlap with the declared\nthreshold" in brief.brief


def test_section_six_is_asked_for_the_open_items_subsection() -> None:
    """D-096: the heading, an owner per line, and the word finding forbidden of an open item."""
    brief = brief_for(ReportSection.findings)
    assert OPEN_ITEMS_HEADING in brief.brief
    assert "model developer" in brief.brief
    assert "Never write the word finding about an open item." in brief.brief
    assert "the ones listed for you at\nthe end of this prompt and no others" in brief.brief


# --- the Phase 9 follow-up 4 additions ----------------------------------------------------------


def _threshold_store(tmp_path: Path) -> ArtifactStore:
    """A store shaped like a real run's: declared bounds, the table, and the recomputed values."""
    store = ArtifactStore(tmp_path / "artifacts")
    rows = [
        {"metric": "auc", "split": "test", "bound": "min 0.7", "value": 0.755, "result": "pass"},
        {"metric": "brier", "split": "test", "bound": "max 0.2", "value": 0.1385, "result": "pass"},
        {"metric": "psi", "split": "", "bound": "max 0.25", "value": 0.0031, "result": "pass"},
    ]
    store.put(THRESHOLD_TABLE, rows, ArtifactKind.table, "declared bounds")
    for name, value in (
        ("threshold.package.auc.test.min", 0.7),
        ("threshold.package.brier.test.max", 0.2),
        ("threshold.package.psi.max", 0.25),
        ("metrics.test.auc", 0.755),
        ("metrics.test.brier", 0.1385),
        ("psi.max", 0.0031),
    ):
        store.put(name, value, ArtifactKind.scalar, name)
    return store


def test_every_declared_bound_brings_its_recomputed_value_to_the_section_shown_it(
    tmp_path: Path,
) -> None:
    """D-100, stated over every declared threshold rather than over the one that went missing."""
    store = _threshold_store(tmp_path)
    rows = store.load(THRESHOLD_TABLE)
    assert isinstance(rows, list)
    for section in SECTION_ORDER:
        brief = brief_for(section)
        selected = {item.name for item in artifact_briefs(store, brief)}
        for row in rows:
            stem = f"threshold.package.{row['metric']}"
            if row["split"]:
                stem = f"{stem}.{row['split']}"
            shown = brief.matches(f"{stem}.min") or brief.matches(f"{stem}.max")
            name = metric_artifact_name(str(row["metric"]), str(row["split"]) or None)
            if shown and name is not None:
                assert name in selected, (section, name)


def test_the_monitoring_section_is_shown_the_test_brier_it_said_was_not_carried(
    tmp_path: Path,
) -> None:
    """The fourth live report's own sentence: "no recomputed test Brier value is carried"."""
    store = _threshold_store(tmp_path)
    brief = brief_for(ReportSection.monitoring)
    assert brief.matches("threshold.package.brier.test.max")
    assert not brief.matches("metrics.test.brier"), "the selector still does not list it by name"
    assert "metrics.test.brier" in recomputed_for_declared_bounds(store, brief)
    assert "metrics.test.brier" in {item.name for item in artifact_briefs(store, brief)}


def test_a_run_with_no_threshold_table_selects_nothing_extra(tmp_path: Path) -> None:
    """A package that declares no threshold: the derivation is empty rather than an error."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.755, ArtifactKind.scalar, "auc")
    assert recomputed_for_declared_bounds(store, brief_for(ReportSection.monitoring)) == set()


def test_the_drafter_is_told_its_artifact_list_is_a_selection_and_not_the_store() -> None:
    """D-100's standing rule, which no section brief has to repeat."""
    from quaestor.report.drafter import DRAFT_INSTRUCTION

    assert "this section's selection, not the store" in DRAFT_INSTRUCTION
    assert "not carried" in DRAFT_INSTRUCTION


def test_an_integral_value_reaches_the_prompt_as_an_integer(tmp_path: Path) -> None:
    """D-106: a count of features is `0`, and a drafter shown `0.0` writes "flags 0.0 features"."""
    assert as_written(0.0) == 0
    assert isinstance(as_written(900.0), int)
    assert as_written(0.7412) == 0.7412
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("profile.train.n", 3500, ArtifactKind.scalar, "rows")
    store.put("metrics.test.auc", 0.74801204, ArtifactKind.scalar, "auc")
    summary = artifact_briefs(store, brief_for(ReportSection.summary))
    payloads = {item.name: item.to_payload() for item in summary}
    assert payloads["profile.train.n"]["value"] == 3500
    assert isinstance(payloads["profile.train.n"]["value"], int)
    assert payloads["metrics.test.auc"]["value"] == pytest.approx(0.748)


# --- section 7 is told how section 4 ordered itself (D-104) -------------------------------------


@pytest.mark.parametrize(
    ("order", "expected", "forbidden"),
    [
        (SectionOrder(False, OrderReason.event_rate), "discrimination before calibration", None),
        (SectionOrder(True, OrderReason.event_rate), "calibration before discrimination", None),
        (
            SectionOrder(True, OrderReason.declared_use),
            "calibration before discrimination",
            CALIBRATION_FIRST_RULE,
        ),
        (SectionOrder(False, OrderReason.declared_use), "discrimination before calibration", None),
    ],
)
def test_the_monitoring_brief_states_what_section_four_did(
    order: SectionOrder, expected: str, forbidden: str | None
) -> None:
    brief = monitoring_brief(brief_for(ReportSection.monitoring), order)
    assert expected in brief.brief
    if not order.calibration_first:
        assert "led with calibration" in brief.brief, "the sentence the fourth run wrote anyway"
    if forbidden is not None:
        assert forbidden not in brief.brief


def test_ordered_briefs_gives_section_seven_the_same_order_it_gave_section_four(
    tmp_path: Path,
) -> None:
    """The two sections cannot disagree, because one function fills both (D-104)."""
    store = _rare(tmp_path, "metrics.test.event_rate", 0.2246)
    briefs = {brief.section: brief for brief in ordered_briefs(store, load_package(CREDIT).spec)}
    assert "discrimination before calibration" in briefs[ReportSection.outcomes].brief
    assert "Section 4 of this report reported **discrimination before calibration**" in (
        briefs[ReportSection.monitoring].brief
    )


# --- section 6 with no finding does not enumerate what it reviewed (D-103) ----------------------


def test_section_six_is_forbidden_from_listing_reviews_it_did_not_run() -> None:
    brief = brief_for(ReportSection.findings)
    assert "Do **not** describe what\nwas reviewed" in brief.brief
    assert "input data lineage" in brief.brief


def test_the_no_findings_block_says_the_renderer_prints_the_enumeration() -> None:
    from quaestor.report.drafter import Drafter

    prompt = Drafter(None, package="p", version="1.0").prompt(  # type: ignore[arg-type]
        brief_for(ReportSection.findings)
    )
    assert "do not describe what was reviewed" in prompt
    assert "checks that ran and raised no candidate" in prompt


# --- the executed follow-up steps reach the prose (D-101, D-102) --------------------------------


def _slice_store(tmp_path: Path, *, gap: float, share: float) -> ArtifactStore:
    """A store holding one sub-population's reading and the two bounds it is read against."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put(SLICE_GAP_BOUND, 0.08, ArtifactKind.scalar, "the slice gap bound")
    store.put(SLICE_SHARE_FLOOR, 0.10, ArtifactKind.scalar, "the slice size floor")
    store.put("metrics.test.sub.s_eq_0.auc", 0.5875, ArtifactKind.scalar, "auc on the slice")
    store.put("metrics.test.sub.s_eq_0.auc_gap", gap, ArtifactKind.scalar, "the gap")
    store.put("metrics.test.sub.s_eq_0.share", share, ArtifactKind.scalar, "the share")
    return store


def test_a_slice_materially_worse_than_the_headline_is_material(tmp_path: Path) -> None:
    """The fourth live run's own numbers: 0.755 - 0.587 on 6,048 of 9,000 rows (D-102)."""
    store = _slice_store(tmp_path, gap=0.1676, share=0.672)
    follow_up = follow_up_for(
        store, "compute_metrics", {"splits": ["test"]}, "does it hold?", sorted(store.names())
    )
    assert follow_up.material is True
    assert SLICE_GAP_BOUND in follow_up.detail
    assert "open items" in follow_up.detail


def test_a_slice_inside_the_bound_is_supporting_evidence(tmp_path: Path) -> None:
    """0.044 for the high-limit half and 0.007 for the low-limit half, neither material."""
    store = _slice_store(tmp_path, gap=0.0436, share=0.513)
    follow_up = follow_up_for(store, "compute_metrics", {}, "why", sorted(store.names()))
    assert follow_up.material is False
    assert "supporting evidence" in follow_up.detail


def test_a_slice_below_the_size_floor_is_never_material(tmp_path: Path) -> None:
    """However far it falls: a slice of a twentieth of the split is sampling noise (D-102)."""
    store = _slice_store(tmp_path, gap=0.4, share=0.05)
    follow_up = follow_up_for(store, "compute_metrics", {}, "why", sorted(store.names()))
    assert follow_up.material is False
    assert SLICE_SHARE_FLOOR in follow_up.detail


def test_a_step_with_no_slice_reading_is_reported_and_never_material(tmp_path: Path) -> None:
    """A re-profiled feature has no bound to be read against, so it raises no open item."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("profile.test.missing.age", 0.0, ArtifactKind.scalar, "missingness")
    follow_up = follow_up_for(
        store, "profile_data", {}, "did age drift?", ["profile.test.missing.age"]
    )
    assert follow_up.material is False
    assert follow_up.detail == ""
    assert follow_up.artifacts == ("profile.test.missing.age",)


def test_the_summary_and_the_findings_section_never_carry_the_follow_up_subsection(
    tmp_path: Path,
) -> None:
    """Section 1 is derivative and section 6 reports a material step as an open item (D-101)."""
    store = _slice_store(tmp_path, gap=0.1676, share=0.672)
    follow_up = follow_up_for(store, "compute_metrics", {}, "why", sorted(store.names()))
    briefs = ordered_briefs(store, load_package(CREDIT).spec)
    sections = sections_for_follow_up(briefs, follow_up)
    assert ReportSection.outcomes in sections
    assert ReportSection.summary not in sections
    assert ReportSection.findings not in sections
    assert brief_for(ReportSection.summary).matches("metrics.test.sub.s_eq_0.auc"), (
        "section 1 is excluded by the rule and not by its selector"
    )


def test_the_follow_up_block_names_the_step_s_own_question(tmp_path: Path) -> None:
    """The half the fourth live run withheld: the step's `why` never reached any prompt (D-101)."""
    from quaestor.report.drafter import Drafter

    store = _slice_store(tmp_path, gap=0.1676, share=0.672)
    follow_up = follow_up_for(
        store,
        "compute_metrics",
        {"splits": ["test"], "subpopulation": {"column": "delinq_count_6m", "rule": "equals:0"}},
        "discrimination often collapses on the never-delinquent majority segment",
        sorted(store.names()),
    )
    drafter = Drafter(None, package="credit_default", version="1.0")  # type: ignore[arg-type]
    outcomes = drafter.prompt(brief_for(ReportSection.outcomes), follow_ups=[follow_up])
    assert "never-delinquent majority segment" in outcomes
    assert "delinq_count_6m" in outcomes
    assert FOLLOW_UPS_HEADING in outcomes
    findings = drafter.prompt(brief_for(ReportSection.findings), follow_ups=[follow_up])
    assert FOLLOW_UPS_HEADING not in findings
    assert OPEN_ITEMS_HEADING in findings
    assert "what the model\ndiscriminates on inside that segment" in findings
    assert "never-delinquent majority segment" not in findings, (
        "since D-173 section 6 is handed its open items, not the loop's steps: the step's own "
        "question belongs to the section that computed it"
    )


# --- Phase 9 follow-up 5: the prompt, the challenger and the slice tables ------------------------


def test_an_integral_value_reaches_the_prompt_unrounded(tmp_path: Path) -> None:
    """D-110: 10,158 rows is 10158 in the prompt, not 10160, and a claim of it verifies."""
    assert prompt_value(10158.0) == 10158
    assert prompt_value(0.74801204) == pytest.approx(0.748)
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.train.sub.limit_bal_low.n", 10158, ArtifactKind.scalar, "rows in the slice")
    store.put("metrics.test.auc", 0.74801204, ArtifactKind.scalar, "auc on test")
    briefs = {
        item.name: item.to_payload()
        for item in artifact_briefs(store, brief_for(ReportSection.outcomes))
    }
    shown = briefs["metrics.train.sub.limit_bal_low.n"]["value"]
    assert shown == 10158
    assert isinstance(shown, int)
    claim = Claim(
        text=f"The slice holds {shown} rows.",
        value=float(shown),
        unit=Unit.count,
        section=ReportSection.outcomes,
        source=ClaimSource.report,
        citation=store.artifact("metrics.train.sub.limit_bal_low.n").citation(),
    )
    assert match_claim(claim, store).claim.status is ClaimStatus.verified


def test_the_monitoring_brief_says_a_challenger_was_compared(tmp_path: Path) -> None:
    """D-114: section 7 wrote that benchmarking "was not part of this validation"."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.event_rate", 0.2246, ArtifactKind.scalar, "event rate")
    order = SectionOrder(False, OrderReason.event_rate)
    without = monitoring_brief(brief_for(ReportSection.monitoring), order, store)
    assert "challenger" not in without.brief
    store.put(CHALLENGER_DELTA, -0.012, ArtifactKind.scalar, "challenger AUC minus champion's")
    with_challenger = monitoring_brief(brief_for(ReportSection.monitoring), order, store)
    assert "A challenger model was compared" in with_challenger.brief
    assert "was not part of it" in with_challenger.brief
    assert monitoring_brief(brief_for(ReportSection.monitoring), order).brief == without.brief


def test_the_drafter_is_told_the_citation_carries_the_logical_name() -> None:
    """D-113: "by up to threshold.O1.slice_auc_gap at 0.08" is the name written twice."""
    from quaestor.report.drafter import DRAFT_INSTRUCTION

    assert "Do not write an artifact's logical name in the prose" in DRAFT_INSTRUCTION


def test_a_section_is_offered_the_slice_tables_its_prefix_names(tmp_path: Path) -> None:
    """D-115: `metrics.<split>.sub.<slug>` is a family one run names, so the entry is a prefix."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.755, ArtifactKind.scalar, "auc on test")
    store.put(
        "metrics.test.sub.limit_bal_low",
        [{"metric": "auc", "value": 0.7477}, {"metric": "share", "value": 0.487}],
        ArtifactKind.table,
        "every metric on the limit_bal below_median slice of test",
    )
    outcomes = brief_for(ReportSection.outcomes)
    assert outcomes.wants_table("metrics.test.sub.limit_bal_low")
    assert not brief_for(ReportSection.sensitivity).wants_table("metrics.test.sub.limit_bal_low")
    shown = {item.name: item for item in artifact_briefs(store, outcomes)}
    assert shown["metrics.test.sub.limit_bal_low"].to_payload()["directive"] == (
        "[[table:metrics.test.sub.limit_bal_low]]"
    )


def test_the_follow_up_block_gives_the_slice_rule_and_the_table_and_not_the_enumeration(
    tmp_path: Path,
) -> None:
    """D-112 and D-115: the rule reaches the prose as code, the metrics as a directive."""
    from quaestor.report.drafter import Drafter

    store = _slice_store(tmp_path, gap=0.1238, share=0.775)
    store.put(
        "metrics.test.sub.s_eq_0",
        [{"metric": "auc", "value": 0.6312}, {"metric": "share", "value": 0.775}],
        ArtifactKind.table,
        "every metric on the delinq_last equals:0 slice of test",
    )
    follow_up = follow_up_for(
        store,
        "compute_metrics",
        {"splits": ["test"], "subpopulation": {"column": "delinq_last", "rule": "equals:0"}},
        "a delinquency-driven score may lose its edge among clean payers",
        sorted(store.names()),
    )
    assert follow_up.slice_rule == "delinq_last == 0"
    assert follow_up.tables == ("metrics.test.sub.s_eq_0",)
    drafter = Drafter(None, package="credit_default", version="1.0")  # type: ignore[arg-type]
    prompt = drafter.prompt(brief_for(ReportSection.outcomes), follow_ups=[follow_up])
    assert "`delinq_last == 0`" in prompt
    assert "[[table:metrics.test.sub.s_eq_0]]" in prompt
    assert "Do **not** enumerate the step's metrics in prose" in prompt
    items = open_items(store, DEFAULT_THRESHOLDS)
    findings = drafter.prompt(
        brief_for(ReportSection.findings), follow_ups=[follow_up], items=items
    )
    assert "`delinq_last == 0`" in findings, (
        "section 6 names the segment by the loop's own expression, which the minting rule cannot "
        "read back out of the artifact stem and the open-items block joins on (D-173)"
    )


def test_a_follow_up_that_asked_for_no_slice_carries_no_rule(tmp_path: Path) -> None:
    """`slice_rule` is empty rather than invented for a step that sliced nothing."""
    store = _slice_store(tmp_path, gap=0.01, share=0.5)
    follow_up = follow_up_for(
        store, "profile_data", {"splits": ["test"]}, "why", ["profile.test.n"]
    )
    assert follow_up.slice_rule == ""
    assert follow_up.tables == ()
