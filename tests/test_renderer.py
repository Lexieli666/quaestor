"""Phase 8: the renderer -- front matter, renderer blocks, four appendices, four refusals.

Everything here is built by hand rather than run end to end, so that each piece of the report can
be wrong on its own: a table directive naming nothing, a finding the drafter did not write about,
a front matter that fails its schema, a number in the prose that no claim covers.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.errors import ReportSchemaError
from quaestor.findings import (
    CandidateNotPromoted,
    DefectClass,
    Finding,
    FindingCandidate,
    FindingsDocument,
    Severity,
)
from quaestor.package import load_package
from quaestor.report.renderer import (
    APPENDICES,
    NotChecked,
    ReportInputs,
    check_report,
    drafted_body,
    expand_tables,
    front_matter,
    render_report,
    scope_block,
    uncovered_numbers,
    write_report,
)
from quaestor.report.sections import FOLLOW_UPS_HEADING, FollowUp
from quaestor.trace import TraceReader, TraceWriter
from quaestor.verifier import (
    ClaimsDocument,
    ClaimSource,
    ClaimStatus,
    VerifiedClaim,
    extract,
    match_claims,
)
from quaestor.vocab import Configuration, ReportSection
from reportsupport import SectionFake

REPO_ROOT = Path(__file__).resolve().parents[1]
CREDIT = REPO_ROOT / "subjects" / "credit_default"
GENERATED = datetime(2026, 9, 8, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with a scalar and a table, which is all the renderer needs to be exercised."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar, "auc on test")
    store.put(
        "deciles.test",
        [{"decile": 1, "lift": 2.24}, {"decile": 2, "lift": 1.58}],
        ArtifactKind.table,
        "decile separation on test",
    )
    store.put(
        "run.status",
        {"memory_cap": "unenforced", "memory_cap_mb": 4096},
        ArtifactKind.json,
        "how the subject's subprocess ended",
    )
    store.put("run.duration_s", 1.23, ArtifactKind.scalar, "subject wall-clock seconds")
    return store


def inputs_for(
    store: ArtifactStore,
    tmp_path: Path,
    *,
    sections: dict[ReportSection, str] | None = None,
    findings: FindingsDocument | None = None,
    configuration: Configuration = Configuration.full_agent,
    not_checked: tuple[NotChecked, ...] = (),
) -> ReportInputs:
    """Assemble a renderable report from one section of prose and nothing else."""
    package = load_package(CREDIT)
    prose = sections or {
        ReportSection.summary: f"The AUC is 0.7412 {store.artifact('metrics.test.auc').citation()}."
    }
    extraction = extract(ReportSection.summary, prose.get(ReportSection.summary, ""), SectionFake())
    matches = match_claims(extraction.claims, store, unattributed=extraction.unattributed_ids)
    claims = ClaimsDocument.build(
        package=package.spec.name,
        version=package.spec.version,
        configuration=configuration,
        run_id="run-0001",
        pre_repair=[match.claim for match in matches],
        exclusions=extraction.exclusions,
    )
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="run-0001")
    trace.emit("tool_call", tool="run_model", args_hash="a", duration_s=1.0, artifacts=[], ok=True)
    trace.llm_call(purpose="draft", model="fake", tokens_in=10, tokens_out=5, cost_usd=0.01)
    trace.llm_call(purpose="reask", model="fake")
    return ReportInputs(
        package=package,
        configuration=configuration,
        model="fake",
        run_id="run-0001",
        data_mode="synthetic",
        synthetic_n=5000,
        sections=prose,
        claims=claims,
        findings=findings
        or FindingsDocument.build(
            package=package.spec.name,
            version=package.spec.version,
            configuration=configuration,
            run_id="run-0001",
            findings=[],
        ),
        store=store,
        events=list(TraceReader(trace.path)),
        not_checked=not_checked,
        quaestor_version="0.1.0.dev0",
        generated=GENERATED,
    )


def one_finding(store: ArtifactStore) -> Finding:
    """One `E1` finding over the fixture store's scalar."""
    return Finding.from_candidates(
        [
            FindingCandidate(
                defect_class=DefectClass.E1,
                evidence=[store.artifact("metrics.test.auc").hash],
                detail="the challenger leads the champion",
                suggested_severity=Severity.low,
                tool="challenger_compare",
            )
        ],
        store=store,
    )


