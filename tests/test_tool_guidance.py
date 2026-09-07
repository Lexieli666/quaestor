"""`retrieve_guidance`: the ninth tool, the one that computes nothing about the model.

The acceptance criterion of spec 3.7, as D-054 corrects it, is the first test here:
`retrieve_guidance("outcomes analysis")` must return, among its top three, SR 11-7 V.1.c and
SR 26-2 V.1.b. Everything else checks the shape of the artifact it stores, since that artifact is
what the drafter is shown and what the trace records it was shown.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quaestor import ArtifactStore, TraceReader, TraceWriter, load_package
from quaestor.artifacts import ArtifactKind
from quaestor.errors import ToolError
from quaestor.tools import RetrieveGuidanceTool, ToolContext, default_registry, guidance_name

HAZARD_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hazard_package"


@pytest.fixture
def context(tmp_path: Path) -> ToolContext:
    """A context with a store and a trace of its own; the tool reads no run directory."""
    return ToolContext(
        package=load_package(HAZARD_FIXTURE),
        store=ArtifactStore(tmp_path / "artifacts"),
        out_dir=tmp_path / "run",
        trace=TraceWriter(tmp_path / "trace.jsonl", run_id="guidance-test"),
    )


def payload(context: ToolContext, name: str) -> dict[str, object]:
    """Read back a stored guidance artifact."""
    loaded = context.store.load(name)
    assert isinstance(loaded, dict)
    return loaded


# --- the acceptance criterion ---------------------------------------------------------------------


def test_outcomes_analysis_retrieves_both_guidance_sections(context: ToolContext) -> None:
    result = default_registry().call("retrieve_guidance", {"query": "outcomes analysis"}, context)
    spans = payload(context, result.artifact_names[0])["spans"]
    assert isinstance(spans, list)
    found = {(span["doc"], span["section_id"]) for span in spans}
    assert len(spans) == 3
    assert ("SR11-7", "V.1.c") in found
    assert ("SR26-2", "V.1.b") in found
    assert result.candidates == []


# --- the artifact ---------------------------------------------------------------------------------


def test_the_artifact_is_named_for_a_hash_of_the_whole_request(context: ToolContext) -> None:
    result = RetrieveGuidanceTool().run(
        RetrieveGuidanceTool.Args(query="model documentation", k=2), context
    )
    name = guidance_name("model documentation", 2, None)
    assert result.artifact_names == [name]
    assert name.startswith("guidance.")
    assert result.artifacts[0].kind is ArtifactKind.json


def test_two_different_requests_do_not_collide(context: ToolContext) -> None:
    tool = RetrieveGuidanceTool()
    first = tool.run(RetrieveGuidanceTool.Args(query="outcomes analysis", k=2), context)
    second = tool.run(RetrieveGuidanceTool.Args(query="outcomes analysis", k=3), context)
    third = tool.run(
        RetrieveGuidanceTool.Args(query="outcomes analysis", k=2, docs=["SR26-2"]), context
    )
    names = {first.artifact_names[0], second.artifact_names[0], third.artifact_names[0]}
    assert len(names) == 3


def test_the_same_request_twice_is_the_same_artifact(context: ToolContext) -> None:
    tool = RetrieveGuidanceTool()
    args = RetrieveGuidanceTool.Args(query="ongoing monitoring")
    first = tool.run(args, context)
    second = tool.run(args, context)
    assert first.artifacts[0].hash == second.artifacts[0].hash


def test_the_artifact_records_the_request_beside_the_spans(context: ToolContext) -> None:
    result = RetrieveGuidanceTool().run(
        RetrieveGuidanceTool.Args(query="effective challenge", k=2), context
    )
    stored = payload(context, result.artifact_names[0])
    assert stored["query"] == "effective challenge"
    assert stored["k"] == 2
    assert stored["docs"] == ["SR11-7", "SR26-2"]
    spans = stored["spans"]
    assert isinstance(spans, list) and len(spans) == 2
    assert set(spans[0]) == {"doc", "section_id", "heading", "text", "score"}


def test_the_summary_names_the_citations_a_drafter_may_write(context: ToolContext) -> None:
    result = RetrieveGuidanceTool().run(
        RetrieveGuidanceTool.Args(query="outcomes analysis", k=1), context
    )
    assert "[[reg:SR26-2:V.1.b]]" in result.summary
    assert "[[reg:SR26-2:V.1.b]]" in result.artifacts[0].summary


def test_the_search_can_be_restricted_to_the_current_guidance(context: ToolContext) -> None:
    result = RetrieveGuidanceTool().run(
        RetrieveGuidanceTool.Args(query="model validation", k=3, docs=["SR26-2"]), context
    )
    stored = payload(context, result.artifact_names[0])
    spans = stored["spans"]
    assert isinstance(spans, list)
    assert {span["doc"] for span in spans} == {"SR26-2"}
    assert stored["docs"] == ["SR26-2"]


def test_a_query_the_guidance_never_discusses_stores_no_spans(context: ToolContext) -> None:
    result = RetrieveGuidanceTool().run(
        RetrieveGuidanceTool.Args(query="prepayment burnout convexity"), context
    )
    assert payload(context, result.artifact_names[0])["spans"] == []
    assert "shares a term" in result.summary
    assert result.candidates == []


# --- what it refuses ------------------------------------------------------------------------------


def test_an_empty_query_is_refused(context: ToolContext) -> None:
    with pytest.raises(ToolError, match="needs a query"):
        RetrieveGuidanceTool().run(RetrieveGuidanceTool.Args(query="   "), context)


def test_a_non_positive_k_is_refused(context: ToolContext) -> None:
    with pytest.raises(ToolError, match="k must be at least 1"):
        RetrieveGuidanceTool().run(RetrieveGuidanceTool.Args(query="anything", k=0), context)


def test_a_document_that_was_never_ingested_is_refused(context: ToolContext) -> None:
    with pytest.raises(ToolError, match="OCC2011-12"):
        RetrieveGuidanceTool().run(
            RetrieveGuidanceTool.Args(query="anything", docs=["OCC2011-12"]), context
        )


# --- the registry ---------------------------------------------------------------------------------


def test_the_registry_now_holds_nine_tools_and_traces_this_one(
    context: ToolContext, tmp_path: Path
) -> None:
    trace_path = tmp_path / "trace.jsonl"
    registry = default_registry()
    assert len(registry) == 9
    assert registry.names()[-1] == "retrieve_guidance"
    assert set(registry.schema("retrieve_guidance")["properties"]) == {"query", "k", "docs"}

    registry.call("retrieve_guidance", {"query": "documentation", "k": 1}, context)
    events = TraceReader(trace_path).events("tool_call")
    assert [event.payload["tool"] for event in events] == ["retrieve_guidance"]
    assert events[0].payload["ok"] is True
    assert len(events[0].payload["artifacts"]) == 1


def test_the_stored_payload_is_canonical_json(context: ToolContext) -> None:
    result = RetrieveGuidanceTool().run(
        RetrieveGuidanceTool.Args(query="internal audit", k=1), context
    )
    written = json.loads(result.artifacts[0].path.read_text(encoding="utf-8"))
    assert list(written) == sorted(written)
