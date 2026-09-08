"""The drafter: one ``structured()`` call per section, and the rule that every number is cited.

Spec section 3.11. The model is given the section's brief, the section's artifacts as compact JSON
(values at four significant figures, each with its ``hash8`` and its logical name), the candidate
findings the checks raised for that section, and the guidance spans the planner retrieved. It is
asked for one thing: ``{"markdown": "..."}``. The rules it is held to are in
:data:`DRAFT_INSTRUCTION` and each of them exists because something downstream depends on it --
one sentence per line because the extractor's pre-pass is line-based (Phase 7), a citation copied
after every number because the matcher resolves it, a ``[[table:...]]`` directive instead of a
retyped table because grounding precision must measure prose and not transcription (D-013).

Nothing here trusts the answer. Every number it writes is extracted, matched and, if it does not
verify, repaired or wrapped. The prompt is where the drafter is *told* the rules; the verifier is
where it is held to them.

``rules_only`` uses this module too, through :func:`template_section`, which writes the same shape
from the same inputs with no model call at all. Its claims are trivially verified because it emits
them itself: it knows which artifact each number came from, so it can hand the matcher the claim
rather than asking a model to reconstruct it from the prose (spec section 3.13).
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..artifacts.store import ArtifactKind
from ..findings import SECTION_FOR_CLASS, Finding, FindingCandidate
from ..llm.base import LLM
from ..llm.structured import structured
from ..trace import TraceWriter
from ..verifier.claim import Claim, ClaimSource, Unit
from ..vocab import ReportSection
from .sections import (
    DEFECT_CLASS_NAMES,
    FOLLOW_UPS_HEADING,
    OPEN_ITEMS_HEADING,
    ArtifactBrief,
    FollowUp,
    SectionBrief,
    written_number,
)

__all__ = [
    "DRAFT_INSTRUCTION",
    "DRAFT_PURPOSE",
    "NO_CANDIDATES",
    "REPAIR_INSTRUCTION",
    "DraftedSection",
    "Drafter",
    "GuidanceSpan",
    "finding_heading",
    "merge_candidates",
    "spans_from_payload",
    "template_section",
]

DRAFT_PURPOSE: Final = "draft"
"""The ``llm_call`` purpose recorded for a section draft, so the study can count them."""

DRAFT_INSTRUCTION: Final = """\
You are drafting one section of a model-validation report on the model package {package} version
{version}. The report follows the structure of the Federal Reserve's model risk management
guidance and never claims compliance with it.

Section: {heading}

What this section must do:
{brief}

Rules, all of them checked after you answer:
- Every number you write is followed immediately by its [[art:...]] citation, copied exactly from
  the JSON below. A number with no citation is counted against this report.
- Write no number that is not in the JSON below. If you want to say something the artifacts do not
  support, say it in words without a number.
- The artifacts below are **this section's selection, not the store**. Never write that a quantity
  is absent, uncomputed, not recomputed, not available or "not carried": another section may hold
  it, and a report that says one section's selection is the whole run contradicts itself. Say what
  the numbers you have show, and where you need one you were not given, write the sentence without
  it.
- One sentence per line. The claim extractor works line by line, so a sentence split over two
  lines is two claims and a paragraph on one line is one.
- For a table artifact, do not retype the cells. Write the directive [[table:<logical_name>]] on a
  line of its own; the renderer expands it, with its caption and its citation, from the store.
- Open the section with a sentence that anchors it to the guidance, carrying one [[reg:...]]
  citation copied from the guidance spans below. Prefer a span of the current guidance, SR26-2;
  cite the superseded SR11-7 only where it says something the revision does not.
- Write markdown. Do not write a level-2 heading: the renderer writes it.
- Do not use the words "compliant" or "certified".
- Call something a finding only if it is in the candidate list at the end of this prompt. The
  findings section reports exactly that list, and a section that calls anything else a finding
  contradicts it.

Artifacts you may cite (values at four significant figures):
{artifacts}

Guidance spans retrieved for this section:
{guidance}

Findings raised for this section:
{candidates}
{extra}
Answer with the section's markdown under the key "markdown"."""
"""The drafter's prompt. Every rule in it is enforced somewhere downstream, or it is not a rule."""