# --- front matter and the scope block ---------------------------------------------------------


def test_the_front_matter_carries_every_key_the_schema_requires(
    store: ArtifactStore, tmp_path: Path
) -> None:
    front = front_matter(inputs_for(store, tmp_path))
    assert front["schema_version"] == 1
    assert front["quaestor_version"] == "0.1.0.dev0"
    assert front["model_type"] == "binary_classification"
    assert front["data_mode"] == "synthetic" and front["synthetic_n"] == 5000
    assert front["generated"] == "2026-09-08T12:00:00Z"
    assert front["illustrative"] is False
    assert list(front)[:4] == ["schema_version", "quaestor_version", "package", "version"]


def test_the_rendered_front_matter_parses_back_as_yaml(
    store: ArtifactStore, tmp_path: Path
) -> None:
    report = render_report(inputs_for(store, tmp_path))
    parsed = yaml.safe_load(report.split("---\n")[1])
    assert parsed["version"] == "1.0"
    assert parsed["generated"] == "2026-09-08T12:00:00Z"
    assert parsed["n_findings_by_severity"] == {"high": 0, "medium": 0, "low": 0, "info": 0}
    assert isinstance(parsed["grounding_precision_pre"], float)


def test_a_real_run_with_no_synthetic_n_omits_the_key(store: ArtifactStore, tmp_path: Path) -> None:
    inputs = inputs_for(store, tmp_path)
    inputs.data_mode = "real"
    inputs.synthetic_n = None
    front = front_matter(inputs)
    assert "synthetic_n" not in front
    assert "real," in scope_block(inputs)


def test_the_scope_block_is_the_first_thing_under_section_one(
    store: ArtifactStore, tmp_path: Path
) -> None:
    report = render_report(inputs_for(store, tmp_path))
    body = report.split("## 1. Summary and scope\n", 1)[1]
    assert body.lstrip().startswith("<!-- quaestor:renderer:begin scope -->")
    block = scope_block(inputs_for(store, tmp_path))
    assert "`credit_default` v1.0" in block
    assert "synthetic, n = 5000" in block
    assert "0 / 0 / 0 / 0" in block
    assert "→" in block


# --- renderer blocks --------------------------------------------------------------------------


def test_a_table_directive_becomes_a_renderer_block_with_a_caption_and_a_citation(
    store: ArtifactStore,
) -> None:
    expanded = expand_tables("Before.\n[[table:deciles.test]]\nAfter.", store)
    assert "<!-- quaestor:renderer:begin table deciles.test -->" in expanded
    assert "Decile separation on test [[art:" in expanded
    assert "| decile | lift |" in expanded
    assert "| 1 | 2.24 |" in expanded
    assert expanded.startswith("Before.") and expanded.endswith("After.")


def test_a_directive_naming_something_that_is_not_a_table_is_marked_not_dropped(
    store: ArtifactStore,
) -> None:
    assert (
        expand_tables("[[table:metrics.test.auc]]", store) == "⟦unverified: table metrics.test.auc⟧"
    )
    assert expand_tables("[[table:no.such.name]]", store) == "⟦unverified: table no.such.name⟧"


def test_a_directive_that_is_not_alone_on_its_line_is_left_for_the_citation_check(
    store: ArtifactStore,
) -> None:
    assert (
        expand_tables("see [[table:deciles.test]] there", store)
        == "see [[table:deciles.test]] there"
    )


# --- section 6 ------------------------------------------------------------------------------


def test_the_renderer_supplies_a_heading_the_drafter_did_not_write(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """D-071: every finding appears once, under the id the findings document assigned."""
    document = FindingsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.full_agent,
        run_id="run-0001",
        findings=[one_finding(store)],
    )
    inputs = inputs_for(
        store,
        tmp_path,
        sections={ReportSection.findings: "The findings are listed below."},
        findings=document,
    )
    report = render_report(inputs)
    assert "### F-001 · E1 effective challenge · severity **low**" in report
    assert "the challenger leads the champion" in report
    assert "Candidates raised and not promoted: none." in report


