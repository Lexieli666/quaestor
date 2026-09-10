"""Build the committed Probatio cases, schemas and rubric inputs from a run, not by hand.

Spec section 6 fixes three case families and what each asserts. What it does not fix is where the
inputs come from, and that is the whole of this module's job: **every input a case carries is
produced by running the real pipeline once, offline, on the synthetic `credit_default` subject**
(seed 20260901, the seed `package.yaml` declares), or read out of the committed live run at
`eval/results/first-live/credit/`. Nothing is typed in.

That matters because a case file is the thing a reviewer diffs, and a hand-written one drifts away
from the pipeline the moment a selector, a brief or an artifact name changes -- silently, because a
drafting case whose artifacts no longer match the store still drafts something. So this module is
the single writer of `cases/*.yaml` and `schemas/*.json`, and `test_inputs_pinned.py` asserts that
what is committed is byte-identical to what this module produces *now*. A change to a section
brief, to a selector, to `DRAFT_INSTRUCTION` or to a tool's arguments therefore fails the offline
suite with a diff, and re-running `python tests/probatio/casebuilder.py` is the fix.

Run it as a script to rewrite the committed files:

    python tests/probatio/casebuilder.py

Nothing here calls a live model: the pipeline is driven by `OfflineLLM`, which is what
`quaestor validate --llm fake` uses.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Final

import yaml

REPO_ROOT: Final = Path(__file__).resolve().parents[2]
"""The repository root; every path this module writes is relative to it."""

HERE: Final = Path(__file__).resolve().parent
"""`tests/probatio/`, which holds the cases, the schemas and the rubric."""

CASES_DIR: Final = HERE / "cases"
SCHEMAS_DIR: Final = HERE / "schemas"

SUBJECT: Final = REPO_ROOT / "subjects" / "credit_default"
"""The synthetic subject every case is built from (spec section 6)."""

SYNTHETIC_N: Final = 5000
"""The row count `quaestor validate --synthetic` resolves to for this subject."""

SUBJECT_SEED: Final = 20260901
"""The seed `subjects/credit_default/package.yaml` declares for its split."""

LIVE_RUN: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit"
"""The committed live run the `extract_claims` case takes its section text from."""

GUIDANCE_SEPARATOR: Final = "\n\n---\n\n"
"""How the retrieved spans' bodies are joined into one `input.guidance` string.

`@format_jitter` needs a **string** field, and the drafter needs six typed spans. Joining the
bodies with a separator and carrying each span's `doc`, `section_id` and `heading` in the case's
`metadata` gives both: the relation reformats exactly the prose the retriever returned, and the
citation the drafter is asked to copy is never mangled by an upper-casing transform.
"""

DISTRACTOR: Final = json.dumps(
    {
        "name": "projection.convexity",
        "hash8": "0d15720c",
        "kind": "scalar",
        "summary": "change in servicing value under a +/-300 bp parallel shock, in dollars",
        "value": -168055.0,
        "citation": "[[art:0d15720c:projection.convexity]]",
    },
    sort_keys=True,
)
"""The one irrelevant artifact `@distractor_robust` appends to a drafting case.

It is an artifact of the *other* subject -- a mortgage-servicing projection has no place in a
credit report -- carried as a JSON string because `DistractorRobust` inserts strings only. The
system under test parses a string item back into an artifact, which is the one tolerance the
harness adds and is recorded in DECISIONS D-141.
"""

MAX_LATENCY_CEILING_MS: Final = 480_000.0
"""Every case's latency ceiling, per run: eight minutes, uniform and not estimated (D-150).

The cost regression below transfers between runs -- it predicted the second record run's spend to
within 6% -- and the latency one does not. `findings` was predicted at 15.1 s from the Phase 9
trace and one of its variants took 100.2 s in the record run, 6.6 times the estimate, because
wall clock on this provider is dominated by service variance rather than by how much the model
writes. So latency gets one generous number chosen from the observed tail instead of a per-section
one derived from a model that does not hold, and the tight, meaningful ceiling is the cost one.

