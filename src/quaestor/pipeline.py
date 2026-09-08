"""``validate()``: the pipeline entry of spec section 9, and the one place the phases meet.

``validate(package, llm=..., config=..., data_dir=..., synthetic=..., out=...)`` runs a package
through every layer this project has built and writes ``report.md``, ``claims.json``,
``findings.json``, ``trace.jsonl`` and the artifact store under ``out``. The order is fixed and is
the argument of the whole design:

1. **Plan** the checks from ``package.yaml`` (Phase 8, :mod:`quaestor.agent.planner`), and under
   ``full_agent`` let a bounded loop add at most four more.
2. **Run** them (Phase 5), which is the only way an artifact ever enters the store.
3. **Promote** the candidates they raised into findings (Phase 7), each of which needs evidence
   that is in that store or it cannot be constructed at all.
4. **Draft** the seven sections (Phase 8), showing the model only what it may cite.
5. **Verify** every number it wrote against the store (Phase 7), before repair and after.
6. **Repair** what did not verify, twice at most, then wrap what still does not.
7. **Render**, and refuse to write a report that breaks a rule of ``docs/REPORT_SCHEMA.md``.

The model is never between steps 2 and 3: it does not decide what ran, and it does not mint
findings. It writes prose, and the prose is checked.

Which of steps 1, 4 and 6 happen is the configuration's business and not this module's; the
three arms of the study differ only in :data:`quaestor.configs.CONFIGURATIONS` (D-070).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .agent.planner import (
    PlannedCall,
    PlanStep,
    completed_calls,
    follow_up_plan,
    guidance_queries,
    rule_based_plan,
)
from .artifacts.store import ArtifactKind, ArtifactStore
from .configs import SCREENED_CLASSES, ConfigSpec, Narrative, PlanMode, config_for
from .errors import ArtifactError
from .findings import (
    CandidateNotPromoted,
    DefectClass,
    Finding,
    FindingCandidate,
    FindingsDocument,
    Severity,
)
from .hashing import stable_hash
from .llm.base import LLM
from .llm.structured import structured
from .package import ModelPackage, load_package
from .package.spec import ModelType
from .report.drafter import Drafter, GuidanceSpan, spans_from_payload, template_section
from .report.renderer import NotChecked, ReportInputs, write_report
from .report.repair import (
    DraftInputs,
    SectionDraft,
    repair_sections,
    wrap_unverified,
)
from .report.sections import ArtifactBrief, SectionBrief, artifact_briefs, ordered_briefs
from .tools import ToolContext, ToolResult, default_registry, guidance_name
from .tools.thresholds import Thresholds
from .trace import EventType, TraceEvent, TraceReader, TraceWriter
from .verifier.claim import Claim, VerifiedClaim
from .verifier.claims_doc import ClaimsDocument
from .verifier.developer import verify_developer_claims
from .verifier.extract import Extraction, extract, extraction_from, merge_exclusions
from .verifier.match import Match, match_claims
from .vocab import Configuration, ReportSection

__all__ = [
    "CLAIMS_FILE",
    "RUN_STAMP_FORMAT",
    "FINDINGS_FILE",
    "CURRENT_GUIDANCE",
    "PLAIN_PROFILE",
    "REPORT_FILE",
    "TRACE_FILE",
    "UNEVIDENCED_PREFIX",
    "PlainFinding",
    "PlainReport",
    "ValidationRun",
    "validate",
]

REPORT_FILE: Final = "report.md"
CLAIMS_FILE: Final = "claims.json"
FINDINGS_FILE: Final = "findings.json"
TRACE_FILE: Final = "trace.jsonl"
"""The four files spec section 8 says a run writes, beside ``artifacts/``."""

PLAIN_PROFILE: Final = "plain_llm.profile"
"""The raw data profile the ``plain_llm`` baseline is handed (spec section 3.13).