def test_the_drafted_body_of_a_finding_is_kept_under_its_heading(
    store: ArtifactStore, tmp_path: Path
) -> None:
    document = FindingsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.full_agent,
        run_id="run-0001",
        findings=[one_finding(store)],
    )
    heading = "### F-001 · E1 effective challenge · severity **low**"
    drafted = f"An opening sentence.\n{heading}\n**A challenger wins.**\nAnd the reason why."
    report = render_report(
        inputs_for(store, tmp_path, sections={ReportSection.findings: drafted}, findings=document)
    )
    assert "An opening sentence." in report
    assert "**A challenger wins.**" in report
    assert report.count(heading) == 1
    assert "the challenger leads the champion" not in report


def test_a_candidate_that_was_not_promoted_is_named_in_the_section(
    store: ArtifactStore, tmp_path: Path
) -> None:
    document = FindingsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.full_agent,
        run_id="run-0001",
        findings=[],
        candidates_not_promoted=[
            CandidateNotPromoted(
                defect_class=DefectClass.T1,
                tool="compute_metrics",
                evidence=[store.artifact("metrics.test.auc").hash[:8]],
                reason="the declared threshold is met on every split the package names",
            )
        ],
        checks_without_candidates={"check_leakage": [DefectClass.L1, DefectClass.L2]},
    )
    report = render_report(inputs_for(store, tmp_path, findings=document))
    assert "Candidates raised and not promoted: `T1` from `compute_metrics`" in report
    assert "Checks that ran and raised no candidate: `check_leakage` (L1, L2)." in report


# --- the appendices --------------------------------------------------------------------------


def test_appendix_a_prints_both_figures_the_exclusions_and_every_claim(
    store: ArtifactStore, tmp_path: Path
) -> None:
    report = render_report(inputs_for(store, tmp_path))
    appendix = report.split(APPENDICES[0], 1)[1].split(APPENDICES[1], 1)[0]
    assert "Grounding precision 1.0000 before repair (1 of 1 claims verified)" in appendix
    assert "Per section (post-repair): summary 1/1." in appendix
    assert "Developer claims:" in appendix
    assert "Excluded numeric tokens (not claims): citation_hash" in appendix
    assert "| 1 | summary |" in appendix
    assert "`[[art:" in appendix
    assert "verified" in appendix


