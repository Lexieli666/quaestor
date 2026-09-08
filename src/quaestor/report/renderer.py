"""The renderer: front matter, renderer blocks, four appendices, and four refusals.

Spec section 3.11 and ``docs/REPORT_SCHEMA.md``. Everything in a report that is *not* drafted prose
is written here, from structured data: the YAML front matter, the scope block that carries the two
grounding figures to the first page, every expanded table, the level-3 heading of every finding,
and Appendices A to D. The drafter never writes a number it would have to transcribe, and the
renderer never writes a sentence.

Four refusals, from the schema's own ``x-quaestor-refusal-rules``:

* front matter that does not validate against ``REPORT_SCHEMA.json``;
* a report with no ``## Appendix A — Claims``;
* a report missing either grounding precision figure;
* under ``full_agent``, a number in sections 1-7 that no verified claim covers and that nothing
  wrapped ``⟦unverified: …⟧``.

The last one is the reason the wrapper exists (see :mod:`quaestor.report.repair`): a pipeline that
could silently drop an unverifiable number would improve its own headline by writing worse prose.
:func:`check_report` applies the structural checks ``tests/test_golden_spec.py`` applies to the
Phase 1 golden report, over a real run's output, which is what makes the golden a specification
rather than a description.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from ..artifacts.store import ArtifactKind, ArtifactStore
from ..errors import ReportSchemaError
from ..findings import FindingsDocument, Severity, severity_rank
from ..package import ModelPackage
from ..trace import EventType, TraceEvent
from ..verifier.claim import ClaimStatus, VerifiedClaim
from ..verifier.claims_doc import ClaimsDocument
from ..verifier.tokens import drafted_prose, eligible_numbers
from ..vocab import SECTION_ORDER, Configuration, ReportSection
from .drafter import finding_heading
from .repair import UNVERIFIED_OPEN, wrapped_values
from .schema import (
    ANY_TOKEN_RE,
    APPENDIX_A_HEADING,
    ARTIFACT_CITATION_RE,
    check_front_matter,
    check_structure,
    front_matter_of,
)
from .sections import OPEN_ITEMS_HEADING, four_significant_figures, section_heading

__all__ = [
    "APPENDICES",
    "NO_OPEN_ITEMS",
    "TEXT_WIDTH",
    "NotChecked",
    "ReportInputs",
    "check_report",
    "drafted_and_rendered_body",
    "drafted_body",
    "front_matter",
    "render_report",
    "scope_block",
    "uncovered_numbers",
    "write_report",
]

TEXT_WIDTH: Final = 60
"""How much of a claim's sentence Appendix A prints before an ellipsis, as the golden prints it."""

APPENDICES: Final = (
    "## Appendix A — Claims",
    "## Appendix B — Artifact index",
    "## Appendix C — Run trace summary",
    "## Appendix D — Not checked",
)
"""The four appendix headings, in order, exactly as ``REPORT_SCHEMA.json`` requires them."""

NO_OPEN_ITEMS: Final = "No open item was recorded for this validation."
"""What ``### Open items`` says when the drafter wrote nothing under it.

The heading is the renderer's, on the same argument as a finding's heading (D-071): the drafter is
asked to write the subsection and the renderer supplies what the drafter left out, so that the
report's shape is a property of the pipeline rather than of one model call.
"""

_BLOCK_BEGIN_SCOPE: Final = "<!-- quaestor:renderer:begin scope -->"
_BLOCK_END: Final = "<!-- quaestor:renderer:end -->"
_TABLE_DIRECTIVE: Final = "[[table:"


@dataclass(frozen=True)
class NotChecked:
    """One row of Appendix D: something this run did not check, and why.

    Attributes:
        item: What was not checked, named as the report names it elsewhere.
        reason: Why not, in one clause.
    """

    item: str
    reason: str