It is stored as an artifact rather than pasted into a prompt so that the baseline can cite it, and
so is held to the same evidence rule as everything else: the arm without tools still may not name
a number that is not in the store.
"""

CURRENT_GUIDANCE: Final = "SR26-2"
"""The document a report anchors to by default: the 2026 revision of SR 11-7 (D-055)."""

UNEVIDENCED_PREFIX: Final = "unevidenced:"
"""How an unevidenced ``plain_llm`` finding is marked in ``candidates_not_promoted`` (D-072)."""

UNEVIDENCED_RECORD: Final = "unevidenced_record"
"""``unevidenced_record.<i>``: the stored record of a finding whose evidence resolves to nothing."""

_PLAIN_INSTRUCTION: Final = """\
You are writing a model-validation report on the package {package} version {version}, a
{model_type} model. You have no tools: what follows is everything the subject itself wrote.

Write the whole report as markdown, with exactly these level-2 headings, in this order:
{headings}

Then list the defects you believe you have found, as JSON objects under "findings", each with a
"defect_class" from {classes}, a "severity" from high/medium/low/info, a "title", a "narrative",
and "evidence": the logical names or hash prefixes of the artifacts that show it. A finding whose
evidence names nothing in the store is recorded as unevidenced.

metrics.json:
{metrics}

model_summary.json:
{model_summary}

features.json:
{features}

splits.json:
{splits}

Raw data profile of the training split:
{profile}