REPAIR_INSTRUCTION: Final = """\
Your previous draft of this section was checked against the artifact store and some of its numbers
did not verify. Here is the draft, and then what is wrong with it.

Previous draft:
{previous}

Problems, one per line, in the form the verifier reported them:
{problems}

Re-draft the whole section under the same rules. For each problem above, either cite the artifact
the number actually comes from, correct the number to what the artifact says, or remove the number
and say it in words. Do not introduce new numbers to explain the old ones."""
"""What a repair round adds to the prompt (spec section 3.11's "cite or remove", made concrete)."""


class DraftedSection(BaseModel):
    """The one thing a drafter is asked for.

    Attributes:
        markdown: The section's prose, without its level-2 heading.
    """

    model_config = ConfigDict(extra="forbid")

    markdown: str = Field(min_length=1)


class GuidanceSpan(BaseModel):
    """One retrieved span of the regulatory corpus, as the drafter is shown it.

    Attributes:
        doc: ``SR26-2`` or ``SR11-7``.
        section_id: The section id a ``[[reg:...]]`` citation names.
        heading: The heading as the document writes it.
        text: The section body.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    doc: str
    section_id: str
    heading: str
    text: str

    @property
    def citation(self) -> str:
        """The ``[[reg:...]]`` citation that resolves to this span."""
        return f"[[reg:{self.doc}:{self.section_id}]]"

    def to_payload(self) -> dict[str, Any]:
        """Return the span as the prompt carries it, body included.

        Returns:
            A plain dict: the citation to copy, the heading, and the text it stands for.
        """
        return {
            "citation": self.citation,
            "heading": self.heading,
            "text": self.text,
        }


def spans_from_payload(payload: Any) -> list[GuidanceSpan]:
    """Read the spans out of a ``guidance.<query_hash>`` artifact's payload.

    Args:
        payload: The decoded JSON artifact written by ``retrieve_guidance``.

    Returns:
        The spans, in retrieval order; empty when the payload holds none.
    """
    if not isinstance(payload, Mapping):
        return []
    spans = payload.get("spans")
    if not isinstance(spans, Sequence):
        return []
    return [
        GuidanceSpan(
            doc=str(span["doc"]),
            section_id=str(span["section_id"]),
            heading=str(span.get("heading", "")),
            text=str(span.get("text", "")),
        )
        for span in spans
        if isinstance(span, Mapping) and "doc" in span and "section_id" in span
    ]


def finding_heading(finding: Finding) -> str:
    """Return the level-3 heading one finding is printed under.

    ``docs/REPORT_SCHEMA.md`` section 3 fixes the form:
    ``### F-NNN · <class> <name> · severity **<severity>**``.

    Args:
        finding: The numbered finding.

    Returns:
        The heading line.
    """
    name = DEFECT_CLASS_NAMES[finding.defect_class]
    return (
        f"### {finding.id} · {finding.defect_class.value} {name} · "
        f"severity **{finding.severity.value}**"
    )


def _artifacts_block(artifacts: Sequence[ArtifactBrief]) -> str:
    """Render the artifact JSON the drafter copies its numbers and citations out of."""
    if not artifacts:
        return "[]  (this section cites no artifact; write it in words)"
    return json.dumps([item.to_payload() for item in artifacts], indent=1, ensure_ascii=True)


def _guidance_block(spans: Sequence[GuidanceSpan]) -> str:
    """Render the guidance spans, each with the citation that resolves to it."""
    if not spans:
        return "(none retrieved; open the section without a [[reg:...]] citation)"
    return json.dumps([span.to_payload() for span in spans], indent=1, ensure_ascii=True)


NO_CANDIDATES: Final = "candidates raised for this section: none -- describe nothing as a finding"
"""What the prompt says when nothing fired, word for word (DECISIONS D-091).