def test_appendix_a_strips_citations_out_of_the_text_column(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """A sentence cut at sixty characters must not leave half a citation in the table."""
    report = render_report(inputs_for(store, tmp_path))
    row = [line for line in report.splitlines() if line.startswith("| 1 | summary |")][0]
    assert "The AUC is 0.7412 ." in row
    assert row.count("[[art:") == 1


def test_appendix_b_indexes_what_the_report_cites_with_its_caption(
    store: ArtifactStore, tmp_path: Path
) -> None:
    report = render_report(inputs_for(store, tmp_path))
    appendix = report.split(APPENDICES[1], 1)[1].split(APPENDICES[2], 1)[0]
    assert "| logical name | hash | kind | value | summary |" in appendix
    assert "| `metrics.test.auc` |" in appendix
    assert "auc on test" in appendix
    assert f"The store holds {len(store)} artifacts" in appendix


def test_appendix_c_is_computed_from_the_trace(store: ArtifactStore, tmp_path: Path) -> None:
    report = render_report(inputs_for(store, tmp_path))
    appendix = report.split(APPENDICES[2], 1)[1].split(APPENDICES[3], 1)[0]
    assert "| tool calls | 1 (run_model 1) |" in appendix
    assert "| LLM calls | 2 (draft 1, reask 1) |" in appendix
    assert "| re-asks | 1 |" in appendix
    assert "| repair rounds | 0 |" in appendix
    assert "| tokens in / out | 10 / 5 |" in appendix
    assert "| notional cost (USD) | 0.0100 |" in appendix
    assert "| subject run (s) | 1.23 |" in appendix
    assert "| memory cap | unenforced (RLIMIT_AS 4096 MB) |" in appendix
    assert "[[art:" not in appendix


def test_appendix_c_carries_the_manifest_row_only_when_a_manifest_was_verified(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """The row is guarded on the artifact, not on the data mode, so synthetic reports do not move.

    `pipeline._record_manifest` writes `data.manifest` when and only when the loader verified one
    (D-162), so a store without it is every `--synthetic` run and every package that declares
    none, and neither may print a "verified" line it did not earn.
    """
    silent = render_report(inputs_for(store, tmp_path)).split(APPENDICES[2], 1)[1]
    assert "data manifest" not in silent.split(APPENDICES[3], 1)[0]

    store.put(
        "data.manifest",
        [
            {"file": "train.csv", "sha256": "a" * 64, "verified": True},
            {"file": "test.csv", "sha256": "b" * 64, "verified": True},
        ],
        ArtifactKind.table,
        "the files data.manifest declares, each verified against its SHA-256 before the run",
    )
    appendix = render_report(inputs_for(store, tmp_path)).split(APPENDICES[2], 1)[1]
    appendix = appendix.split(APPENDICES[3], 1)[0]
    assert (
        "| data manifest | verified: 2 file(s) against package.yaml (see data.manifest) |"
        in appendix
    )
    assert "[[art:" not in appendix


def test_appendix_d_says_what_did_not_run(store: ArtifactStore, tmp_path: Path) -> None:
    rows = (NotChecked("`run_scenarios` (X1)", "not applicable to `binary_classification`"),)
    report = render_report(inputs_for(store, tmp_path, not_checked=rows))
    appendix = report.split(APPENDICES[3], 1)[1]
    assert "| `run_scenarios` (X1) | not applicable to `binary_classification` |" in appendix
    plain = render_report(inputs_for(store, tmp_path))
    assert "| nothing | every check this package supports ran |" in plain


# --- the refusals -----------------------------------------------------------------------------


def test_the_renderer_refuses_front_matter_that_does_not_validate(
    store: ArtifactStore, tmp_path: Path
) -> None:
    inputs = inputs_for(store, tmp_path)
    inputs.quaestor_version = "not a version"
    with pytest.raises(ReportSchemaError, match="front matter"):
        render_report(inputs)


def test_the_renderer_refuses_a_number_the_claims_do_not_cover_under_full_agent(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """The wrapper rule: a number nothing accounts for is not a report this renderer writes."""
    inputs = inputs_for(store, tmp_path)
    inputs.sections = {**inputs.sections, ReportSection.monitoring: "Track the AUC above 0.70."}
    with pytest.raises(ReportSchemaError, match="0.70"):
        render_report(inputs)


def test_the_same_report_is_written_under_rules_only(store: ArtifactStore, tmp_path: Path) -> None:
    """The wrapper rule binds `full_agent`; the other arms are checked but not refused for it."""
    inputs = inputs_for(store, tmp_path, configuration=Configuration.rules_only)
    inputs.sections = {**inputs.sections, ReportSection.monitoring: "Track the AUC above 0.70."}
    assert "0.70" in render_report(inputs)


def test_a_report_missing_an_appendix_is_reported_by_check_report(
    store: ArtifactStore, tmp_path: Path
) -> None:
    inputs = inputs_for(store, tmp_path)
    report = render_report(inputs)
    truncated = report.split(APPENDICES[2], 1)[0]
    problems = check_report(truncated, inputs.configuration, inputs.claims.post_repair)
    assert any(APPENDICES[2] in problem for problem in problems)


def test_appendix_a_counts_the_developer_claims_that_verified(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """Under `--data` the declared numbers are ordinary claims and the appendix says how many."""
    inputs = inputs_for(store, tmp_path)
    declared = VerifiedClaim(
        text="AUC on test is 0.74",
        value=0.74,
        metric="auc",
        section=ReportSection.outcomes,
        source=ClaimSource.developer,
        citation=store.artifact("metrics.test.auc").citation(),
        status=ClaimStatus.verified,
        artifact_value=0.7412,
    )
    inputs.claims = ClaimsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=inputs.configuration,
        run_id="run-0001",
        pre_repair=inputs.claims.pre_repair,
        developer_claims=[declared],
    )
    report = render_report(inputs)
    assert "Developer claims: 1 of 1 declared in `package.yaml` verify" in report


def test_write_report_writes_the_file_and_returns_its_path(
    store: ArtifactStore, tmp_path: Path
) -> None:
    path = write_report(inputs_for(store, tmp_path), tmp_path / "out" / "report.md")
    assert path.is_file()
    assert path.read_text(encoding="utf-8").startswith("---\n")


def test_check_report_agrees_with_the_renderer_on_its_own_output(
    store: ArtifactStore, tmp_path: Path
) -> None:
    inputs = inputs_for(store, tmp_path)
    report = render_report(inputs)
    assert check_report(report, inputs.configuration, inputs.claims.post_repair) == []


def test_an_unverified_claim_that_nothing_wrapped_is_reported(
    store: ArtifactStore, tmp_path: Path
) -> None:
    inputs = inputs_for(store, tmp_path)
    report = render_report(inputs)
    unverified = inputs.claims.post_repair[0].model_copy(
        update={"status": ClaimStatus.mismatch, "value": 0.7412}
    )
    problems = check_report(report, inputs.configuration, [unverified])
    assert any("is not wrapped" in problem for problem in problems)


# --- the two helpers the pipeline and the tests share -------------------------------------------


def test_uncovered_numbers_counts_only_what_the_pre_pass_would_have_counted() -> None:
    """A citation's hash, a feature name in backticks and a wrapped number are all accounted for."""
    body = (
        "The AUC is 0.7412 [[art:4bb1344e:metrics.test.auc]].\n"
        "The Brier score is 0.68.\n"
        "The feature `bill_mean_6m` was kept.\n"
    )
    verified = VerifiedClaim(
        text="The AUC is 0.7412 [[art:4bb1344e:metrics.test.auc]].",
        value=0.7412,
        section=ReportSection.summary,
        status=ClaimStatus.verified,
    )
    assert uncovered_numbers(body, [verified]) == ["0.68"]
    wrapped = body.replace("0.68", "⟦unverified: 0.68⟧")
    assert uncovered_numbers(wrapped, [verified]) == []


def test_drafted_body_drops_the_front_matter_the_appendices_and_every_renderer_block(
    store: ArtifactStore, tmp_path: Path
) -> None:
    report = render_report(inputs_for(store, tmp_path))
    prose = drafted_body(report)
    assert "schema_version" not in prose
    assert "Appendix" not in prose
    assert "quaestor:renderer:begin" not in prose
    assert "The AUC is 0.7412" in prose


# --- what the report says about itself (D-093, D-094, D-096, D-097) -----------------------------


@pytest.fixture
def inputs(store: ArtifactStore, tmp_path: Path) -> ReportInputs:
    """The renderer's inputs over the fixture store, ready to be varied one field at a time."""
    return inputs_for(store, tmp_path)


def test_the_front_matter_names_the_model_and_appendix_c_names_the_adapter(
    inputs: ReportInputs,
) -> None:
    """`claude-cli` is a subprocess; the front matter says which model wrote the report (D-093)."""
    inputs.model_id = "claude-opus-5[1m]"
    assert front_matter(inputs)["model"] == "claude-opus-5[1m]"
    assert "claude-opus-5[1m]" in scope_block(inputs)
    report = render_report(inputs)
    assert "| provider adapter | fake |" in report
    assert "| model | claude-opus-5[1m] |" in report


def test_with_no_model_id_the_front_matter_falls_back_and_appendix_c_says_so(
    inputs: ReportInputs,
) -> None:
    """`rules_only` answers with no model at all, which is not "the adapter was called fake"."""
    assert inputs.model_id == ""
    assert front_matter(inputs)["model"] == "fake"
    report = render_report(inputs)
    assert "| model | none: no model answered |" in report


@pytest.mark.parametrize(
    ("cell", "printed"),
    [
        ("0.6855555556", "0.6856"),
        ("3.098945254", "3.099"),
        ("900", "900"),
        (0.08332970973, "0.08333"),
        (-1.0, "-1"),
        ("2024-01", "2024-01"),
        ("", ""),
        (True, "True"),
        (None, "None"),
    ],
)
def test_a_table_cell_prints_a_measure_at_four_figures_and_a_count_as_a_count(
    cell: object, printed: str
) -> None:
    """D-094: one number, one spelling, and a period label is not a number."""
    from quaestor.report.renderer import _table_cell

    assert _table_cell(cell) == printed


def test_an_expanded_table_is_rendered_at_four_significant_figures(
    store: ArtifactStore,
) -> None:
    """The renderer block beside prose that wrote four figures now writes four as well."""
    store.put(
        "calibration.test",
        [{"bin": 1, "count": 900, "observed": 0.6855555556, "lift": 3.098945254}],
        ArtifactKind.table,
        "calibration by decile on test",
    )
    expanded = expand_tables("[[table:calibration.test]]", store)
    assert "| 1 | 900 | 0.6856 | 3.099 |" in expanded


def test_section_six_always_carries_open_items_even_with_nothing_under_it(
    inputs: ReportInputs,
) -> None:
    """D-096: the renderer supplies the heading the drafter omitted, as it does a finding's."""
    from quaestor.report.renderer import NO_OPEN_ITEMS

    inputs.sections = {**inputs.sections, ReportSection.findings: "Nothing was raised."}
    report = render_report(inputs)
    assert "### Open items" in report
    assert NO_OPEN_ITEMS in report
    assert check_report(report, inputs.configuration, inputs.claims.post_repair) == []


def test_what_the_drafter_wrote_under_open_items_is_kept_and_placed_last(
    inputs: ReportInputs,
) -> None:
    """The drafter is asked for the subsection; the renderer decides where it goes."""
    inputs.sections = {
        **inputs.sections,
        ReportSection.findings: (
            "Nothing was raised.\n\n### Open items\n\nThe sign on utilisation is unexplained; "
            "owner: model developer."
        ),
    }
    section = render_report(inputs).split("## 6. Findings")[1].split("## 7.")[0]
    assert "The sign on utilisation is unexplained" in section
    assert section.index("Candidates raised and not promoted") < section.index("### Open items")


def test_the_repair_sentence_counts_rewrites_and_removals_apart(
    tmp_path: Path, inputs: ReportInputs
) -> None:
    """D-097: a loop that removed three numbers and rewrote none did not do nothing."""
    trace = TraceWriter(tmp_path / "removed.jsonl", run_id="run-0001")
    trace.emit(
        "repair",
        section="data_integrity",
        round=1,
        flagged=["a", "b"],
        instructions=[],
        repaired=[],
        removed=[9.982, 6.0],
        still_failing=[],
    )
    trace.emit(
        "repair",
        section="outcomes",
        round=1,
        flagged=["c"],
        instructions=[],
        repaired=[],
        removed=[50.0],
        still_failing=[],
    )
    inputs.events = list(TraceReader(trace.path))
    report = render_report(inputs)
    assert "after 0 claim(s) rewritten and 3 number(s) removed from the prose" in report


# --- the follow-up subsection (DECISIONS D-101) -------------------------------------------------


def test_the_renderer_supplies_the_follow_up_heading_the_drafter_omitted(
    inputs: ReportInputs,
) -> None:
    """The same argument as `### Open items`: the shape is the pipeline's, not one model call's."""
    from quaestor.report.renderer import NO_FOLLOW_UP_PROSE

    inputs.follow_ups = {ReportSection.outcomes: [FollowUp(tool="compute_metrics")]}
    inputs.sections = {**inputs.sections, ReportSection.outcomes: "Discrimination is reported."}
    report = render_report(inputs)
    outcomes = report.split("## 4. Outcomes analysis", 1)[1].split("## 5.", 1)[0]
    assert FOLLOW_UPS_HEADING in outcomes
    assert NO_FOLLOW_UP_PROSE in outcomes
    assert check_report(report, inputs.configuration, inputs.claims.post_repair) == []


def test_what_the_drafter_wrote_under_the_follow_up_heading_is_left_alone(
    inputs: ReportInputs,
) -> None:
    inputs.follow_ups = {ReportSection.outcomes: [FollowUp(tool="compute_metrics")]}
    inputs.sections = {
        **inputs.sections,
        ReportSection.outcomes: (
            f"Discrimination is reported.\n\n{FOLLOW_UPS_HEADING}\n\nThe low-limit half was "
            "recomputed."
        ),
    }
    report = render_report(inputs)
    assert report.count(FOLLOW_UPS_HEADING) == 1
    assert "The low-limit half was recomputed." in report


def test_a_section_the_loop_did_not_touch_gets_no_follow_up_heading(inputs: ReportInputs) -> None:
    inputs.follow_ups = {ReportSection.outcomes: [FollowUp(tool="compute_metrics")]}
    report = render_report(inputs)
    sensitivity = report.split("## 5. Sensitivity and scenario analysis", 1)[1].split("## 6.", 1)[0]
    assert FOLLOW_UPS_HEADING not in sensitivity


def test_the_findings_section_is_never_asked_for_the_follow_up_heading(
    inputs: ReportInputs,
) -> None:
    """A material step reaches section 6 as an open item, which is a different sentence (D-102)."""
    inputs.follow_ups = {ReportSection.findings: [FollowUp(tool="compute_metrics", material=True)]}
    report = render_report(inputs)
    assert FOLLOW_UPS_HEADING not in report