@dataclass
class ReportInputs:
    """Everything the renderer needs, all of it already decided by the pipeline.

    Attributes:
        package: The loaded package.
        configuration: Which configuration ran.
        model: The **adapter's** name -- ``claude-cli``, ``anthropic``, ``fake`` -- which is what
            Appendix C records, because it is what a reader would have to re-run.
        model_id: The model that actually answered, read off the completions the run received;
            empty where nothing answered, in which case the front matter falls back to the
            adapter's name (D-093).
        run_id: Joins the report to ``trace.jsonl``.
        data_mode: ``synthetic`` or ``real``.
        synthetic_n: How many rows were generated, in synthetic mode.
        sections: Section identifier to the prose it holds, wrapped and ready.
        claims: The claims document, from which Appendix A is rendered.
        findings: The findings document, from which section 6's headings are rendered.
        store: The run's artifact store, for Appendix B and for table expansion.
        events: The run's trace events, for Appendix C.
        not_checked: Appendix D's rows.
        quaestor_version: The version stamped on the front matter.
        generated: The one timestamp outside the trace.
    """

    package: ModelPackage
    configuration: Configuration
    model: str
    run_id: str
    data_mode: str
    synthetic_n: int | None
    sections: Mapping[ReportSection, str]
    claims: ClaimsDocument
    findings: FindingsDocument
    store: ArtifactStore
    events: Sequence[TraceEvent] = ()
    not_checked: Sequence[NotChecked] = ()
    model_id: str = ""
    quaestor_version: str = ""
    generated: datetime = field(default_factory=lambda: datetime.now(UTC))


def _cell(text: str) -> str:
    """Escape a markdown table cell, so that a citation or a sentence cannot break the row."""
    return text.replace("|", r"\|").replace("\n", " ")


def _truncate(text: str, width: int = TEXT_WIDTH) -> str:
    """Shorten a claim's sentence for Appendix A, as the golden report shortens it.

    Citations are removed before the sentence is cut. The row prints the claim's citation in its
    own column, and cutting a sentence at sixty characters would otherwise leave half a
    ``[[art:...]]`` token in the table -- a double-bracket token that is not a citation, which is
    exactly what the structural check forbids.
    """
    flat = " ".join(ANY_TOKEN_RE.sub("", text).split())
    return flat if len(flat) <= width else flat[:width].rstrip() + "…"