Eight minutes covers a run of two calls -- `structured()` asks once and may re-ask -- at twice the
longest single call any tape holds (106.5 s, itself censored: the three calls that overran the
provider's 120 s default recorded nothing). `--probatio-timeout` sits above it at 600 s, so a hung
subprocess is killed by the provider and a merely slow case fails its budget, which is a verdict
rather than an error.
"""

PROVIDER_TIMEOUT_S: Final = 600.0
"""What `--probatio-timeout` is set to in `pyproject.toml`; see `MAX_LATENCY_CEILING_MS`."""

BUDGET_HEADROOM: Final = 2.5
"""What the estimate is multiplied by to get a ceiling.

Two, because `structured()` may re-ask once and a re-ask is the same call again, and a half more
because the estimate is a regression over eighteen calls of one run and not a guarantee.
"""

USD_PER_INPUT_TOKEN: Final = 10.42776919e-6
USD_PER_OUTPUT_TOKEN: Final = 24.6540282e-6
"""Least squares over the eighteen calls of `eval/results/first-live/credit/`.

Blended rates, not list prices: the run was made through the Claude Code CLI on a subscription
login and its `total_cost_usd` is the notional API price of a turn whose input was partly served
from cache. The fit reproduces all eighteen recorded costs to within 6.6%, which is what a budget
ceiling needs; nothing else in the project reads these numbers.
"""

BYTES_PER_INPUT_TOKEN: Final = 2.04
"""Prompt bytes per input token, over the seven drafting calls of the same run."""

LATENCY_MS_PER_OUTPUT_TOKEN: Final = 9.96
LATENCY_MS_FIXED: Final = 7_020.0
"""Wall clock against output tokens, over the same eighteen calls."""


# -- the offline run every input comes from ---------------------------------------------------


@dataclass(frozen=True)
class Capture:
    """One offline run of the synthetic credit subject, and what the pipeline built from it.

    Attributes:
        out_dir: The run directory.
        briefs: The seven section briefs, in report order, as `ordered_briefs` produced them.
        inputs: What each section's drafter was given, as `_draft_inputs` produced it.
        loop: The keyword arguments the bounded follow-up loop was called with.
        registry: The tool registry the loop was shown.
        package: The loaded package.
    """

    out_dir: Path
    briefs: Any
    inputs: Any
    loop: Any
    registry: Any
    package: Any


def capture(out_dir: Path) -> Capture:
    """Run the pipeline once, offline, and return what it handed the drafter and the loop.

    The two collaborators are spied on rather than re-implemented: a second expression of "which
    artifacts does section 4 get" is a second chance to disagree with the first, which is the
    defect D-084 named. What this returns is the object the drafter was actually passed.

    Args:
        out_dir: Where the run writes; a temporary directory in the suite, a scratch one here.

    Returns:
        The capture.
    """
    import quaestor.pipeline as pipeline
    from quaestor import load_package
    from quaestor.artifacts.store import ArtifactStore
    from quaestor.llm.offline import OfflineLLM
    from quaestor.report.sections import ordered_briefs
    from quaestor.tools import default_registry

    captured_inputs: dict[Any, Any] = {}
    captured_loop: dict[str, Any] = {}
    original_inputs = pipeline._draft_inputs
    original_loop = pipeline.follow_up_plan

    def spy_inputs(*args: Any, **kwargs: Any) -> Any:
        result = original_inputs(*args, **kwargs)
        captured_inputs.update(result)
        return result

    def spy_loop(llm: Any, registry: Any, package: Any, **kwargs: Any) -> Any:
        captured_loop.update(kwargs)
        return original_loop(llm, registry, package, **kwargs)

    pipeline._draft_inputs = spy_inputs
    pipeline.follow_up_plan = spy_loop
    try:
        package = load_package(SUBJECT)
        pipeline.validate(
            package, llm=OfflineLLM(), config="full_agent", out=out_dir, synthetic=SYNTHETIC_N
        )
    finally:
        pipeline._draft_inputs = original_inputs
        pipeline.follow_up_plan = original_loop

    store = ArtifactStore(out_dir / "artifacts")
    briefs = {brief.section: brief for brief in ordered_briefs(store, package.spec)}
    return Capture(
        out_dir=out_dir,
        briefs=briefs,
        inputs=captured_inputs,
        loop=captured_loop,
        registry=default_registry(),
        package=package,
    )


# -- estimates, which become the budgets ------------------------------------------------------


def estimate_cost_usd(prompt_bytes: int, output_tokens: int) -> float:
    """Estimate one call's cost from its prompt size and how much it is expected to write."""
    tokens_in = prompt_bytes / BYTES_PER_INPUT_TOKEN
    return tokens_in * USD_PER_INPUT_TOKEN + output_tokens * USD_PER_OUTPUT_TOKEN


def estimate_latency_ms(output_tokens: int) -> float:
    """Estimate one call's wall clock from how much it is expected to write.

    Kept for the wall-clock figure the Phase 11 report quotes, and deliberately **not** used to
    size a budget any more: measured against the second record run it was out by a factor of 6.6
    on one section, which is D-150's whole subject.
    """
    return LATENCY_MS_FIXED + output_tokens * LATENCY_MS_PER_OUTPUT_TOKEN


def budget_for(prompt_bytes: int, output_tokens: int) -> dict[str, float]:
    """Return the `budget` block one case declares: cost from its estimate, latency uniform.

    The two ceilings are set differently on purpose, and D-150 records why: the cost model held to
    6% against a whole record run and the latency model was out by a factor of 6.6 on one section,
    so only one of them has earned the right to size a per-case number.
    """
    cost = estimate_cost_usd(prompt_bytes, output_tokens) * BUDGET_HEADROOM
    return {
        "max_cost_usd": round(cost + 0.005, 2),
        "max_latency_ms": MAX_LATENCY_CEILING_MS,
    }


LIVE_DRAFT_OUTPUT_TOKENS: Final[Mapping[str, int]] = {
    "summary": 3431,
    "conceptual_soundness": 6968,
    "data_integrity": 6064,
    "outcomes": 7429,
    "sensitivity": 2175,
    "findings": 815,
    "monitoring": 3667,
}
"""What each section's drafting call wrote on the committed live run, per its trace.

Used only to size a budget. The synthetic sections are smaller than the live ones, so a ceiling
built from these is a ceiling with room in it rather than one tuned to the answer.
"""

LIVE_EXTRACT_OUTPUT_TOKENS: Final = 8247
"""What the live run's section 2 extraction wrote; the `extract_claims` case replays that prose."""

LIVE_PLAN_OUTPUT_TOKENS: Final = 564
"""The largest of the live run's four planning answers."""


# -- draft_section ------------------------------------------------------------------------------


def _span_payloads(spans: Sequence[Any]) -> list[dict[str, str]]:
    """Return each span's identity, which `input.guidance` deliberately does not carry."""
    return [
        {"doc": span.doc, "section_id": span.section_id, "heading": span.heading} for span in spans
    ]


def _guidance_text(spans: Sequence[Any]) -> str:
    """Join the spans' bodies into the one string `@format_jitter` reformats."""
    for span in spans:
        if GUIDANCE_SEPARATOR in span.text:
            raise ValueError(
                f"the {span.doc} {span.section_id} span carries the separator "
                f"{GUIDANCE_SEPARATOR!r}, so the bodies cannot be joined with it"
            )
    return GUIDANCE_SEPARATOR.join(span.text for span in spans)


def _candidate_payloads(candidates: Sequence[Any]) -> list[dict[str, Any]]:
    """Return the candidates as the case carries them, exactly as the pipeline raised them."""
    return [candidate.model_dump(mode="json") for candidate in candidates]


def _finding_payloads(findings: Sequence[Any]) -> list[dict[str, Any]]:
    """Return the promoted findings section 6 is asked to write about."""
    return [finding.model_dump(mode="json") for finding in findings]


DRAFT_ASSERTION_NOT_CONTAINS: Final = [
    "⟦unverified",
    "compliant",
    "certified",
]
"""What a drafted section may never carry.

Spec section 6 names the unverified wrapper; the other two are `DRAFT_INSTRUCTION`'s own
prohibition and `CLAUDE.md`'s, and a draft that broke either would reach the renderer.
"""


def draft_cases(cap: Capture) -> list[dict[str, Any]]:
    """Build one drafting case per section that drafts: seven, one per brief."""
    from quaestor.llm.offline import OfflineLLM
    from quaestor.report.drafter import Drafter

    drafter = Drafter(OfflineLLM(), package=cap.package.spec.name, version=cap.package.spec.version)
    cases: list[dict[str, Any]] = []
    for section, brief in cap.briefs.items():
        given = cap.inputs[section]
        prompt = drafter.prompt(
            brief,
            artifacts=given.artifacts,
            spans=given.spans,
            candidates=given.candidates,
            findings=given.findings,
            follow_ups=given.follow_ups,
        )
        expected_out = LIVE_DRAFT_OUTPUT_TOKENS[section.value]
        cases.append(
            {
                "id": f"draft_section.{section.value}",
                "input": {
                    "section": section.value,
                    "artifacts_json": [item.to_payload() for item in given.artifacts],
                    "candidates": _candidate_payloads(given.candidates),
                    "guidance": _guidance_text(given.spans),
                },
                "metadata": {
                    "package": cap.package.spec.name,
                    "version": cap.package.spec.version,
                    "synthetic_n": SYNTHETIC_N,
                    "seed": SUBJECT_SEED,
                    "heading": brief.heading,
                    "guidance_query": brief.guidance_query,
                    "brief": brief.brief,
                    "spans": _span_payloads(given.spans),
                    "findings": _finding_payloads(given.findings),
                    "prompt_bytes": len(prompt.encode("utf-8")),
                    "rubric_sha256": rubric_digest("grounding"),
                },
                "assertions": [
                    {
                        "type": "schema_valid",
                        "schema_file": "tests/probatio/schemas/drafted_section.json",
                    },
                    {"type": "contains", "all": ["[[art:"], "case_sensitive": True},
                    {
                        "type": "not_contains",
                        "all": list(DRAFT_ASSERTION_NOT_CONTAINS),
                        "case_sensitive": False,
                    },
                    {"type": "judge", "rubric": "grounding", "threshold": 1.0},
                ],
                "budget": budget_for(len(prompt.encode("utf-8")), expected_out),
                "snapshot": "scores",
                "tags": ["drafter", "credit_default", "synthetic"],
            }
        )
    return cases


# -- extract_claims -----------------------------------------------------------------------------


def live_section_two() -> str:
    """Return section 2 of the committed live report, as the extractor would be handed it.

    The level-2 heading is the renderer's, not the drafter's, so it is dropped; renderer blocks
    are removed with the pipeline's own `drafted_prose`, so the case cannot disagree with what
    `extract()` will do to the same text.
    """
    from quaestor.verifier.tokens import drafted_prose

    text = (LIVE_RUN / "report.md").read_text(encoding="utf-8")
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("## 2. "))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    body = "\n".join(lines[start + 1 : end]).strip("\n")
    return drafted_prose(body).strip("\n")