Artifacts you may cite, as [[art:<hash8>:<logical_name>]] or
[[art:<hash8>:<logical_name>#<path>]]:
{artifacts}"""
"""The baseline's one call: the four contract files, the raw profile, and nothing else."""


class PlainFinding(BaseModel):
    """One finding as the ``plain_llm`` baseline reports it, before anything is checked.

    Attributes:
        defect_class: One of the twelve codes.
        severity: What the model calls it.
        title: One line.
        narrative: The prose.
        evidence: The artifacts it names, by logical name or by hash prefix; often neither.
    """

    model_config = ConfigDict(extra="forbid")

    defect_class: DefectClass
    severity: Severity = Severity.medium
    title: str = ""
    narrative: str = ""
    evidence: list[str] = Field(default_factory=list)


class PlainReport(BaseModel):
    """What the ``plain_llm`` baseline is asked for: one report and a list of findings.

    Attributes:
        markdown: The whole report, with the seven level-2 headings.
        findings: The defects the model believes it found.
    """

    model_config = ConfigDict(extra="forbid")

    markdown: str = ""
    findings: list[PlainFinding] = Field(default_factory=list)


@dataclass
class ValidationRun:
    """What one call to :func:`validate` produced.

    Attributes:
        package: The loaded package.
        configuration: Which configuration ran.
        run_id: Joins every file this run wrote.
        out_dir: Where they were written.
        report_path: The rendered report.
        report: The report's text.
        claims: The claims document, both grounding figures included.
        findings: The findings document.
        store: The run's artifact store.
        plan: The rule-based plan, as executed.
        steps: The bounded loop's steps, accepted and refused.
        results: One result per tool call, in order.
    """

    package: ModelPackage
    configuration: Configuration
    run_id: str
    out_dir: Path
    report_path: Path
    report: str
    claims: ClaimsDocument
    findings: FindingsDocument
    store: ArtifactStore
    plan: list[PlannedCall] = field(default_factory=list)
    steps: list[PlanStep] = field(default_factory=list)
    results: list[ToolResult] = field(default_factory=list)

    @property
    def precision_pre(self) -> float:
        """Grounding precision before repair, as the front matter prints it."""
        return self.claims.precision_pre

    @property
    def precision_post(self) -> float:
        """Grounding precision after the last repair round."""
        return self.claims.precision_post


RUN_STAMP_FORMAT: Final = "%Y%m%dT%H%M%SZ"
"""How the per-run component of a run id is spelled: UTC, to the second (DECISIONS D-093)."""


def _run_id(  # noqa: PLR0913 - the identifier is a function of everything that identifies a run
    package: ModelPackage,
    config: ConfigSpec,
    mode: str,
    n: int | None,
    seed: int | None,
    at: datetime,
) -> str:
    """Return a run identifier that names the run and the occasion, so no two runs share one.

    The hash is what it always was -- the package, its version, the configuration, the data mode,
    the row count and the seed -- and it is what makes two runs of the same *inputs* recognisable
    as such. The timestamp in front of it is what makes them distinguishable: the first and third
    live ``credit_default`` validations both carried ``credit_default-full_agent-d03b07c6``, two
    runs seventeen minutes and one build apart with the same name in every file each wrote, which
    is a joining key that does not join (D-093).

    Args:
        package: The loaded package.
        config: The configuration.
        mode: ``synthetic`` or ``real``.
        n: The synthetic row count, or ``None``.
        seed: The seed passed to the subject, or ``None``.
        at: When the run started, as the report's own timestamp records it -- so a caller that
            pins ``generated`` for a byte-stable test pins the run id with it.

    Returns:
        ``<package>-<configuration>-<UTC timestamp>-<input hash>``.
    """
    digest = stable_hash(
        {
            "package": package.spec.name,
            "version": package.spec.version,
            "configuration": config.name.value,
            "data_mode": mode,
            "synthetic_n": n,
            "seed": seed,
        },
        length=8,
    )
    stamp = at.astimezone(UTC).strftime(RUN_STAMP_FORMAT)
    return f"{package.spec.name}-{config.name.value}-{stamp}-{digest}"


def _model_id(events: Sequence[TraceEvent]) -> str:
    """Return the model that answered this run, from the completions the trace recorded.

    Args:
        events: The run's trace events.

    Returns:
        The model id every ``llm_call`` reported, or a comma-separated list where a run somehow
        met more than one, or ``""`` where no model answered at all -- which is what ``rules_only``
        is, and is not the same fact as "the adapter was called ``fake``" (D-093).
    """
    seen: list[str] = []
    for event in events:
        if event.type is not EventType.llm_call:
            continue
        name = str(event.payload.get("model") or "")
        if name and name not in seen:
            seen.append(name)
    return ", ".join(seen)


def _profile_for_baseline(out_dir: Path, store: ArtifactStore, split: str = "train") -> Any:
    """Describe the training matrix the subject wrote, for the one arm that has no profiler.

    Spec section 3.13 hands the baseline "the raw data profile". No check computes it -- that is
    the point of the arm -- so it is a plain description of the columns the subject used, stored
    as an artifact so that the baseline can cite it like anything else.
    """
    path = out_dir / f"data_{split}.csv"
    if not path.is_file():
        return {}
    frame = pd.read_csv(path)
    numeric = frame.select_dtypes("number")
    profile = {
        "n_rows": int(len(frame)),
        "columns": {
            str(column): {
                "mean": float(numeric[column].mean()),
                "std": float(numeric[column].std()),
                "min": float(numeric[column].min()),
                "max": float(numeric[column].max()),
                "missing": float(frame[column].isna().mean()),
            }
            for column in numeric.columns
        },
    }
    store.put(PLAIN_PROFILE, profile, ArtifactKind.json, f"raw profile of data_{split}.csv")
    return profile


def _payload(store: ArtifactStore, name: str) -> Any:
    """Return one JSON artifact's payload, or an empty object when the run did not write it."""
    return store.load(name) if name in store else {}


def _promote(
    candidates: Sequence[FindingCandidate],
    store: ArtifactStore,
    trace: TraceWriter | None,
) -> tuple[list[Finding], list[CandidateNotPromoted]]:
    """Promote every candidate to a finding, merging the candidates of one class.

    The validator promotes what the checks raised and changes no severity: a severity change needs
    a reason a human wrote, and nothing in this pipeline has one. A group whose candidates name no
    artifact between them cannot become a finding -- the evidence rule is the constraint the
    project is built around -- and is recorded as not promoted, which is what happens to a
    pre-run ``L1`` on a run where ``check_leakage`` never got to attach its artifact.
    """
    grouped: dict[DefectClass, list[FindingCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.defect_class, []).append(candidate)
    findings: list[Finding] = []
    declined: list[CandidateNotPromoted] = []
    for group in grouped.values():
        if not any(candidate.evidence for candidate in group):
            declined += [
                CandidateNotPromoted(
                    defect_class=candidate.defect_class,
                    tool=candidate.tool,
                    evidence=["00000000"],
                    reason=(
                        "raised before any tool ran, so no artifact names it; the check that "
                        "would attach its evidence did not run"
                    ),
                )
                for candidate in group
            ]
            continue
        findings.append(Finding.from_candidates(group, store=store, trace=trace))
    return findings, declined


def _checks_without_candidates(
    tools_run: Sequence[str], raised: Sequence[DefectClass]
) -> dict[str, list[DefectClass]]:
    """Return the classes each check screened for and did not raise."""
    seen = set(raised)
    clear: dict[str, list[DefectClass]] = {}
    for tool in dict.fromkeys(tools_run):
        classes = [item for item in SCREENED_CLASSES.get(tool, ()) if item not in seen]
        if classes:
            clear[tool] = classes
    return clear


def _guidance(store: ArtifactStore) -> dict[ReportSection, list[GuidanceSpan]]:
    """Read back the spans the plan retrieved, by the logical name each was stored under."""
    spans: dict[ReportSection, list[GuidanceSpan]] = {}
    for section, query in guidance_queries():
        name = guidance_name(query, 3, None)
        if name in store:
            spans[ReportSection(section)] = _current_first(spans_from_payload(store.load(name)))
    return spans


def _current_first(spans: Sequence[GuidanceSpan]) -> list[GuidanceSpan]:
    """Put the current guidance first, keeping the retriever's order inside each document.

    The corpus holds SR 11-7 and the 2026 revision that superseded it, and both are retrieved,
    because a historical citation has to keep resolving (D-055). A report written today should
    anchor to the current text, so ``SR26-2`` spans are shown first and the superseded ones stay
    available for a section the revision does not cover.
    """
    return [span for span in spans if span.doc == CURRENT_GUIDANCE] + [
        span for span in spans if span.doc != CURRENT_GUIDANCE
    ]


def _draft_inputs(
    store: ArtifactStore,
    briefs: Sequence[SectionBrief],
    candidates_by_section: Mapping[ReportSection, list[FindingCandidate]],
    spans: Mapping[ReportSection, list[GuidanceSpan]],
    findings: Sequence[Finding],
) -> dict[ReportSection, DraftInputs]:
    """Assemble, per section, everything the drafter is allowed to see."""
    evidence_names = sorted(
        {store.get(digest).name for finding in findings for digest in finding.evidence}
    )
    inputs: dict[ReportSection, DraftInputs] = {}
    for brief in briefs:
        extra = evidence_names if brief.section is ReportSection.findings else ()
        artifacts: list[ArtifactBrief] = artifact_briefs(store, brief, extra=extra)
        inputs[brief.section] = DraftInputs(
            artifacts=artifacts,
            spans=spans.get(brief.section, []),
            candidates=candidates_by_section.get(brief.section, []),
            findings=list(findings) if brief.section is ReportSection.findings else [],
        )
    return inputs


def _not_checked(
    package: ModelPackage,
    config: ConfigSpec,
    tools_run: Sequence[str],
    developer_note: str | None,
) -> list[NotChecked]:
    """Build Appendix D: what did not run, and why it did not."""
    spec = package.spec
    rows: list[NotChecked] = []
    if "check_stability" not in tools_run:
        rows.append(
            NotChecked(
                "`check_stability` (R1)",
                "package declares no `regime.column`"
                if not spec.regime.column
                else "this configuration runs no checks",
            )
        )
    if "run_scenarios" not in tools_run:
        rows.append(
            NotChecked(
                "`run_scenarios` (X1)",
                f"not applicable to `{spec.model_type.value}`"
                if spec.model_type is ModelType.binary_classification
                else "this configuration runs no checks",
            )
        )
    if spec.splits.out_of_time is None and spec.splits.vintage_holdout is None:
        rows.append(
            NotChecked(
                "out-of-time and vintage-holdout metrics (O1, second rule)",
                "package declares neither split",
            )
        )
    if developer_note:
        rows.append(NotChecked("developer claims (T1, claim channel)", developer_note))
    if package.docs_dir is None:
        rows.append(NotChecked("developer documentation", "package has no `docs/` directory"))
    if spec.data.manifest is None:
        rows.append(NotChecked("data manifest", "`data.manifest` is null in `package.yaml`"))
    elif package.data_dir is None:
        rows.append(NotChecked("data manifest", "not verified: the run read no data directory"))
    if not config.uses_tools:
        rows.append(
            NotChecked(
                "every check of spec 3.7 but `run_model`",
                f"`{config.name.value}` runs the subject and one model call, by design",
            )
        )
    if not config.calls_a_model:
        rows.append(
            NotChecked(
                "drafted narrative and the repair loop",
                f"`{config.name.value}` calls no model; the narrative is a template",
            )
        )
    return rows


def _split_sections(markdown: str, briefs: Sequence[SectionBrief]) -> dict[ReportSection, str]:
    """Split one model's whole-report answer into the seven sections, by their headings."""
    remaining = markdown
    found: dict[ReportSection, str] = {}
    order = list(briefs)
    for position, brief in enumerate(order):
        if brief.heading not in remaining:
            continue
        _, _, rest = remaining.partition(brief.heading)
        nxt = next(
            (later.heading for later in order[position + 1 :] if later.heading in rest), None
        )
        body = rest.split(nxt, 1)[0] if nxt else rest
        found[brief.section] = body.strip()
        remaining = rest
    return found


def _plain_findings(
    answer: PlainReport,
    store: ArtifactStore,
    trace: TraceWriter | None,
) -> tuple[list[Finding], list[CandidateNotPromoted]]:
    """Turn the baseline's own JSON list into findings, or into unevidenced records (D-072)."""
    findings: list[Finding] = []
    declined: list[CandidateNotPromoted] = []
    for index, item in enumerate(answer.findings):
        resolved = _resolve_evidence(item.evidence, store)
        if resolved:
            candidate = FindingCandidate(
                defect_class=item.defect_class,
                evidence=resolved,
                detail=item.title or item.narrative or item.defect_class.value,
                suggested_severity=item.severity,
                tool=Configuration.plain_llm.value,
            )
            findings.append(
                Finding.from_candidates(
                    [candidate],
                    store=store,
                    title=item.title or item.narrative[:80] or item.defect_class.value,
                    narrative=item.narrative or item.title or item.defect_class.value,
                    trace=trace,
                )
            )
            continue
        record = store.put(
            f"{UNEVIDENCED_RECORD}.{index}",
            {
                "defect_class": item.defect_class.value,
                "severity": item.severity.value,
                "title": item.title,
                "narrative": item.narrative,
                "evidence_named": list(item.evidence),
                "resolves": False,
            },
            ArtifactKind.json,
            f"unevidenced {item.defect_class.value} finding {index} from the plain_llm baseline",
        )
        declined.append(
            CandidateNotPromoted(
                defect_class=item.defect_class,
                tool=Configuration.plain_llm.value,
                evidence=[record.hash[:8]],
                reason=(
                    f"{UNEVIDENCED_PREFIX} the model named {list(item.evidence)}, none of which "
                    f"is in the artifact store; the claim is recorded as {record.name}"
                ),
            )
        )
    return findings, declined


def _resolve_evidence(named: Sequence[str], store: ArtifactStore) -> list[str]:
    """Resolve what a model called evidence to hashes that are actually in the store."""
    resolved: list[str] = []
    for item in named:
        text = item.strip()
        if text in store:
            resolved.append(store.entry(text).hash[:8])
            continue
        try:
            resolved.append(store.get(text).hash[:8])
        except ArtifactError:
            continue
    return sorted(set(resolved))


def validate(  # noqa: PLR0913, PLR0915 - the pipeline's steps are its signature and its body
    package: ModelPackage | Path | str,
    *,
    llm: LLM,
    config: Configuration | str = Configuration.full_agent,
    data_dir: Path | str | None = None,
    synthetic: int | None = None,
    out: Path | str,
    seed: int | None = None,
    thresholds: Thresholds | None = None,
    generated: datetime | None = None,
    quaestor_version: str = "",
    **params: Any,
) -> ValidationRun:
    """Validate one model package and write the four files of spec section 8.

    Args:
        package: The package, loaded or as a path.
        llm: The provider. ``FakeLLM`` offline; ``ClaudeCLILLM`` or ``AnthropicLLM`` live.
        config: Which of the three configurations to run.
        data_dir: Where the real data is, for a ``--data`` run.
        synthetic: How many rows to generate, for an offline run. Exactly one of this and
            ``data_dir``.
        out: Where to write ``report.md``, ``claims.json``, ``findings.json``, ``trace.jsonl`` and
            ``artifacts/``.
        seed: Passed to the subject, or ``None`` for the subject's own documented default.
        thresholds: Effective thresholds, defaulting to the spec 3.7 values.
        generated: The report's timestamp; injectable so that a test's report is byte-stable.
        quaestor_version: Stamped on the front matter; defaults to ``quaestor.__version__``.
        **params: Passed to the provider on every call, such as ``model``.

    Returns:
        The run: its documents, its store, and what the planner did.

    Raises:
        PackageError: The package does not load, or its manifest does not match.
        SandboxError: The subject failed in a way that leaves nothing to report on.
        ToolError: A planned call cannot run.
        ReportSchemaError: The rendered report breaks a rule of ``docs/REPORT_SCHEMA.md``.
    """
    spec_config = config_for(config)
    loaded = (
        package if isinstance(package, ModelPackage) else load_package(package, data_dir=data_dir)
    )
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_mode = "synthetic" if synthetic is not None else "real"
    started = generated or datetime.now(UTC)
    run_id = _run_id(loaded, spec_config, data_mode, synthetic, seed, started)
    trace = TraceWriter(out_dir / TRACE_FILE, run_id=run_id)
    store = ArtifactStore(out_dir / "artifacts")
    ctx = ToolContext(
        package=loaded,
        store=store,
        out_dir=out_dir / "run",
        trace=trace,
        thresholds=thresholds or Thresholds(),
    )
    registry = default_registry()

    plan = rule_based_plan(
        loaded,
        synthetic=synthetic,
        data_dir=data_dir,
        seed=seed,
        guidance=spec_config.retrieve_guidance,
    )
    if spec_config.plan == PlanMode.run_only:
        plan = plan[:1]
    results = [registry.call(call.tool, dict(call.args), ctx) for call in plan]
    candidates = [candidate for result in results for candidate in result.candidates]
    if spec_config.uses_tools:
        candidates = list(loaded.pre_run_candidates()) + candidates

    steps: list[PlanStep] = []
    if spec_config.max_follow_ups:

        def _execute(call: PlannedCall) -> ToolResult:
            result = registry.call(call.tool, dict(call.args), ctx)
            results.append(result)
            candidates.extend(result.candidates)
            return result

        steps = follow_up_plan(
            llm,
            registry,
            loaded,
            candidates=candidates,
            completed=completed_calls(plan, results),
            artifact_names=store.names(),
            roots=[out_dir] + ([Path(data_dir)] if data_dir is not None else []),
            max_steps=spec_config.max_follow_ups,
            trace=trace,
            execute=_execute,
            **params,
        )

    developer = None
    if spec_config.uses_tools:
        developer = verify_developer_claims(
            loaded, store, data_dir=Path(data_dir) if data_dir is not None else None
        )
        candidates += list(developer.candidates)
    developer_note = (
        developer.note
        if developer is not None
        else (f"`{spec_config.name.value}` runs no check over `package.yaml`'s declared claims")
    )

    findings, declined = _promote(candidates, store, trace)
    tools_run = [call.tool for call in plan] + [
        step.call.tool for step in steps if step.call is not None and step.executed
    ]
    document = FindingsDocument.build(
        package=loaded.spec.name,
        version=loaded.spec.version,
        configuration=spec_config.name,
        run_id=run_id,
        findings=findings,
        candidates_not_promoted=declined,
        checks_without_candidates=_checks_without_candidates(
            tools_run, [candidate.defect_class for candidate in candidates]
        ),
    )

    briefs = ordered_briefs(store, loaded.spec)
    spans = _guidance(store)
    from .report.drafter import merge_candidates  # noqa: PLC0415 - one caller, one import

    inputs = _draft_inputs(store, briefs, merge_candidates(candidates), spans, document.findings)
    drafter = Drafter(
        llm,
        package=loaded.spec.name,
        version=loaded.spec.version,
        trace=trace,
        **params,
    )

    declared: dict[ReportSection, list[Claim]] = {}
    if spec_config.narrative == Narrative.template:
        drafted = {}
        for brief in briefs:
            given = inputs[brief.section]
            markdown, claims = template_section(
                brief,
                artifacts=given.artifacts,
                spans=given.spans,
                candidates=given.candidates,
                findings=given.findings,
            )
            drafted[brief.section] = markdown
            declared[brief.section] = claims
    elif spec_config.narrative == Narrative.one_call:
        answer = _plain_call(llm, loaded, store, ctx, briefs, trace=trace, **params)
        drafted = _split_sections(answer.markdown, briefs)
        plain_findings, plain_declined = _plain_findings(answer, store, trace)
        document = FindingsDocument.build(
            package=loaded.spec.name,
            version=loaded.spec.version,
            configuration=spec_config.name,
            run_id=run_id,
            findings=plain_findings,
            candidates_not_promoted=plain_declined,
            checks_without_candidates={},
        )
    else:
        drafted = {
            brief.section: drafter.draft(
                brief,
                artifacts=inputs[brief.section].artifacts,
                spans=inputs[brief.section].spans,
                candidates=inputs[brief.section].candidates,
                findings=inputs[brief.section].findings,
            )
            for brief in briefs
        }

    def _verify(section: ReportSection, markdown: str) -> tuple[Extraction, list[Match]]:
        if spec_config.narrative == Narrative.template:
            extraction = extraction_from(
                section, markdown, declared.get(section, []), package_version=loaded.spec.version
            )
        else:
            extraction = extract(
                section,
                markdown,
                llm,
                package_version=loaded.spec.version,
                trace=trace,
                **params,
            )
        matches = match_claims(
            extraction.claims,
            store,
            unattributed=extraction.unattributed_ids,
            trace=trace,
        )
        return extraction, matches

    drafts: list[SectionDraft] = []
    for brief in briefs:
        markdown = drafted.get(brief.section, "").strip() or (
            "This section has nothing to report from this run."
        )
        extraction, matches = _verify(brief.section, markdown)
        drafts.append(
            SectionDraft(brief=brief, markdown=markdown, extraction=extraction, matches=matches)
        )
    pre_repair = [claim for draft in drafts for claim in draft.claims]

    repairs: list[Any] = []
    if spec_config.repair:
        outcome = repair_sections(
            drafts, drafter=drafter, verify=_verify, inputs=inputs, trace=trace
        )
        drafts = outcome.drafts
        repairs = outcome.repairs

    sections: dict[ReportSection, str] = {}
    post_repair: list[VerifiedClaim] = []
    for draft in drafts:
        sections[draft.section] = wrap_unverified(
            draft.markdown, draft.claims, package_version=loaded.spec.version
        )
        post_repair += draft.claims

    claims_document = ClaimsDocument.build(
        package=loaded.spec.name,
        version=loaded.spec.version,
        configuration=spec_config.name,
        run_id=run_id,
        pre_repair=pre_repair,
        post_repair=post_repair,
        repairs=repairs,
        developer_claims=developer.claims if developer is not None else [],
        developer_claims_note=developer_note,
        exclusions=merge_exclusions(draft.extraction for draft in drafts),
    )

    document = _redraft_findings(document, sections.get(ReportSection.findings, ""))
    events = list(TraceReader(trace.path))
    report_inputs = ReportInputs(
        package=loaded,
        configuration=spec_config.name,
        model=getattr(llm, "name", "unknown"),
        run_id=run_id,
        data_mode=data_mode,
        synthetic_n=synthetic,
        sections=sections,
        claims=claims_document,
        findings=document,
        store=store,
        events=events,
        not_checked=_not_checked(loaded, spec_config, tools_run, developer_note),
        model_id=_model_id(events),
        quaestor_version=quaestor_version or _quaestor_version(),
        generated=started,
    )
    report_path = write_report(report_inputs, out_dir / REPORT_FILE)
    claims_document.write(out_dir / CLAIMS_FILE)
    document.write(out_dir / FINDINGS_FILE)
    return ValidationRun(
        package=loaded,
        configuration=spec_config.name,
        run_id=run_id,
        out_dir=out_dir,
        report_path=report_path,
        report=report_path.read_text(encoding="utf-8"),
        claims=claims_document,
        findings=document,
        store=store,
        plan=plan,
        steps=steps,
        results=results,
    )


def _quaestor_version() -> str:
    """Return the installed version, imported at call time to keep the package import acyclic."""
    from . import __version__  # noqa: PLC0415 - quaestor/__init__.py imports this module

    return str(__version__)


def _redraft_findings(document: FindingsDocument, markdown: str) -> FindingsDocument:
    """Give each finding the title and narrative the drafter wrote for it (D-071)."""
    from .report.drafter import finding_heading  # noqa: PLC0415 - one caller, one import

    bodies: dict[str, str] = {}
    current = ""
    buffer: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("### "):
            bodies[current] = "\n".join(buffer).strip()
            current = line.strip()
            buffer = []
            continue
        buffer.append(line)
    bodies[current] = "\n".join(buffer).strip()

    updated = []
    for finding in document.findings:
        body = bodies.get(finding_heading(finding), "").strip()
        if not body:
            updated.append(finding)
            continue
        title, narrative = _title_and_narrative(body)
        updated.append(
            finding.model_copy(
                update={"title": title or finding.title, "narrative": narrative or body}
            )
        )
    return document.model_copy(update={"findings": updated})


def _title_and_narrative(body: str) -> tuple[str, str]:
    """Split a drafted finding into its bold title and the prose beneath it."""
    stripped = body.lstrip()
    if stripped.startswith("**") and "**" in stripped[2:]:
        end = stripped.index("**", 2)
        return stripped[2:end].strip(), stripped[end + 2 :].strip() or stripped[2:end].strip()
    return "", body


def _plain_call(
    llm: LLM,
    package: ModelPackage,
    store: ArtifactStore,
    ctx: ToolContext,
    briefs: Sequence[SectionBrief],
    *,
    trace: TraceWriter | None = None,
    **params: Any,
) -> PlainReport:
    """Make the baseline's one call, over the contract files and the raw profile."""
    profile = _profile_for_baseline(ctx.out_dir, store)
    citable = [
        {"name": name, "hash8": store.entry(name).hash[:8], "kind": store.entry(name).kind.value}
        for name in store.names()
    ]
    prompt = _PLAIN_INSTRUCTION.format(
        package=package.spec.name,
        version=package.spec.version,
        model_type=package.spec.model_type.value,
        headings="\n".join(brief.heading for brief in briefs),
        classes=[item.value for item in DefectClass],
        metrics=json.dumps(_payload(store, "run.metrics"), indent=1)[:6000],
        model_summary=json.dumps(_payload(store, "run.model_summary"), indent=1)[:6000],
        features=json.dumps(_payload(store, "run.features"), indent=1)[:6000],
        splits=json.dumps(_payload(store, "run.splits"), indent=1)[:6000],
        profile=json.dumps(profile, indent=1)[:6000],
        artifacts=json.dumps(citable, indent=1)[:8000],
    )
    return structured(llm, prompt, PlainReport, trace=trace, purpose="plain_llm", **params)
