"""The report's machine-readable structure, and the checks the renderer refuses to write past.

``examples/golden_report/REPORT_SCHEMA.json`` is the Phase 1 specification of a report: a JSON
Schema over the front matter, plus the ``x-quaestor-*`` structural rules that JSON Schema cannot
express over markdown -- the eleven level-2 headings in order, the required ``scope`` renderer
block, the citation forms, and the patterns a report may not contain. The renderer needs all of it
at runtime and ``examples/`` is not shipped inside the wheel, so the file is **copied into the
package** as ``report_schema.json`` and read from there, exactly as the regulatory corpus is; the
two copies are pinned byte-for-byte by ``tests/test_report_schema.py``, so a sanctioned edit to
the golden schema under D-011 that forgot the copy is a failing test rather than a renderer that
enforces last month's rules (DECISIONS D-074).

:func:`check_front_matter` and :func:`check_structure` are the refusals of spec section 3.11 and
of the schema's own ``x-quaestor-refusal-rules``: schema-invalid front matter, a missing Appendix
A, a missing grounding figure, and -- under ``full_agent`` -- a number in the prose that no
verified claim covers and that nothing wrapped.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final

import jsonschema
import yaml

from ..errors import ReportSchemaError
from ..vocab import Configuration

__all__ = [
    "APPENDIX_A_HEADING",
    "FOLLOW_UPS_HEADING",
    "OPEN_ITEMS_HEADING",
    "SCHEMA_FILE",
    "REPORT_SCHEMA",
    "REQUIRED_HEADINGS",
    "check_front_matter",
    "check_structure",
    "front_matter_of",
    "required_renderer_blocks",
]

SCHEMA_FILE: Final = Path(__file__).with_name("report_schema.json")
"""The packaged copy of ``examples/golden_report/REPORT_SCHEMA.json``, read once at import."""

REPORT_SCHEMA: Final[dict[str, Any]] = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
"""``examples/golden_report/REPORT_SCHEMA.json``, shipped so that the renderer carries its rules."""


REQUIRED_HEADINGS: Final[tuple[str, ...]] = tuple(REPORT_SCHEMA["x-quaestor-required-headings"])
"""The eleven level-2 headings, in order; the report may hold no other."""

APPENDIX_A_HEADING: Final = "## Appendix A — Claims"
"""The appendix the renderer refuses to write a report without."""

OPEN_ITEMS_HEADING: Final = "### Open items"
"""The subsection section 6 must carry, findings or none (DECISIONS D-096).

A validation that raised no finding is not a validation that found nothing to say. The third live
run's section 6 was four sentences saying nothing was raised -- while section 2 had just observed
that a coefficient's sign contradicts subject-matter expectation and section 3 that 1.256% of test
rows repeat a training feature vector. Neither is a defect under any rule this project applies, and
both are things a model developer should answer, so the report now has somewhere to put them and
"no findings" cannot quietly mean "no questions".

It is checked here and **not** added to ``REPORT_SCHEMA.json``'s heading list, which is the list of
the eleven level-2 headings and is pinned to the Phase 1 golden report under D-011. The rule is a
level-3 one, it is the renderer that guarantees it -- ``_findings_section`` supplies the heading
when the drafter omits it, exactly as it supplies a finding's heading under D-071 -- and this check
is the assertion that it did.
"""

FOLLOW_UPS_HEADING: Final = "### Follow-up analyses"
"""The subsection a section carries when the bounded loop ran a step on its material (D-101).

The fourth live run's loop spent three of its four steps computing sub-population metrics --
``metrics.test.sub.limit_bal_low.*``, ``.limit_bal_high.*`` and ``.delinq_count_6m_eq_0.*``, one of
which showed test AUC falling from 0.755 to 0.587 on the never-delinquent 6,048 rows of 9,000 --
and the report says nothing about any of them. Section 4's drafter was shown all twenty-four
scalars and wrote about none, which is the correct behaviour of a drafter told to answer its brief:
the brief did not ask, and the step's own ``why`` was never passed on. So the step reaches the
prompt as a question to answer and its answer reaches the report under a heading of its own.

