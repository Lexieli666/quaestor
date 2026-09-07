"""The tool contract of spec 3.7: the registry, the generated schemas, the context and the trace.

Nothing here runs a subject. What is being tested is the layer every tool is called through: that
arguments are validated against a closed model, that a schema is generated once and is the same
object three callers can read, that every call writes exactly one `tool_call` event with the
fields `eval/score.py` counts, and that the effective thresholds are readable only by the names
they are stored under.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor import ArtifactStore, TraceReader, TraceWriter, load_package
from quaestor.errors import ToolError
from quaestor.findings import DefectClass, FindingCandidate, Severity
from quaestor.tools import (
    DEFAULT_THRESHOLDS,
    Thresholds,
    Tool,
    ToolArgs,
    ToolContext,
    ToolRegistry,
    ToolResult,
    default_registry,
    package_threshold_names,
)
from quaestor.tools.metrics import Subpopulation, metric_artifact_name
from quaestor.tools.thresholds import THRESHOLD_SUMMARIES

HAZARD_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hazard_package"


class CountingTool(Tool["CountingTool.Args"]):
    """A tool that stores one artifact and, when asked, raises one candidate."""

    name = "counting"
    description = "Store one scalar and optionally raise one candidate."

    class Args(ToolArgs):
        """Arguments of the counting tool."""

        value: float = 1.0
        raise_candidate: bool = False

    def run(self, args: CountingTool.Args, ctx: ToolContext) -> ToolResult:
        """Store the value under `counting.value` and return it."""
        # Named for the value, because the store refuses to re-point a name at a new payload.
        segment = f"v{args.value:g}".replace(".", "_")
        artifact = ctx.store.put(f"counting.{segment}", args.value, "scalar", "a test artifact")
        candidates = (
            [
                FindingCandidate(
                    defect_class=DefectClass.M1,
                    evidence=[artifact.hash],
                    detail="a test candidate",
                    suggested_severity=Severity.low,
                    tool=self.name,
                )
            ]
            if args.raise_candidate
            else []
        )
        return ToolResult(
            tool=self.name, artifacts=[artifact], candidates=candidates, summary="counted"
        )


class FailingTool(Tool["FailingTool.Args"]):
    """A tool that always raises, so the trace of a failed call can be asserted on."""

    name = "failing"
    description = "Always raise a ToolError."

    class Args(ToolArgs):
        """Arguments of the failing tool."""

    def run(self, args: FailingTool.Args, ctx: ToolContext) -> ToolResult:
        """Raise."""
        raise ToolError("this tool always fails")


@pytest.fixture
def context(tmp_path: Path) -> ToolContext:
    """A context over the hazard fixture package, with a store and a trace of its own."""
    return ToolContext(
        package=load_package(HAZARD_FIXTURE),
        store=ArtifactStore(tmp_path / "artifacts"),
        out_dir=tmp_path / "run",
        trace=TraceWriter(tmp_path / "trace.jsonl", run_id="registry-test"),
    )


# --- the registry --------------------------------------------------------------------------------


def test_the_default_registry_holds_the_nine_tools_of_spec_3_7() -> None:
    registry = default_registry()
    assert registry.names() == [
        "run_model",
        "profile_data",
        "compute_metrics",
        "check_leakage",
        "check_stability",
        "check_collinearity",
        "challenger_compare",
        "run_scenarios",
        "retrieve_guidance",
    ]
    assert len(registry) == 9
    assert "run_model" in registry
    # retrieve_guidance was withheld through Phase 5 rather than stubbed; Phase 6 registers it.
    assert "retrieve_guidance" in registry


def test_every_registered_tool_declares_a_name_a_description_and_closed_args() -> None:
    for tool in default_registry():
        assert tool.name and tool.description
        assert tool.Args.model_config["extra"] == "forbid"
        assert tool.__doc__ and tool.run.__doc__


def test_schemas_are_generated_once_and_handed_to_every_caller() -> None:
    registry = default_registry()
    first = registry.schema("profile_data")
    assert registry.schema("profile_data") is first
    assert registry.schemas()["profile_data"] is first
    assert first["additionalProperties"] is False
    assert set(first["properties"]) == {"splits", "features"}


def test_the_catalogue_carries_the_name_description_and_schema_of_each_tool() -> None:
    catalogue = default_registry().catalogue()
    assert [entry["tool"] for entry in catalogue] == default_registry().names()
    entry = next(item for item in catalogue if item["tool"] == "compute_metrics")
    assert "threshold" in entry["description"]
    assert set(entry["schema"]["properties"]) == {"splits", "subpopulation"}


def test_an_unknown_tool_is_refused_by_name_and_lists_the_known_ones() -> None:
    with pytest.raises(ToolError, match="no tool named 'check_everything'"):
        default_registry().get("check_everything")
    with pytest.raises(ToolError, match="run_model"):
        default_registry().schema("nope")


def test_a_tool_cannot_be_registered_twice() -> None:
    registry = ToolRegistry([CountingTool()])
    with pytest.raises(ToolError, match="already registered"):
        registry.register(CountingTool())


def test_a_tool_without_a_name_or_description_is_refused() -> None:
    class Nameless(CountingTool):
        name = ""

    with pytest.raises(ToolError, match="name and a description"):
        ToolRegistry([Nameless()])


# --- argument validation --------------------------------------------------------------------------


def test_an_undeclared_argument_is_rejected_and_names_the_field() -> None:
    tool = CountingTool()
    with pytest.raises(ToolError, match="value_typo"):
        tool.parse({"value_typo": 2.0})


def test_arguments_may_be_passed_already_built_or_as_a_mapping_or_omitted() -> None:
    tool = CountingTool()
    assert tool.parse(None).value == 1.0
    assert tool.parse({"value": 3.0}).value == 3.0
    built = CountingTool.Args(value=4.0)
    assert tool.parse(built) is built


def test_an_args_model_of_the_wrong_tool_is_refused() -> None:
    with pytest.raises(ToolError, match="takes CountingTool.Args"):
        CountingTool().parse(FailingTool.Args())


def test_a_wrongly_typed_argument_is_rejected() -> None:
    with pytest.raises(ToolError, match="cannot take these arguments"):
        CountingTool().parse({"value": "not a number"})


# --- the trace ------------------------------------------------------------------------------------


def test_one_call_writes_exactly_one_tool_call_event_with_the_spec_31_fields(
    context: ToolContext, tmp_path: Path
) -> None:
    registry = ToolRegistry([CountingTool()])
    result = registry.call("counting", {"value": 2.0, "raise_candidate": True}, context)
    events = TraceReader(tmp_path / "trace.jsonl").events("tool_call")
    assert len(events) == 1
    payload = events[0].payload
    assert payload["tool"] == "counting"
    assert payload["artifacts"] == [result.artifacts[0].hash]
    assert payload["candidates"] == ["M1"]
    assert payload["ok"] is True
    assert isinstance(payload["duration_s"], float)
    assert len(payload["args_hash"]) == 16


def test_the_args_hash_distinguishes_two_calls_of_one_tool(
    context: ToolContext, tmp_path: Path
) -> None:
    registry = ToolRegistry([CountingTool()])
    registry.call("counting", {"value": 2.0}, context)
    registry.call("counting", {"value": 2.0}, context)
    registry.call("counting", {"value": 3.0}, context)
    hashes = [event.payload["args_hash"] for event in TraceReader(tmp_path / "trace.jsonl")]
    assert hashes[0] == hashes[1] != hashes[2]


def test_a_failed_call_is_traced_before_the_error_is_re_raised(
    context: ToolContext, tmp_path: Path
) -> None:
    registry = ToolRegistry([FailingTool()])
    with pytest.raises(ToolError, match="always fails"):
        registry.call("failing", {}, context)
    events = TraceReader(tmp_path / "trace.jsonl").events("tool_call")
    assert len(events) == 1
    assert events[0].payload["ok"] is False
    assert events[0].payload["artifacts"] == []


def test_a_context_without_a_trace_still_runs(tmp_path: Path) -> None:
    ctx = ToolContext(
        package=load_package(HAZARD_FIXTURE),
        store=ArtifactStore(tmp_path / "artifacts"),
        out_dir=tmp_path / "run",
    )
    assert ctx.trace is None
    assert ToolRegistry([CountingTool()]).call("counting", None, ctx).summary == "counted"
    assert not (tmp_path / "trace.jsonl").exists()


def test_the_context_reports_the_packages_declared_splits(context: ToolContext) -> None:
    assert context.splits == ["train", "test", "out_of_time", "vintage_holdout"]


def test_a_result_reports_its_artifact_names_and_its_classes(context: ToolContext) -> None:
    result = ToolRegistry([CountingTool()]).call("counting", {"raise_candidate": True}, context)
    assert result.artifact_names == ["counting.v1"]  # value 1.0 renders as v1
    assert result.classes == ["M1"]
    assert ToolResult(tool="empty").classes == []


# --- thresholds ----------------------------------------------------------------------------------


def test_every_threshold_of_spec_37_has_a_default_and_a_caption() -> None:
    assert set(DEFAULT_THRESHOLDS) == set(THRESHOLD_SUMMARIES)
    thresholds = Thresholds()
    assert len(thresholds) == len(DEFAULT_THRESHOLDS)
    assert list(thresholds) == sorted(DEFAULT_THRESHOLDS)
    assert thresholds["threshold.M1.vif"] == 10.0
    assert thresholds["threshold.E1.delta_auc"] == 0.03
    assert thresholds["rule.calibration_first_event_rate"] == 0.05


def test_a_threshold_may_be_overridden_but_not_invented() -> None:
    assert Thresholds({"threshold.M1.vif": 5.0})["threshold.M1.vif"] == 5.0
    with pytest.raises(ToolError, match="not a threshold"):
        Thresholds({"threshold.M1.vifs": 5.0})
    with pytest.raises(ToolError, match="not a threshold"):
        Thresholds()["threshold.nope"]


def test_reading_a_threshold_through_artifact_puts_it_in_the_store(context: ToolContext) -> None:
    artifact = context.thresholds.artifact(context.store, "threshold.M1.vif")
    assert artifact.name == "threshold.M1.vif"
    assert context.store.value("threshold.M1.vif") == 10.0
    assert artifact.summary == THRESHOLD_SUMMARIES["threshold.M1.vif"]
    # Storing it twice is the same artifact, so two tools may both cite the rule they applied.
    assert context.thresholds.artifact(context.store, "threshold.M1.vif").hash == artifact.hash


def test_a_package_threshold_is_named_for_its_metric_split_and_bound() -> None:
    spec = load_package(HAZARD_FIXTURE).spec
    named = [package_threshold_names(rule) for rule in spec.thresholds]
    assert named[0] == {"threshold.package.auc.out_of_time.min": 0.65}
    assert named[1] == {"threshold.package.psi.max": 0.25}


def test_a_declared_metric_maps_to_the_artifact_that_answers_it() -> None:
    assert metric_artifact_name("auc", "test") == "metrics.test.auc"
    assert metric_artifact_name("calibration_slope", "test") == "calibration_slope.test"
    assert metric_artifact_name("cpr_mae", "train") == "cpr.train.mae"
    assert metric_artifact_name("psi", None) == "psi.max"
    assert metric_artifact_name("condition_number", None) == "condition_number"
    # A metric no artifact answers, and a split-scoped metric with no split, are both unresolvable.
    assert metric_artifact_name("sharpe_ratio", "test") is None
    assert metric_artifact_name("auc", None) is None


# --- the sub-population argument -----------------------------------------------------------------


def test_a_subpopulation_slug_matches_the_names_the_golden_report_cites() -> None:
    assert Subpopulation(column="limit_bal", rule="below_median").slug == "limit_bal_low"
    assert Subpopulation(column="limit_bal", rule="above_median").slug == "limit_bal_high"
    assert (
        Subpopulation(column="rate_regime", rule="equals:falling").slug == "rate_regime_eq_falling"
    )
    assert Subpopulation(column="vintage", rule="equals:2014 Q1").slug == "vintage_eq_2014_Q1"


def test_an_unknown_subpopulation_rule_is_refused() -> None:
    with pytest.raises(ToolError, match="not a sub-population rule"):
        ToolRegistry(default_registry()).get("compute_metrics").parse(
            {"subpopulation": {"column": "limit_bal", "rule": "median"}}
        )