def _expected_values(prose: str) -> list[str]:
    """Pick the values the extractor must return, from the live run's own `claims.json`.

    A needle is taken only when it is a value of a section 2 claim of that run, is written in the
    prose exactly as `json.dumps` would write it, and appears there exactly once. Six are kept,
    spread evenly through the section, so a needle is evidence that the extractor read that part
    of the prose rather than the first paragraph six times.
    """
    payload = json.loads((LIVE_RUN / "claims.json").read_text(encoding="utf-8"))
    claims = [
        claim
        for claim in payload["post_repair"]
        if claim["section"] == "conceptual_soundness" and claim.get("value") is not None
    ]
    seen: list[str] = []
    for claim in claims:
        needle = json.dumps(claim["value"])
        if "e" in needle or "E" in needle:
            continue
        if len(needle.lstrip("-0.")) < 4:
            continue
        if prose.count(needle) != 1 or needle in seen:
            continue
        seen.append(needle)
    if len(seen) < 6:  # pragma: no cover - the committed run has far more than six
        raise ValueError(f"only {len(seen)} usable needles in the live section 2")
    step = len(seen) // 6
    return [seen[index * step] for index in range(6)]


def extract_cases() -> list[dict[str, Any]]:
    """Build the one extraction case: the live report's section 2, verbatim."""
    prose = live_section_two()
    needles = _expected_values(prose)
    prompt_bytes = len(prose.encode("utf-8")) + 2_000
    return [
        {
            "id": "extract_claims.conceptual_soundness",
            "input": {"section": "conceptual_soundness", "prose": prose},
            "metadata": {
                "package": "credit_default",
                "version": "1.0",
                "source": "eval/results/first-live/credit/report.md",
                "source_section": "2. Conceptual soundness",
                "runs": 5,
                "floor": 0.8,
            },
            "assertions": [
                {
                    "type": "schema_valid",
                    "schema_file": "tests/probatio/schemas/extracted_claims.json",
                },
                {"type": "contains", "all": needles, "case_sensitive": True},
            ],
            "budget": budget_for(prompt_bytes, LIVE_EXTRACT_OUTPUT_TOKENS),
            "snapshot": "scores",
            "tags": ["verifier", "credit_default", "live-prose"],
        }
    ]