The Phase 8 prompt said "(none: every check that ran on this section's material raised nothing)",
which states the fact and does not state the consequence. On the third live run section 3 read a
1.256% overlap against the wrong bound, concluded it was an exceedance, and wrote that it "is
recorded as a finding" -- while section 6, which had the findings, correctly said none was raised.
Only the drafter can put those two sentences in one report, so the instruction not to belongs
where the drafter reads it, in the words a reader of the prompt cannot mistake.
"""


def _candidates_block(candidates: Sequence[FindingCandidate]) -> str:
    """Render the candidate findings a section is asked to account for, or say there are none."""
    if not candidates:
        return NO_CANDIDATES
    lines = [f"candidates raised for this section: {len(candidates)}"]
    lines += [
        f"- {candidate.defect_class.value} "
        f"({DEFECT_CLASS_NAMES[candidate.defect_class]}, suggested severity "
        f"{candidate.suggested_severity.value}, from {candidate.tool}): {candidate.detail}"
        for candidate in candidates
    ]
    lines.append(
        "Those are the only findings this section may describe. A number that exceeds a bound and "
        "is not in that list is not a finding: report it, say what bound it was read against, and "
        "leave it to the findings section's open items."
    )
    return "\n".join(lines)


def _follow_ups_block(follow_ups: Sequence[FollowUp], section: ReportSection) -> str:
    """Render the executed follow-up steps a section is asked to report.

    The step's own ``why`` is the half that was missing: on the fourth live run the loop asked for
    three sub-population recomputations, each with a stated reason, and the drafter of the section
    whose selector matched their artifacts was shown the twenty-four numbers and none of the three
    questions -- so it answered its brief, which does not ask, and wrote about none of them
    (DECISIONS D-101).

    Section 6 is asked for a different sentence about the same step. It is given only the steps
    whose result is materially worse than the headline, and it writes each as an open item -- a
    request for a developer response -- rather than under a heading of its own (D-102).
    """
    if not follow_ups:
        return ""
    lines = [
        "",
        "Follow-up analyses the bounded planning loop ran, whose artifacts are among those above:",
    ]
    for follow_up in follow_ups:
        lines.append(
            f"- {follow_up.tool}({json.dumps(dict(follow_up.args), sort_keys=True)})"
            f" -- why: {follow_up.why}"
        )
        lines.append(f"  artifacts: {', '.join(follow_up.artifacts)}")
        if follow_up.detail:
            lines.append(f"  materiality: {follow_up.detail}")
    if section is ReportSection.findings:
        lines.append(
            "Each of those is an open item and not a finding: no rule fired on any of them. Write "
            f"one line per step under `{OPEN_ITEMS_HEADING}`, asking the model developer what the "
            "model discriminates on inside that segment, and cite the slice's own value, the "
            "headline it is compared with and the bound the comparison was made against."
        )
    else:
        lines.append(
            f"Report every one of them under the heading `{FOLLOW_UPS_HEADING}`, written exactly "
            "like that on a line of its own and placed after the rest of this section: for each, "
            "what was asked, why it was asked, and what the numbers say, every number carrying its "
            "citation. A step the run paid for and the report does not mention is a question a "
            "reader cannot see was asked."
        )
    return "\n".join(lines) + "\n"


def _findings_block(findings: Sequence[Finding]) -> str:
    """Render the findings section 6 must write about, each with the heading to copy.

    With no finding to write about, the instruction is one sentence and a prohibition. The fourth
    live report's section 6 said no finding was raised and then listed seven reviews it had carried
    out, two of which -- "input data lineage" and "documentation of intended use and known
    limitations" -- were reviews no check performed, on a package whose Appendix D says it has no
    docs directory. The enumeration a reader needs is the renderer's own "Checks that ran and
    raised no candidate" line, built from the run's record, so the drafter is asked not to write a
    second one (DECISIONS D-103).
    """
    if not findings:
        return (
            "\nNo finding was raised. Say so in one sentence and do not describe what was reviewed "
            "instead: the renderer prints the checks that ran and raised no candidate beneath your "
            f"prose. Then write the {OPEN_ITEMS_HEADING!r} subsection your brief describes: a "
            "validation that raised no finding still owes the developer the observations it made.\n"
        )
    lines = ["\nFindings to write about, in this order, each under the heading given:"]
    for finding in findings:
        lines.append(f"\n{finding_heading(finding)}")
        lines.append(f"  class: {finding.defect_class.value}, severity: {finding.severity.value}")
        lines.append(f"  what the check found: {finding.narrative}")
        lines.append(f"  evidence: {', '.join(finding.evidence)}")
    return "\n".join(lines) + "\n"


class Drafter:
    """Writes one section per model call, under the rules of spec section 3.11.

    Attributes:
        llm: The provider. Tests pass a ``FakeLLM``; nothing here calls a live model by itself.
        package: The package name, for the prompt.
        version: The package version, for the prompt.
        trace: The run's trace; each draft is one ``llm_call`` event with purpose ``draft``.
        params: Provider parameters, such as ``model``.
    """

    def __init__(
        self,
        llm: LLM,
        *,
        package: str,
        version: str,
        trace: TraceWriter | None = None,
        **params: Any,
    ) -> None:
        """Configure a drafter for one run.

        Args:
            llm: The provider.
            package: The package name.
            version: The package version.
            trace: The run's trace writer.
            **params: Passed to the provider on every call.
        """
        self.llm = llm
        self.package = package
        self.version = version
        self.trace = trace
        self.params = params

    def prompt(
        self,
        brief: SectionBrief,
        *,
        artifacts: Sequence[ArtifactBrief] = (),
        spans: Sequence[GuidanceSpan] = (),
        candidates: Sequence[FindingCandidate] = (),
        findings: Sequence[Finding] = (),
        follow_ups: Sequence[FollowUp] = (),
        previous: str | None = None,
        problems: Sequence[str] = (),
    ) -> str:
        """Build one section's prompt, repair round included.

        Args:
            brief: The section's brief.
            artifacts: What it may cite.
            spans: The guidance retrieved for it.
            candidates: The candidates raised on its material.
            findings: The findings it must write about; section 6 only.
            follow_ups: The bounded loop's executed steps whose artifacts this section was shown.
            previous: The draft being repaired, or ``None`` on the first round.
            problems: The verifier's sentences for the claims that did not verify.

        Returns:
            The prompt text.
        """
        extra = _follow_ups_block(follow_ups, brief.section)
        if findings or brief.section is ReportSection.findings:
            extra += _findings_block(findings)
        if previous is not None and problems:
            extra += "\n" + REPAIR_INSTRUCTION.format(
                previous=previous, problems="\n".join(f"- {problem}" for problem in problems)
            )
        return DRAFT_INSTRUCTION.format(
            package=self.package,
            version=self.version,
            heading=brief.heading,
            brief=brief.brief,
            artifacts=_artifacts_block(artifacts),
            guidance=_guidance_block(spans),
            candidates=_candidates_block(candidates),
            extra=extra,
        )

    def draft(
        self,
        brief: SectionBrief,
        *,
        artifacts: Sequence[ArtifactBrief] = (),
        spans: Sequence[GuidanceSpan] = (),
        candidates: Sequence[FindingCandidate] = (),
        findings: Sequence[Finding] = (),
        follow_ups: Sequence[FollowUp] = (),
        previous: str | None = None,
        problems: Sequence[str] = (),
    ) -> str:
        """Draft one section and return its markdown.

        Args:
            brief: The section's brief.
            artifacts: What it may cite.
            spans: The guidance retrieved for it.
            candidates: The candidates raised on its material.
            findings: The findings it must write about; section 6 only.
            follow_ups: The bounded loop's executed steps whose artifacts this section was shown.
            previous: The draft being repaired, or ``None`` on the first round.
            problems: The verifier's sentences for the claims that did not verify.

        Returns:
            The section's markdown, without its level-2 heading.

        Raises:
            LLMOutputError: The model did not return a valid ``{"markdown": ...}`` in two
                attempts.
        """
        answer = structured(
            self.llm,
            self.prompt(
                brief,
                artifacts=artifacts,
                spans=spans,
                candidates=candidates,
                findings=findings,
                follow_ups=follow_ups,
                previous=previous,
                problems=problems,
            ),
            DraftedSection,
            trace=self.trace,
            purpose=DRAFT_PURPOSE,
            trace_fields={"section": brief.section.value, "repair": previous is not None},
            **self.params,
        )
        return answer.markdown.strip()


def _sentence(brief: ArtifactBrief) -> str:
    """Render one scalar artifact as one cited sentence of template prose.

    The logical name is written as inline code and the caption is not written at all. A caption is
    prose the template did not compose and cannot be responsible for -- ``change in servicing
    value at -300 bp`` carries a number that no citation follows -- and an uncited number in a
    template's own output would lower a grounding precision that is meant to be trivially 1.0.
    """
    return f"The value of `{brief.name}` is {written_number(brief.value or 0.0)} {brief.citation}."


def template_section(
    brief: SectionBrief,
    *,
    artifacts: Sequence[ArtifactBrief] = (),
    spans: Sequence[GuidanceSpan] = (),
    candidates: Sequence[FindingCandidate] = (),
    findings: Sequence[Finding] = (),
) -> tuple[str, list[Claim]]:
    """Write one section without a model, and the claims it made while writing it.

    This is the ``rules_only`` narrative of spec section 3.13: one cited sentence per scalar the
    section may cite, one table directive per table, and the candidates listed as findings. It
    returns its own claims rather than leaving them to be extracted, which is what "trivially
    verified" means -- the template knows which artifact each number came from, so there is
    nothing for a model to reconstruct and nothing for it to get wrong. The deterministic pre-pass
    still runs over the result, so a number the template wrote and forgot to declare would be
    counted against it exactly as a drafter's would.

    Args:
        brief: The section's brief.
        artifacts: What the section may cite.
        spans: The guidance retrieved for it.
        candidates: The candidates raised on its material.
        findings: The findings section 6 must list.

    Returns:
        The markdown and the claims it carries, in prose order.
    """
    lines: list[str] = []
    claims: list[Claim] = []
    if spans:
        lines.append(
            f"This section follows the model risk management guidance at {spans[0].citation}."
        )
    scalars = [item for item in artifacts if item.kind is ArtifactKind.scalar]
    tables = [item for item in artifacts if item.kind is ArtifactKind.table]
    if brief.section is ReportSection.findings:
        lines.extend(_finding_lines(findings))
    for item in scalars:
        if item.value is None:  # pragma: no cover - a scalar brief always carries its value
            continue
        line = _sentence(item)
        lines.append(line)
        claims.append(
            Claim(
                text=line,
                value=item.value,
                unit=Unit.ratio,
                metric=item.name.split(".")[0],
                citation=item.citation,
                section=brief.section,
                source=ClaimSource.report,
            )
        )
    for item in tables:
        lines.append(f"[[table:{item.name}]]")
    if candidates and brief.section is not ReportSection.findings:
        lines.append(
            "Candidates raised on this section's material: "
            + "; ".join(candidate.defect_class.value for candidate in candidates)
            + " (see the findings section)."
        )
    if not lines:
        lines.append("No artifact of this run bears on this section.")
    return "\n".join(lines), claims


def _finding_lines(findings: Sequence[Finding]) -> list[str]:
    """Render section 6's headings and a template statement of each finding.

    The check's own sentence -- "the challenger scores 0.8240 against the champion's 0.7480" --
    is deliberately **not** copied into the prose. It carries numbers that no citation follows,
    and an uncited number in the ``rules_only`` arm's own output would lower a grounding precision
    that spec section 3.13 says is trivially 1.0. The numbers are in the section anyway, one cited
    sentence per evidence artifact, which is where they belong; the check's account of them stays
    in ``findings.json``.
    """
    if not findings:
        return ["No finding was raised by the checks that ran."]
    lines: list[str] = []
    for finding in findings:
        lines.append(finding_heading(finding))
        lines.append(
            f"**A `{finding.defect_class.value}` finding, raised by `{finding.tool}` at severity "
            f"`{finding.severity.value}`.**"
        )
        lines.append(
            "Its evidence is the artifacts cited in this section; the check's own account of it "
            "is recorded in `findings.json`."
        )
    return lines


def merge_candidates(
    candidates: Iterable[FindingCandidate],
) -> dict[ReportSection, list[FindingCandidate]]:
    """Group candidates by the section whose material they rest on.

    Args:
        candidates: Every candidate the plan raised.

    Returns:
        Section to candidates, in the order they were raised.
    """
    grouped: dict[ReportSection, list[FindingCandidate]] = {}
    for candidate in candidates:
        section = SECTION_FOR_CLASS[candidate.defect_class]
        grouped.setdefault(section, []).append(candidate)
    return grouped