def _number(value: float) -> str:
    """Render a number for an appendix: an integer as an integer, anything else at ten digits."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.10g}"


def front_matter(inputs: ReportInputs) -> dict[str, Any]:
    """Build the report's front matter.

    Args:
        inputs: The rendering inputs.

    Returns:
        The front matter as a plain dict, in the order the report writes it.
    """
    spec = inputs.package.spec
    front: dict[str, Any] = {
        "schema_version": 1,
        "quaestor_version": inputs.quaestor_version,
        "package": spec.name,
        "version": spec.version,
        "model_type": spec.model_type.value,
        "configuration": inputs.configuration.value,
        "model": inputs.model_id or inputs.model,
        "run_id": inputs.run_id,
        "data_mode": inputs.data_mode,
    }
    if inputs.synthetic_n is not None:
        front["synthetic_n"] = int(inputs.synthetic_n)
    front["grounding_precision_pre"] = inputs.claims.precision_pre
    front["grounding_precision_post"] = inputs.claims.precision_post
    front["n_claims"] = inputs.claims.n_claims
    front["n_findings_by_severity"] = inputs.findings.counts_by_severity()
    front["generated"] = (
        inputs.generated.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    front["illustrative"] = False
    return front


def _front_matter_text(front: Mapping[str, Any]) -> str:
    """Render the front matter as YAML, quoting exactly what the golden report quotes."""
    quoted = {"quaestor_version", "version", "generated"}
    lines = ["---"]
    for key, value in front.items():
        if key in quoted:
            lines.append(f'{key}: "{value}"')
        elif key in ("grounding_precision_pre", "grounding_precision_post"):
            lines.append(f"{key}: {float(value):.4f}")
        elif key == "n_findings_by_severity":
            counts = ", ".join(f"{name}: {count}" for name, count in value.items())
            lines.append(f"{key}: {{{counts}}}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def scope_block(inputs: ReportInputs) -> str:
    """Render the scope block: the first thing under section 1, and the only place it may be.

    The two grounding figures reach "the report's first page" (spec section 3.10) through this
    block rather than through the drafter, which could not state a number that does not exist
    until after its own prose has been extracted (D-013).

    Args:
        inputs: The rendering inputs.

    Returns:
        The block, markers included.
    """
    spec = inputs.package.spec
    data = (
        f"synthetic, n = {inputs.synthetic_n}"
        if inputs.data_mode == "synthetic"
        else f"real, {spec.data.source}"
    )
    counts = inputs.findings.counts_by_severity()
    findings = " / ".join(str(counts[name.value]) for name in sorted(Severity, key=severity_rank))
    return "\n".join(
        (
            _BLOCK_BEGIN_SCOPE,
            "| package | configuration | model | data | "
            "grounding precision (pre → post repair) | "
            "findings (high / medium / low / info) |",
            "|---|---|---|---|---|---|",
            f"| `{spec.name}` v{spec.version} | `{inputs.configuration.value}` | "
            f"{_cell(inputs.model_id or inputs.model)} | {_cell(data)} | "
            f"{inputs.claims.precision_pre:.4f} → {inputs.claims.precision_post:.4f} | "
            f"{findings} |",
            _BLOCK_END,
        )
    )


def expand_tables(markdown: str, store: ArtifactStore) -> str:
    """Replace every ``[[table:<name>]]`` directive with the table, inside a renderer block.

    A directive naming something that is not a table artifact of this run is left as
    ``⟦unverified: table <name>⟧`` (``docs/REPORT_SCHEMA.md`` section 5): the drafter asked for a
    table that does not exist, and a reader should see that it asked.

    Args:
        markdown: The drafted section.
        store: The run's artifact store.

    Returns:
        The section with every directive expanded or marked.
    """
    lines: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not (stripped.startswith(_TABLE_DIRECTIVE) and stripped.endswith("]]")):
            lines.append(line)
            continue
        name = stripped[len(_TABLE_DIRECTIVE) : -2]
        lines.append(_table_block(name, store))
    return "\n".join(lines)


def _table_block(name: str, store: ArtifactStore) -> str:
    """Render one table artifact as a renderer block, or mark a directive that names no table."""
    if name not in store or store.entry(name).kind is not ArtifactKind.table:
        return f"⟦unverified: table {name}⟧"
    artifact = store.artifact(name)
    rows = store.load(name)
    if not rows:  # pragma: no cover - a stored table always has at least one row
        return f"⟦unverified: table {name}⟧"
    columns = list(rows[0])
    caption = artifact.summary or name
    body = [
        f"<!-- quaestor:renderer:begin table {name} -->",
        f"{caption[:1].upper()}{caption[1:]} {artifact.citation()}:",
        "",
        "| " + " | ".join(columns) + " |",
        "|" + "---|" * len(columns),
    ]
    body += [
        "| " + " | ".join(_table_cell(row[column]) for column in columns) + " |" for row in rows
    ]
    body.append(_BLOCK_END)
    return "\n".join(body)


def _table_cell(value: Any) -> str:
    """Render one cell of an expanded table: a count as a count, a measure at four figures.

    The drafter sees every artifact at four significant figures (spec section 3.11) and writes what
    it sees, so a renderer block that printed ``0.6855555556`` beside prose saying ``0.6856`` was
    showing the reader two spellings of one number and inviting the arithmetic to be checked
    against the wrong one. Integral values -- a decile's index, a bin's count -- are printed as
    integers, because ``900`` is not a measurement to four figures (DECISIONS D-094).

    Args:
        value: The cell as the table artifact holds it.

    Returns:
        The cell as the report prints it.
    """
    number = _as_number(value)
    if number is None:
        return _cell(str(value))
    if number == int(number) and abs(number) < 1e15:
        return str(int(number))
    return _cell(f"{four_significant_figures(number):g}")


def _as_number(value: Any) -> float | None:
    """Return a cell as a number, or ``None`` when it is not one.

    A table artifact's payload is canonical text -- ``store.put`` renders every cell through
    ``%.10g`` -- so the cells come back as strings and the type has to be recovered rather than
    read off. A period label such as ``2024-01`` is not a number and is printed as it stands.

    Args:
        value: The cell as the artifact holds it.

    Returns:
        The number, or ``None``.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _findings_section(markdown: str, inputs: ReportInputs) -> str:
    """Re-compose section 6 so that every finding appears, once, under the heading it was given.

    The drafter is asked to copy each finding's heading; the renderer takes it at its word where
    it did and supplies the heading where it did not, keeping whatever prose came back beneath it
    (DECISIONS D-071).
    """
    bodies = _split_by_heading(markdown)
    open_items = bodies.pop(OPEN_ITEMS_HEADING, "").strip()
    parts = [bodies.pop("", "").strip()]
    for finding in inputs.findings.findings:
        heading = finding_heading(finding)
        parts.append(heading)
        body = bodies.pop(heading, "").strip()
        parts.append(body or finding.narrative.strip())
    leftovers = [f"{heading}\n{body}".strip() for heading, body in bodies.items()]
    parts.extend(leftovers)
    not_promoted = inputs.findings.candidates_not_promoted
    if not_promoted:
        parts.append(
            "Candidates raised and not promoted: "
            + "; ".join(
                f"`{item.defect_class.value}` from `{item.tool}` — {item.reason}"
                for item in not_promoted
            )
        )
    else:
        parts.append("Candidates raised and not promoted: none.")
    clear = inputs.findings.checks_without_candidates
    if clear:
        parts.append(
            "Checks that ran and raised no candidate: "
            + ", ".join(
                f"`{tool}` ({', '.join(item.value for item in classes)})"
                for tool, classes in clear.items()
            )
            + "."
        )
    parts += [OPEN_ITEMS_HEADING, open_items or NO_OPEN_ITEMS]
    return "\n\n".join(part for part in parts if part)


