"""Wiring the three systems under test to Probatio's provider, and nothing else.

Quaestor's `LLM` protocol was written to be structurally identical to Probatio's `Provider`
(`complete(prompt, *, system=None, **params) -> Completion`), so the `provider` fixture is handed
straight to `Drafter`, to `extract()` and to `structured()`: **there is no adapter**, and DECISIONS
D-139 records the check that made that safe.

One wrapper is added, and it is not an adapter. `_LastAnswer` remembers the text of the last
completion a call produced, because a Probatio case asserts on **what the model returned** --
`schema_valid` on the JSON wrapper, `contains` on the values it listed -- and every one of the
three systems under test returns something parsed instead. Returning the parsed object would make
`schema_valid` a statement about pydantic rather than about the model, and would turn the answer
that `structured()` rejects into an exception where the suite needs a failing assertion.

So each system under test here returns the raw answer. An answer that `structured()` refused twice
is returned too, which is what lets `--probatio-provider fake` run every case to completion and
fail its content assertions rather than erroring: proving that the cases load, the systems under
test are wired and the relations expand costs nothing and calls nobody.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

from probatio.case import LLMCase

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBJECT = REPO_ROOT / "subjects" / "credit_default"

GUIDANCE_SEPARATOR = "\n\n---\n\n"
"""How `input.guidance` joins the retrieved spans' bodies; see `casebuilder.GUIDANCE_SEPARATOR`."""


class _LastAnswer:
    """A provider that passes every call through and remembers the last answer's text.

    Attributes:
        inner: The provider from the `provider` fixture, cassette-wrapped and observed.
        name: The inner provider's name, so a tape records the adapter and not this wrapper.
        answer: The text of the most recent completion; empty before the first call.
    """

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.name = getattr(inner, "name", "unknown")
        self.answer = ""

    @property
    def model(self) -> str | None:
        """The inner provider's model, forwarded so nothing downstream loses it."""
        model: str | None = getattr(self.inner, "model", None)
        return model

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Any:
        """Complete one prompt through the inner provider, keeping the answer's text."""
        completion = self.inner.complete(prompt, system=system, **params)
        self.answer = completion.text
        return completion


# -- rebuilding the drafter's inputs from a case -----------------------------------------------


def artifact_briefs(case: LLMCase) -> list[Any]:
    """Rebuild the artifacts the drafter is shown from `input.artifacts_json`.

    A list item is normally the mapping `ArtifactBrief.to_payload()` produced. It may also be a
    **JSON string**: `@distractor_robust` inserts strings only, so the irrelevant artifact it
    appends arrives as one, and parsing it here is the single tolerance this harness adds
    (DECISIONS D-141).
    """
    import json

    from quaestor.artifacts.store import ArtifactKind
    from quaestor.report.sections import ArtifactBrief

    briefs: list[Any] = []
    for item in case.input["artifacts_json"] if isinstance(case.input, dict) else []:
        payload = json.loads(item) if isinstance(item, str) else dict(item)
        kind = ArtifactKind(payload["kind"])
        value = payload.get("value")
        briefs.append(
            ArtifactBrief(
                name=str(payload["name"]),
                hash8=str(payload["hash8"]),
                kind=kind,
                value=None if value is None else float(value),
                values={
                    str(path): float(number)
                    for path, number in dict(payload.get("values", {})).items()
                },
                summary=str(payload.get("summary", "")),
                truncated=bool(payload.get("truncated", False)),
            )
        )
    return briefs


def guidance_spans(case: LLMCase) -> list[Any]:
    """Rebuild the retrieved spans: their identity from `metadata`, their bodies from `input`.

    The split is positional and forgiving on purpose. `@format_jitter` reformats the bodies -- it
    wraps them in a fence, doubles their spaces, upper-cases the first sentence -- and none of
    those transforms adds or removes a separator, so the count is stable; a variant that somehow
    changed it should still draft rather than raise, because a relation measures a verdict and an
    exception is not one.
    """
    from quaestor.report.drafter import GuidanceSpan

    if not isinstance(case.input, dict):  # pragma: no cover - every case's input is a mapping
        return []
    bodies = str(case.input.get("guidance", "")).split(GUIDANCE_SEPARATOR)
    spans: list[Any] = []
    for index, span in enumerate(case.metadata.get("spans", [])):
        spans.append(
            GuidanceSpan(
                doc=str(span["doc"]),
                section_id=str(span["section_id"]),
                heading=str(span["heading"]),
                text=bodies[index] if index < len(bodies) else "",
            )
        )
    return spans