# -- plan_followup ------------------------------------------------------------------------------


UNOFFERED_TOOLS: Final = ["check_stability", "run_scenarios"]
"""Registry tools this package does not support, so the catalogue does not list them (D-089)."""

INVENTED_TOOLS: Final = [
    "check_drift",
    "compute_psi",
    "run_backtest",
    "profile_features",
    "check_overfitting",
]
"""Names no registry has ever had. A loop that answers with one of them has invented a tool."""


def _completed_payloads(completed: Sequence[Any]) -> list[dict[str, Any]]:
    """Return the rule-based plan's calls as the case carries them."""
    return [
        {"tool": call.tool, "args": dict(call.args), "classes": list(call.classes)}
        for call in completed
    ]


def _refusal_reason(cap: Capture, tool: str, args: Mapping[str, Any]) -> str:
    """Return the reason the loop's own validator gives for refusing one action, verbatim."""
    from quaestor.agent.planner import FollowUpAction, validate_action

    call, reason = validate_action(
        FollowUpAction(tool=tool, args=dict(args), why=""), cap.registry, cap.package
    )
    if call is not None:
        raise ValueError(f"{tool}({args}) was not refused, so there is no reason to record")
    return reason


def _tool_error(cap: Capture, tool: str, args: Mapping[str, Any]) -> str:
    """Return the message one tool raises on this run, verbatim, by making it raise.

    The message a case carries in its history block is the tool's own sentence, not a paraphrase
    of it: the point of the case is that the loop is shown what a real failure looks like, and a
    sentence written here would be a second version of it that could drift (D-084).
    """
    from quaestor.artifacts.store import ArtifactStore
    from quaestor.errors import ToolError
    from quaestor.tools.registry import ToolContext

    ctx = ToolContext(
        package=cap.package,
        store=ArtifactStore(cap.out_dir / "artifacts"),
        out_dir=cap.out_dir / "run",
    )
    try:
        cap.registry.call(tool, dict(args), ctx)
    except ToolError as exc:
        return exc.message
    raise ValueError(f"{tool}({args}) did not raise, so there is no message to record")