Level 3, like :data:`OPEN_ITEMS_HEADING` and for the same reason: ``REPORT_SCHEMA.json``'s heading
list is the eleven level-2 headings and is pinned to the Phase 1 golden report under D-011.
"""

RENDERER_BLOCK_RE: Final = re.compile(REPORT_SCHEMA["x-quaestor-renderer-block-pattern"])
"""A renderer block: the scope block, or one expanded table."""

ARTIFACT_CITATION_RE: Final = re.compile(REPORT_SCHEMA["x-quaestor-citation-patterns"]["artifact"])
"""A well-formed ``[[art:...]]`` citation."""

REGULATORY_CITATION_RE: Final = re.compile(
    REPORT_SCHEMA["x-quaestor-citation-patterns"]["regulatory"]
)
"""A well-formed ``[[reg:...]]`` citation."""

ANY_TOKEN_RE: Final = re.compile(r"\[\[[^\]]+\]\]")
"""Anything written in double brackets, well-formed or not."""


def required_renderer_blocks() -> list[Mapping[str, Any]]:
    """Return the renderer blocks every report must carry.

    Returns:
        One mapping per required block, each naming where it goes and how it opens and closes.
    """
    return list(REPORT_SCHEMA["x-quaestor-required-renderer-blocks"])


def front_matter_of(report: str) -> dict[str, Any]:
    """Parse a report's YAML front matter.

    Args:
        report: The whole of ``report.md``.

    Returns:
        The front matter as a plain dict.

    Raises:
        ReportSchemaError: The report does not begin with a YAML front-matter block.
    """
    parts = report.split("---\n")
    if len(parts) < 3 or parts[0].strip():
        raise ReportSchemaError(
            "a report begins with a YAML front-matter block delimited by ---; this one does not"
        )
    loaded = yaml.safe_load(parts[1])
    if not isinstance(loaded, dict):
        raise ReportSchemaError("the report's front matter is not a mapping of keys to values")
    return loaded


def check_front_matter(front: Mapping[str, Any]) -> list[str]:
    """Validate the front matter against the schema and against the two refusal rules.

    Args:
        front: The parsed front matter.

    Returns:
        One message per problem, empty when there is none.
    """
    problems: list[str] = []
    validator = jsonschema.Draft202012Validator(REPORT_SCHEMA)
    for error in sorted(validator.iter_errors(dict(front)), key=str):
        where = ".".join(str(part) for part in error.absolute_path) or "<front matter>"
        problems.append(f"front matter {where}: {error.message}")
    for key in ("grounding_precision_pre", "grounding_precision_post"):
        if front.get(key) is None:
            problems.append(
                f"the front matter carries no {key}; a report prints both grounding precision "
                "figures or it is not written"
            )
    return problems


def check_structure(
    report: str,
    *,
    configuration: Configuration,
    uncovered: Sequence[str] = (),
    follow_up_headings: Sequence[str] = (),
) -> list[str]:
    """Check a rendered report's headings, citations, appendices and forbidden patterns.

    Args:
        report: The whole of ``report.md``.
        configuration: Which configuration wrote it; the wrapper rule binds ``full_agent``.
        uncovered: Numeric tokens of the prose that no verified claim covers and that nothing
            wrapped, as the renderer computed them.
        follow_up_headings: The level-2 headings of the sections the bounded loop ran a step for,
            each of which must carry :data:`FOLLOW_UPS_HEADING`. The renderer supplies that
            heading where the drafter omitted it, exactly as it supplies section 6's open-items
            heading, so this is the assertion that it did rather than a rule that can lose a run.

    Returns:
        One message per problem, empty when there is none.
    """
    problems: list[str] = []
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    if headings != list(REQUIRED_HEADINGS):
        problems.append(
            f"the report's level-2 headings are {headings}, not the eleven "
            f"docs/REPORT_SCHEMA.md fixes, in order"
        )
    if APPENDIX_A_HEADING not in report:
        problems.append(
            f"the report has no {APPENDIX_A_HEADING!r}; a report without its claims appendix is "
            "a report whose numbers cannot be audited"
        )
    if OPEN_ITEMS_HEADING not in _findings_section_of(report):
        problems.append(
            f"section 6 has no {OPEN_ITEMS_HEADING!r}; a validation that raised no finding still "
            "records what the developer is asked to answer for"
        )
    for heading in follow_up_headings:
        if FOLLOW_UPS_HEADING not in _section_of(report, heading):
            problems.append(
                f"{heading!r} has no {FOLLOW_UPS_HEADING!r}; the bounded loop ran a step whose "
                "artifacts this section was shown, and a step the run paid for is reported"
            )
    for block in required_renderer_blocks():
        if str(block["begin"]) not in report:
            problems.append(f"the report has no {block['name']} renderer block")
    bad = [
        token
        for token in ANY_TOKEN_RE.findall(report)
        if not (ARTIFACT_CITATION_RE.fullmatch(token) or REGULATORY_CITATION_RE.fullmatch(token))
    ]
    if bad:
        problems.append(f"these double-bracket tokens are not well-formed citations: {bad}")
    problems.extend(_forbidden(report))
    if configuration is Configuration.full_agent and uncovered:
        problems.append(
            f"these numbers in the prose are covered by no verified claim and are not wrapped "
            f"{'⟦unverified: …⟧'}: {list(uncovered)}"
        )
    return problems


def _section_of(report: str, heading: str) -> str:
    """Return one level-2 section's body, from its own heading to the next one.

    Args:
        report: The whole of ``report.md``.
        heading: The level-2 heading that opens it.

    Returns:
        The body, or ``""`` when the heading is not there -- in which case the heading check has
        already reported the real problem.
    """
    headings = list(REQUIRED_HEADINGS)
    if heading not in report or heading not in headings:
        return ""
    after = report.split(heading, 1)[1]
    following = headings[headings.index(heading) + 1 :]
    nxt = next((later for later in following if later in after), None)
    return after.split(nxt, 1)[0] if nxt else after


def _findings_section_of(report: str) -> str:
    """Return section 6, which is where the open-items subsection has to be.

    Args:
        report: The whole of ``report.md``.

    Returns:
        Everything between section 6's heading and section 7's, or ``""`` when section 6 is not
        there -- in which case the heading check has already reported the real problem.
    """
    return _section_of(report, REQUIRED_HEADINGS[5])


SCOPES: Final[Mapping[str, Callable[[str], str]]] = {
    "whole report": lambda report: report,
    "front matter and section 1": lambda report: _front_matter_and_summary(report),
    "Appendix C and Appendix D only": lambda report: _appendices_c_and_d(report),
}
"""How each declared scope is cut out of a rendered report, by the name the schema uses."""


def _forbidden(report: str) -> list[str]:
    """Apply the schema's forbidden patterns, each inside the scope it declares.

    Raises:
        KeyError: The schema declares a scope this module cannot cut out, which is a schema and
            code that have drifted apart rather than a bad report.
    """
    problems: list[str] = []
    for rule in REPORT_SCHEMA["x-quaestor-forbidden-patterns"]:
        scope = str(rule["scope"])
        found = re.findall(str(rule["pattern"]), SCOPES[scope](report), flags=re.I)
        if found:
            problems.append(f"{sorted(set(found))} in {scope}: {rule['why']}")
    return problems


def _front_matter_and_summary(report: str) -> str:
    """Return the front matter and section 1, which is where a self-claim can live.

    The scope of the ``compliant``/``certified`` rule. ``CLAUDE.md``'s constraint is that no
    document of this project claims that *it* or the model it validates is compliant or certified,
    and a claim of that kind is made where the report says what it is: the front matter and the
    summary under it, which carries the scope block. Over the whole report the same words are
    ordinary model-risk English in the mouth of the *subject* -- a live ``plain_llm`` run lost a
    paid cell to four occurrences of "the certified domain", which is the input range a model is
    approved for and was being recommended for *narrowing* (DECISIONS D-187).

    Args:
        report: The whole of ``report.md``.

    Returns:
        Everything from the start of the report to section 2's heading, or the whole report when
        section 2 is not there -- in which case the heading check has already reported the real
        problem and this rule should see everything rather than nothing.
    """
    second = REQUIRED_HEADINGS[1]
    return report.split(second, 1)[0] if second in report else report


def _appendices_c_and_d(report: str) -> str:
    """Return Appendix C and Appendix D, the scope of the citation-leak rule."""
    marker = "## Appendix C"
    return report.split(marker, 1)[1] if marker in report else ""