def candidates(payloads: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Rebuild the candidate findings a section or the loop is shown."""
    from quaestor.findings import FindingCandidate

    return [FindingCandidate.model_validate(dict(payload)) for payload in payloads]


def findings(payloads: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Rebuild the promoted findings section 6 writes about.

    The evidence rule binds construction, and this is reading a written finding back rather than
    minting one, so the store context is passed as `None` -- deliberately and by name, which is
    the waiver D-061 defined for `eval/score.py`.
    """
    from quaestor.findings import STORE_CONTEXT_KEY, Finding

    return [
        Finding.model_validate(dict(payload), context={STORE_CONTEXT_KEY: None})
        for payload in payloads
    ]


def section_brief(case: LLMCase) -> Any:
    """Rebuild the brief the drafter is given, pinned in the case's metadata.

    The heading, the guidance query and the brief text are what `ordered_briefs` produced on the
    run the case was built from -- section 4's ordering and section 7's benchmarking sentence are
    both decided by that run's own artifacts -- so they are carried rather than recomputed, and
    `test_inputs_pinned.py` asserts they still match.
    """
    from quaestor.report.sections import SectionBrief
    from quaestor.vocab import ReportSection

    return SectionBrief(
        section=ReportSection(case.input["section"]),
        heading=str(case.metadata["heading"]),
        guidance_query=str(case.metadata["guidance_query"]),
        brief=str(case.metadata["brief"]),
    )


# -- the three systems under test ---------------------------------------------------------------


def draft_answer(case: LLMCase, provider: Any) -> str:
    """Draft one section through `Drafter.draft` and return the model's own answer."""
    from quaestor.errors import LLMOutputError
    from quaestor.report.drafter import Drafter

    recorder = _LastAnswer(provider)
    drafter = Drafter(
        recorder,
        package=str(case.metadata["package"]),
        version=str(case.metadata["version"]),
    )
    try:
        drafter.draft(
            section_brief(case),
            artifacts=artifact_briefs(case),
            spans=guidance_spans(case),
            candidates=candidates(case.input.get("candidates", [])),
            findings=findings(case.metadata.get("findings", [])),
        )
    except LLMOutputError:
        pass
    return recorder.answer


def extract_answer(case: LLMCase, provider: Any) -> str:
    """Extract one section's claims through `extract` and return the model's own answer."""
    from quaestor.errors import LLMOutputError
    from quaestor.verifier.extract import extract

    recorder = _LastAnswer(provider)
    try:
        extract(
            case.input["section"],
            str(case.input["prose"]),
            recorder,
            package_version=str(case.metadata["version"]),
        )
    except LLMOutputError:
        pass
    return recorder.answer


@lru_cache(maxsize=1)
def _package() -> Any:
    """Load the credit subject once per process; the loop prompt needs its spec, not its data."""
    from quaestor import load_package

    return load_package(SUBJECT)


def plan_steps(history: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Rebuild the loop's own `PlanStep` objects from the form a case carries them in."""
    from quaestor.agent.planner import FollowUpAction, PlannedCall, PlanStep

    steps: list[Any] = []
    for entry in history:
        action = FollowUpAction(
            tool=entry["tool"], args=dict(entry["args"]), why=str(entry["why"]), stop=False
        )
        call = (
            PlannedCall(str(entry["tool"]), dict(entry["args"]), str(entry["why"]), source="loop")
            if entry["accepted"]
            else None
        )
        steps.append(
            PlanStep(
                step=int(entry["step"]),
                action=action,
                accepted=bool(entry["accepted"]),
                reason=str(entry["reason"]),
                call=call,
                executed=bool(entry["executed"]),
                error=str(entry["error"]),
            )
        )
    return steps


def completed_calls(payloads: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Rebuild what the rule-based plan called, as the loop is shown it."""
    from quaestor.agent.planner import CompletedCall

    return [
        CompletedCall(
            tool=str(payload["tool"]),
            args=dict(payload["args"]),
            classes=list(payload["classes"]),
        )
        for payload in payloads
    ]


def loop_prompt_for(case: LLMCase) -> str:
    """Build the prompt one step of the bounded loop is sent, from the case's own inputs."""
    from quaestor.agent.planner import loop_prompt
    from quaestor.tools import default_registry

    return loop_prompt(
        default_registry(),
        _package(),
        remaining=int(case.input["remaining"]),
        candidates=candidates(case.input["candidates"]),
        completed=completed_calls(case.input["completed"]),
        artifact_names=list(case.input["artifact_names"]),
        data_columns=list(case.input["columns"]),
        history=plan_steps(case.input["history"]),
    )


def plan_answer(case: LLMCase, provider: Any) -> str:
    """Take one step of the bounded loop and return the model's own action, unparsed."""
    from quaestor.agent.planner import FollowUpAction
    from quaestor.errors import LLMOutputError
    from quaestor.llm.structured import structured

    recorder = _LastAnswer(provider)
    try:
        structured(recorder, loop_prompt_for(case), FollowUpAction)
    except LLMOutputError:
        pass
    return recorder.answer