def plan_cases(cap: Capture) -> list[dict[str, Any]]:
    """Build the two planning cases: the loop's first step, and a step after two mistakes."""
    from quaestor.agent.planner import MAX_FOLLOW_UP_STEPS, loop_prompt

    loop = cap.loop
    shared_input = {
        "candidates": _candidate_payloads(loop["candidates"]),
        "completed": _completed_payloads(loop["completed"]),
        "artifact_names": list(loop["artifact_names"]),
        "columns": list(loop["data_columns"]),
    }
    not_contains = [*UNOFFERED_TOOLS, *INVENTED_TOOLS]

    first_prompt = loop_prompt(
        cap.registry,
        cap.package,
        remaining=MAX_FOLLOW_UP_STEPS,
        candidates=loop["candidates"],
        completed=loop["completed"],
        artifact_names=loop["artifact_names"],
        data_columns=loop["data_columns"],
        history=(),
    )

    stability_reason = _refusal_reason(cap, "check_stability", {})
    wrong_column = {"subpopulation": {"column": "credit_limit", "rule": "above_median"}}
    column_error = _tool_error(cap, "compute_metrics", wrong_column)
    history = [
        {
            "step": 1,
            "tool": "check_stability",
            "args": {},
            "why": "compare the model's discrimination across regimes",
            "accepted": False,
            "reason": stability_reason,
            "executed": False,
            "error": "",
        },
        {
            "step": 2,
            "tool": "compute_metrics",
            "args": wrong_column,
            "why": "recompute the metrics on the high-limit half of each split",
            "accepted": True,
            "reason": "",
            "executed": False,
            "error": column_error,
        },
    ]
    after_prompt = loop_prompt(
        cap.registry,
        cap.package,
        remaining=MAX_FOLLOW_UP_STEPS - 2,
        candidates=loop["candidates"],
        completed=loop["completed"],
        artifact_names=loop["artifact_names"],
        data_columns=loop["data_columns"],
        history=_plan_steps(history),
    )

    return [
        {
            "id": "plan_followup.first_step",
            "input": {**shared_input, "remaining": MAX_FOLLOW_UP_STEPS, "history": []},
            "metadata": {
                "package": "credit_default",
                "version": cap.package.spec.version,
                "synthetic_n": SYNTHETIC_N,
                "seed": SUBJECT_SEED,
                "prompt_bytes": len(first_prompt.encode("utf-8")),
            },
            "assertions": [
                {
                    "type": "schema_valid",
                    "schema_file": "tests/probatio/schemas/follow_up_action.json",
                },
                {"type": "not_contains", "all": not_contains, "case_sensitive": False},
            ],
            "budget": budget_for(len(first_prompt.encode("utf-8")), LIVE_PLAN_OUTPUT_TOKENS),
            "snapshot": "scores",
            "tags": ["planner", "credit_default", "synthetic"],
        },
        {
            "id": "plan_followup.after_refusal",
            "input": {
                **shared_input,
                "remaining": MAX_FOLLOW_UP_STEPS - 2,
                "history": history,
            },
            "metadata": {
                "package": "credit_default",
                "version": cap.package.spec.version,
                "synthetic_n": SYNTHETIC_N,
                "seed": SUBJECT_SEED,
                "prompt_bytes": len(after_prompt.encode("utf-8")),
            },
            "assertions": [
                {
                    "type": "schema_valid",
                    "schema_file": "tests/probatio/schemas/follow_up_action.json",
                },
                {
                    "type": "not_contains",
                    "all": [*not_contains, "credit_limit"],
                    "case_sensitive": False,
                },
            ],
            "budget": budget_for(len(after_prompt.encode("utf-8")), LIVE_PLAN_OUTPUT_TOKENS),
            "snapshot": "scores",
            "tags": ["planner", "credit_default", "synthetic", "after-refusal"],
        },
    ]