def _split_by_heading(markdown: str) -> dict[str, str]:
    """Split a section into the text before its first ``###`` heading and one part per heading."""
    parts: dict[str, str] = {}
    current = ""
    buffer: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("### "):
            parts[current] = "\n".join(buffer).strip()
            current = line.strip()
            buffer = []
            continue
        buffer.append(line)
    parts[current] = "\n".join(buffer).strip()
    return parts


def _appendix_a(inputs: ReportInputs) -> str:
    """Render Appendix A: the two grounding figures, the repairs, the exclusions, every claim."""
    claims = inputs.claims
    pre = claims.grounding["pre_repair"]
    post = claims.grounding["post_repair"]
    failures = ", ".join(
        f"{count} {status}"
        for status, count in pre.status_counts.items()
        if status != ClaimStatus.verified.value and count
    )
    rewritten = len({(repair.section, repair.claim_id) for repair in claims.repairs})
    removed = _numbers_removed(inputs.events)
    lines = [
        APPENDIX_A_HEADING,
        "",
        f"Grounding precision {pre.precision:.4f} before repair "
        f"({pre.status_counts[ClaimStatus.verified.value]} of {pre.n_claims} claims verified"
        + (f"; {failures}" if failures else "")
        + f") and {post.precision:.4f} after {rewritten} claim(s) rewritten and "
        + f"{removed} number(s) removed from the prose. "
        + "Per section (post-repair): "
        + "; ".join(
            f"{name} {row.verified}/{row.n_claims}" for name, row in post.per_section.items()
        )
        + ".",
    ]
    if claims.repairs:
        lines += [
            "",
            "Repairs:",
            "",
            "| section | before | after | instruction to the drafter |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| {repair.section.value} | {_number(repair.before.value)} "
            f"({repair.before.status.value}) | {_number(repair.after.value)} "
            f"({repair.after.status.value}) | {_cell(repair.instruction)} |"
            for repair in claims.repairs
        ]
    lines += ["", _developer_claims_line(inputs), "", _exclusions_line(inputs), ""]
    lines += [
        "All claims, post-repair:",
        "",
        "| # | section | text | value | unit | metric | split | cmp | citation | status "
        "| artifact value |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for number, claim in enumerate(claims.post_repair, start=1):
        lines.append(_claim_row(number, claim))
    return "\n".join(lines)


def _numbers_removed(events: Sequence[TraceEvent]) -> int:
    """Count the numbers the repair loop's drafts dropped rather than cited, from the trace.

    A repair has two outcomes and ``claims.json`` records only one of them. A claim that was
    rewritten -- corrected, or given the citation it was missing -- is paired with what replaced it
    and becomes a ``repairs`` row; a number the drafter removed instead has no ``after`` side to
    pair with and is recorded on the ``repair`` trace event's ``removed`` field alone (D-073). So
    the appendix reporting "after N repaired claim(s)" printed N = 0 for the third live run, whose
    two repair rounds removed three numbers and rewrote none, which reads as a repair loop that did
    nothing. This is the other half of the sentence, read off the events (DECISIONS D-097).

    Args:
        events: The run's trace events.

    Returns:
        How many numbers the repair rounds removed.
    """
    return sum(
        len(event.payload.get("removed") or ())
        for event in events
        if event.type is EventType.repair
    )


def _claim_row(number: int, claim: VerifiedClaim) -> str:
    """Render one row of Appendix A's claims table."""
    citation = f"`{claim.citation}`" if claim.citation else ""
    artifact_value = "" if claim.artifact_value is None else _number(claim.artifact_value)
    return (
        f"| {number} | {claim.section.value} | {_cell(_truncate(claim.text))} "
        f"| {_number(claim.value)} | {claim.unit.value} | {claim.metric or ''} "
        f"| {claim.split.value if claim.split else ''} | {claim.comparison.value} "
        f"| {_cell(citation)} | {claim.status.value} | {artifact_value} |"
    )


def _developer_claims_line(inputs: ReportInputs) -> str:
    """Say what happened to `package.yaml`'s own declared numbers (D-016)."""
    claims = inputs.claims
    if claims.developer_claims:
        verified = sum(1 for claim in claims.developer_claims if claim.is_verified)
        return (
            f"Developer claims: {verified} of {len(claims.developer_claims)} declared in "
            "`package.yaml` verify against this run's artifacts."
        )
    note = claims.developer_claims_note or "none declared in `package.yaml`."
    return f"Developer claims: {note} See Appendix D."


def _exclusions_line(inputs: ReportInputs) -> str:
    """List the numeric tokens the pre-pass deliberately ignored, with examples (D-015)."""
    exclusions = inputs.claims.exclusions
    if not exclusions:
        return "Excluded numeric tokens (not claims): none."
    body = "; ".join(f"{item.pattern} ({', '.join(item.examples[:4])})" for item in exclusions)
    return f"Excluded numeric tokens (not claims): {body}."


def _cited_names(report: str) -> list[str]:
    """Every logical name the report cites, in first-seen order."""
    seen: list[str] = []
    for match in ARTIFACT_CITATION_RE.finditer(report):
        body = match.group(0)[len("[[art:") : -2]
        name = body.split(":", 1)[1].split("#", 1)[0]
        if name not in seen:
            seen.append(name)
    return seen


def _appendix_b(inputs: ReportInputs, body: str) -> str:
    """Render Appendix B: every artifact the report cites or a finding names, with its caption."""
    names = set(_cited_names(body))
    for finding in inputs.findings.findings:
        for digest in finding.evidence:
            names.add(inputs.store.get(digest).name)
    lines = [
        APPENDICES[1],
        "",
        f"The store holds {len(inputs.store)} artifacts; the {len(names)} this report cites or "
        "rests a finding on are indexed here.",
        "",
        "| logical name | hash | kind | value | summary |",
        "|---|---|---|---|---|",
    ]
    for name in sorted(names):
        entry = inputs.store.entry(name)
        if entry.kind is ArtifactKind.scalar and entry.value is not None:
            value = _number(entry.value)
        elif entry.kind is ArtifactKind.table:
            value = f"table, {len(inputs.store.load(name))} rows"
        else:
            value = entry.kind.value
        lines.append(
            f"| `{name}` | `{entry.hash[:8]}` | {entry.kind.value} | {value} "
            f"| {_cell(entry.summary)} |"
        )
    return "\n".join(lines)


def _counted(values: Iterable[str]) -> str:
    """Render a multiset as ``name n, name n``, in first-seen order."""
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return ", ".join(f"{name} {count}" for name, count in counts.items())


def _appendix_c(inputs: ReportInputs) -> str:
    """Render Appendix C from the trace, so every number in it recomputes from ``trace.jsonl``."""
    events = list(inputs.events)
    tools = [event for event in events if event.type is EventType.tool_call]
    llm = [event for event in events if event.type is EventType.llm_call]
    plans = [event for event in events if event.type is EventType.plan_step]
    repairs = [event for event in events if event.type is EventType.repair]
    reasks = [event for event in llm if event.payload.get("purpose") == "reask"]
    tokens_in = sum(int(event.payload.get("tokens_in") or 0) for event in llm)
    tokens_out = sum(int(event.payload.get("tokens_out") or 0) for event in llm)
    cost = sum(float(event.payload.get("cost_usd") or 0.0) for event in llm)
    wall = 0.0
    if events:
        wall = (events[-1].ts - events[0].ts).total_seconds()
    status = inputs.store.load("run.status") if "run.status" in inputs.store else {}
    memory_cap = str(status.get("memory_cap", "unknown")) if isinstance(status, Mapping) else "?"
    memory_mb = status.get("memory_cap_mb") if isinstance(status, Mapping) else None
    subject = (
        f"{inputs.store.value('run.duration_s'):.2f}"
        if "run.duration_s" in inputs.store
        else "not run"
    )
    rows = [
        ("tool calls", f"{len(tools)} ({_counted(str(e.payload.get('tool')) for e in tools)})"),
        ("plan steps (bounded loop)", str(len(plans))),
        ("LLM calls", f"{len(llm)} ({_counted(str(e.payload.get('purpose')) for e in llm)})"),
        ("re-asks", str(len(reasks))),
        ("repair rounds", str(len(repairs))),
        ("tokens in / out", f"{tokens_in:,} / {tokens_out:,}"),
        ("notional cost (USD)", f"{cost:.4f}"),
        ("wall-clock (s)", f"{wall:.2f}"),
        ("subject run (s)", subject),
        ("memory cap", f"{memory_cap}" + (f" (RLIMIT_AS {memory_mb} MB)" if memory_mb else "")),
        ("provider adapter", inputs.model),
        ("model", inputs.model_id or "none: no model answered"),
        ("run id", inputs.run_id),
    ]
    return "\n".join(
        [APPENDICES[2], "", "| quantity | value |", "|---|---|"]
        + [f"| {name} | {_cell(value)} |" for name, value in rows]
    )


def _appendix_d(inputs: ReportInputs) -> str:
    """Render Appendix D: what this run did not check, and why."""
    rows = list(inputs.not_checked)
    if not rows:
        rows = [NotChecked("nothing", "every check this package supports ran")]
    return "\n".join(
        [APPENDICES[3], "", "| item | reason |", "|---|---|"]
        + [f"| {_cell(row.item)} | {_cell(row.reason)} |" for row in rows]
    )


def uncovered_numbers(
    body: str,
    claims: Sequence[VerifiedClaim],
    *,
    package_version: str | None = None,
) -> list[str]:
    """Return the numeric tokens of the drafted prose that nothing accounts for.

    A token is accounted for when a claim of the report verifies it, or when it is wrapped
    ``⟦unverified: …⟧``. Which tokens are eligible at all is not decided here: it is
    :func:`~quaestor.verifier.tokens.eligible_numbers`, the same function the extraction pre-pass
    and the repair loop's wrapper read, so that this check cannot refuse a report over a number
    the pre-pass never counted as a claim (D-084).

    Args:
        body: Sections 1 to 7 of the rendered report.
        claims: Every post-repair claim of the report.
        package_version: The package's version string, which is excluded by D-015 and which the
            drafter does mention in prose -- "the champion in credit_default 1.0 is a
            linear-in-log-odds scorecard" is the sentence that cost the first live run its report.

    Returns:
        The tokens with nothing behind them, in prose order.
    """
    eligible = eligible_numbers(body, package_version=package_version)
    verified: dict[float, int] = {}
    for claim in claims:
        if claim.status is ClaimStatus.verified:
            verified[claim.value] = verified.get(claim.value, 0) + 1
    for value in wrapped_values(body):
        verified[value] = verified.get(value, 0) + 1
    uncovered: list[str] = []
    for token in eligible.tokens:
        if verified.get(token.value, 0) > 0:
            verified[token.value] -= 1
        else:
            uncovered.append(token.text)
    return uncovered


def render_report(inputs: ReportInputs) -> str:
    """Render the whole report and refuse to return one that breaks a rule.

    Args:
        inputs: Everything the pipeline decided.

    Returns:
        The report as markdown, front matter first.

    Raises:
        ReportSchemaError: The front matter does not validate, an appendix or a grounding figure
            is missing, the headings are not the eleven in order, a double-bracket token is not a
            citation, or -- under ``full_agent`` -- a number in the prose is covered by no
            verified claim and is not wrapped.
    """
    front = front_matter(inputs)
    problems = check_front_matter(front)
    if problems:
        raise ReportSchemaError(
            "the report's front matter does not satisfy docs/REPORT_SCHEMA.md: "
            + "; ".join(problems)
        )
    spec = inputs.package.spec
    parts = [
        _front_matter_text(front),
        "",
        f"# Validation report — `{spec.name}` v{spec.version}",
    ]
    for section in SECTION_ORDER:
        markdown = inputs.sections.get(section, "").strip()
        if section is ReportSection.findings:
            markdown = _findings_section(markdown, inputs)
        markdown = expand_tables(markdown, inputs.store)
        parts += ["", section_heading(section), ""]
        if section is ReportSection.summary:
            parts += [scope_block(inputs), ""]
        parts.append(markdown)
    body = "\n".join(parts)
    report = "\n".join(
        [
            body,
            "",
            _appendix_a(inputs),
            "",
            _appendix_b(inputs, body),
            "",
            _appendix_c(inputs),
            "",
            _appendix_d(inputs),
            "",
        ]
    )
    failures = check_report(
        report,
        inputs.configuration,
        inputs.claims.post_repair,
        package_version=spec.version,
    )
    if failures:
        raise ReportSchemaError(
            "the rendered report does not satisfy docs/REPORT_SCHEMA.md: " + "; ".join(failures)
        )
    return report


def check_report(
    report: str,
    configuration: Configuration,
    claims: Sequence[VerifiedClaim],
    *,
    package_version: str | None = None,
) -> list[str]:
    """Apply to a rendered report the checks ``tests/test_golden_spec.py`` applies to the golden.

    Args:
        report: The whole of ``report.md``.
        configuration: Which configuration wrote it.
        claims: Its post-repair claims.
        package_version: The package's version string, passed on to
            :func:`uncovered_numbers`; omitted, the version is not excluded from the prose, so a
            caller that has the package should always pass it. :func:`render_report` does.

    Returns:
        One message per problem, empty when the report satisfies the schema.
    """
    problems = check_front_matter(front_matter_of(report))
    body = drafted_and_rendered_body(report)
    uncovered = uncovered_numbers(body, claims, package_version=package_version)
    problems += check_structure(report, configuration=configuration, uncovered=uncovered)
    problems += _unwrapped_failures(body, claims)
    for appendix in APPENDICES:
        if appendix not in report:
            problems.append(f"the report has no {appendix!r}")
    return problems


def _unwrapped_failures(body: str, claims: Sequence[VerifiedClaim]) -> list[str]:
    """Check that every claim that did not verify is wrapped in the prose (golden check 9)."""
    wrapped: dict[float, int] = {}
    for value in wrapped_values(body):
        wrapped[value] = wrapped.get(value, 0) + 1
    problems = []
    for claim in claims:
        if claim.status is ClaimStatus.verified:
            continue
        if wrapped.get(claim.value, 0) <= 0:
            problems.append(
                f"claim {claim.id} is {claim.status.value} and its {claim.value:g} is not wrapped "
                f"{UNVERIFIED_OPEN}{claim.value:g}⟧ in the prose"
            )
            continue
        wrapped[claim.value] -= 1
    return problems


def drafted_and_rendered_body(report: str) -> str:
    """Return sections 1 to 7: everything after the front matter and before Appendix A.

    The front matter is deliberately outside it. It is YAML the renderer wrote, and its version
    strings, its timestamp and its two precisions are not claims about the model -- counting them
    as uncovered numbers would make every report fail its own wrapper rule.

    Args:
        report: The whole of ``report.md``.

    Returns:
        The report's body, renderer blocks included.
    """
    after_front = report.split("---\n", 2)[-1]
    return after_front.split(APPENDIX_A_HEADING, 1)[0]


def drafted_body(report: str) -> str:
    """Return sections 1 to 7 with every renderer block removed, which is the drafter's own prose.

    Args:
        report: The whole of ``report.md``.

    Returns:
        The prose no renderer wrote.
    """
    return drafted_prose(drafted_and_rendered_body(report))


def write_report(inputs: ReportInputs, path: Path | str) -> Path:
    """Render the report and write it.

    Args:
        inputs: Everything the pipeline decided.
        path: Where to write ``report.md``; parent directories are created.

    Returns:
        The path written.

    Raises:
        ReportSchemaError: The report does not satisfy ``docs/REPORT_SCHEMA.md``; nothing is
            written.
    """
    text = render_report(inputs)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