def _plan_steps(history: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Rebuild the loop's own `PlanStep` objects from the form a case carries them in."""
    from quaestor.agent.planner import FollowUpAction, PlannedCall, PlanStep

    steps: list[Any] = []
    for entry in history:
        action = FollowUpAction(
            tool=entry["tool"], args=dict(entry["args"]), why=entry["why"], stop=False
        )
        call = (
            PlannedCall(entry["tool"], dict(entry["args"]), entry["why"], source="loop")
            if entry["accepted"]
            else None
        )
        steps.append(
            PlanStep(
                step=int(entry["step"]),
                action=action,
                accepted=bool(entry["accepted"]),
                reason=entry["reason"],
                call=call,
                executed=bool(entry["executed"]),
                error=entry["error"],
            )
        )
    return steps


# -- the schemas the `schema_valid` assertions point at ----------------------------------------


def schemas() -> dict[str, dict[str, Any]]:
    """Return the three JSON Schemas, generated from the pydantic models they are about.

    Generated, never transcribed: a schema file written by hand is a second statement of what the
    drafter returns, and the point of `schema_valid` is that the answer matches the model
    `structured()` will validate it against.
    """
    from quaestor.agent.planner import FollowUpAction
    from quaestor.report.drafter import DraftedSection
    from quaestor.verifier.extract import ExtractedClaims

    return {
        "drafted_section": DraftedSection.model_json_schema(),
        "extracted_claims": ExtractedClaims.model_json_schema(),
        "follow_up_action": FollowUpAction.model_json_schema(),
    }


# -- writing ------------------------------------------------------------------------------------


class _BlockDumper(yaml.SafeDumper):
    """A dumper that writes multi-line strings as literal blocks and never emits an anchor.

    Two cases of one family share a candidate list, and PyYAML would write the second as
    ``*id001``. A committed case has to be readable on its own -- a reviewer diffing the file
    should see what the second case is given, not a pointer to it -- so aliasing is off and the
    value is repeated.
    """

    def ignore_aliases(self, data: Any) -> bool:
        """Never emit an anchor or an alias, however many times a value is shared."""
        return True


def _block_string(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    """Represent a string, choosing the literal block style when it spans lines."""
    if "\n" in value:
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", value)


_BlockDumper.add_representer(str, _block_string)


def dump_cases(cases: Sequence[Mapping[str, Any]]) -> str:
    """Render a family of cases as the YAML document that is committed."""
    return yaml.dump(
        list(cases),
        Dumper=_BlockDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=98,
    )


def dump_schema(schema: Mapping[str, Any]) -> str:
    """Render one JSON Schema as the file that is committed."""
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


# -- pinning the prompt a tape will be keyed on -------------------------------------------------


class _PromptRecorder:
    """A provider that answers with one fixed valid JSON object and keeps the prompt it was sent.

    Attributes:
        name: What a tape would record; nothing ever tapes this one.
        answer: The reply, chosen so that `structured()` validates it on the first attempt and
            makes exactly one call.
        prompt: The last prompt it was sent, which is what a cassette key hashes.
    """

    name = "prompt-recorder"

    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.prompt = ""

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Any:
        """Record the prompt and answer with the fixed reply."""
        from quaestor.llm.base import Completion

        self.prompt = prompt
        return Completion(text=self.answer, model=self.name)


VALID_ANSWERS: Final[Mapping[str, str]] = {
    "draft_section": '{"markdown": "x"}',
    "extract_claims": '{"claims": []}',
    "plan_followup": '{"stop": true}',
}
"""One answer per family that `structured()` accepts, so the recorder is called exactly once."""


def prompt_sent(case: Any) -> str:
    """Return the prompt this case's system under test will actually send, verbatim.

    Not the prompt `Drafter.prompt` or `loop_prompt` composes: the one `structured()` sends, with
    the strict-JSON instruction and the pydantic schema appended. That is the string a cassette
    key hashes, so it is the string a case has to pin.
    """
    import probatiosupport

    family = case.id.partition(".")[0]
    recorder = _PromptRecorder(VALID_ANSWERS[family])
    runner = {
        "draft_section": probatiosupport.draft_answer,
        "extract_claims": probatiosupport.extract_answer,
        "plan_followup": probatiosupport.plan_answer,
    }[family]
    runner(case, recorder)
    return recorder.prompt


def prompt_digest(prompt: str) -> str:
    """Return the sixteen hex characters a case carries as `metadata.prompt_sha256`."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


RUBRICS_DIR: Final = HERE / "rubrics"
"""Where a judge assertion's rubric name resolves; the requesting module's own directory."""


def rubric_digest(name: str) -> str:
    """Return the digest a case carries as `metadata.rubric_sha256`.

    Probatio's own `Rubric.content_hash`, not a hash of this module's choosing, because that is
    what a judge validation record pins: one number that means "this rubric text" in the case
    file, in the validation record and in the warning that says the judge is unvalidated.

    A rubric is part of every judge prompt, so editing it changes every judge interaction key and
    strands every judge tape -- which is D-147's failure mode reached through a second door, and
    the door the interrupted record run of 2026-09-08 actually went through (D-148).
    """
    from probatio.judge import resolve_rubric

    return resolve_rubric(name, rubric_dirs=[RUBRICS_DIR]).content_hash[:16]


def with_prompt_digests(cases: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Add `metadata.prompt_sha256` to each case, computed by running its own SUT once.

    A byte count does not pin a prompt: replacing `above_median` with `below_median` and
    `minimum` with `maximum` in `_LOOP_INSTRUCTION` -- which is exactly what D-146 did, one
    command before a recording -- changes every planning tape's cassette key and not one byte of
    the case file. The digest is what makes a prompt change fail the offline suite (D-147).
    """
    from probatio.case import LLMCase

    stamped: list[dict[str, Any]] = []
    for case in cases:
        entry = json.loads(json.dumps(case))
        entry["metadata"]["prompt_sha256"] = prompt_digest(
            prompt_sent(LLMCase.model_validate(entry))
        )
        stamped.append(entry)
    return stamped


def build(cap: Capture) -> dict[Path, str]:
    """Return every file this module owns, path to text."""
    written: dict[Path, str] = {
        CASES_DIR / "draft_section.yaml": dump_cases(with_prompt_digests(draft_cases(cap))),
        CASES_DIR / "extract_claims.yaml": dump_cases(with_prompt_digests(extract_cases())),
        CASES_DIR / "plan_followup.yaml": dump_cases(with_prompt_digests(plan_cases(cap))),
    }
    for name, schema in schemas().items():
        written[SCHEMAS_DIR / f"{name}.json"] = dump_schema(schema)
    return written


def written_paths() -> Iterator[Path]:
    """Yield every path `build` writes, without running the pipeline."""
    yield CASES_DIR / "draft_section.yaml"
    yield CASES_DIR / "extract_claims.yaml"
    yield CASES_DIR / "plan_followup.yaml"
    for name in ("drafted_section", "extracted_claims", "follow_up_action"):
        yield SCHEMAS_DIR / f"{name}.json"


def main() -> int:
    """Rewrite every committed case and schema from a fresh offline run."""
    with TemporaryDirectory(prefix="quaestor-probatio-cases-") as scratch:
        cap = capture(Path(scratch) / "run")
        files = build(cap)
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO_ROOT)} ({len(text.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
