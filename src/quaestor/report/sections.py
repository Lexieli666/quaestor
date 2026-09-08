"""The section plan: what each of the seven sections is about, and which artifacts it may cite.

Spec section 3.11 fixes the seven sections and their order; this module says, for each one, the
brief the drafter is given, the guidance query the planner retrieves for it, and the artifacts the
drafter is shown. That last part is the load-bearing one: **a drafter can only cite what it was
given**, because the rule it is held to is "write no number that is not in the JSON", and the JSON
is built here. A section whose selector is too wide invites a report that wanders; one that is too
narrow makes a section that cannot say anything, and the pre-pass will not forgive it either way.

Values reach the drafter at four significant figures (spec section 3.11) with their ``hash8`` and
their logical name, which is exactly what a ``[[art:...]]`` citation is made of, so citing is
copying. A table artifact is shown as a name and a caption and never as rows: the drafter writes
``[[table:<logical_name>]]`` on a line of its own and the renderer expands it (D-013). A JSON
artifact is flattened into its numeric paths, so that ``run.model_summary`` can be cited as
``[[art:843f4548:run.model_summary#coefficients.utilisation.value]]`` without the drafter having
to guess the shape of the payload.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from ..artifacts.store import ArtifactKind, ArtifactStore
from ..findings import DefectClass
from ..vocab import SECTION_ORDER, ReportSection

__all__ = [
    "CALIBRATION_FIRST_RULE",
    "DEFECT_CLASS_NAMES",
    "MAX_JSON_PATHS",
    "SECTION_BRIEFS",
    "SIGNIFICANT_FIGURES",
    "ArtifactBrief",
    "SectionBrief",
    "artifact_briefs",
    "ordered_briefs",
    "brief_for",
    "calibration_before_discrimination",
    "flatten_json",
    "four_significant_figures",
    "written_number",
    "section_heading",
]

SIGNIFICANT_FIGURES: Final = 4
"""Spec section 3.11: the drafter sees values at four significant figures, and writes what it sees.

The tolerance rule of D-069 is what makes this safe: a number written to four significant figures
is held to the precision of four significant figures, so a value the drafter copies out of this
JSON verifies against the artifact it came from, and one it rounds further verifies too.
"""

MAX_JSON_PATHS: Final = 40
"""How many numeric paths of one JSON artifact reach the prompt, longest-lived first.

``run.model_summary`` on a twelve-feature subject has thirty-odd leaves and ``run.metrics`` a
dozen; the cap exists so that a subject with a thousand coefficients cannot turn one section's
prompt into a data dump. When it bites, the artifact says so in its ``truncated`` flag rather than
silently showing a prefix.
"""

CALIBRATION_FIRST_RULE: Final = "rule.calibration_first_event_rate"
"""The artifact holding the event rate below which section 4 puts calibration first (spec 3.11)."""

DEFECT_CLASS_NAMES: Final[Mapping[DefectClass, str]] = {
    DefectClass.L1: "leakage",
    DefectClass.L2: "contamination",
    DefectClass.R1: "regime stability",
    DefectClass.C1: "calibration",
    DefectClass.S1: "population drift",
    DefectClass.M1: "collinearity",
    DefectClass.D1: "data integrity",
    DefectClass.T1: "declared threshold",
    DefectClass.O1: "out-of-sample degradation",
    DefectClass.E1: "effective challenge",
    DefectClass.X1: "scenario analysis",
    DefectClass.R0: "subject run",
}
"""The human name each defect class carries in a finding's heading, as the golden report writes it.

``### F-001 · E1 effective challenge · severity **low**``: the code is what the study scores and
the name is what a reader recognises, and neither is derivable from the other.
"""


def four_significant_figures(value: float) -> float:
    """Return a number rounded to four significant figures, as the drafter is shown it.

    Args:
        value: The artifact value.

    Returns:
        The rounded value. ``0.7480120…`` becomes ``0.748``; ``1500`` stays ``1500``.
    """
    return float(f"{value:.{SIGNIFICANT_FIGURES}g}")


def written_number(value: float) -> str:
    """Render a number the way report prose writes it: no exponent, no trailing zeros.

    ``format(value, "g")`` writes ``1e-05``, whose first numeric token is ``1``: a drafter that
    used it would write one number and claim another. Everything here stays in positional
    notation, which is what a validation report writes anyway.

    Args:
        value: The number to write.

    Returns:
        The number as prose writes it.
    """
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.12f}".rstrip("0")
    return text if not text.endswith(".") else f"{text}0"


def flatten_json(payload: Any, prefix: str = "", limit: int = MAX_JSON_PATHS) -> dict[str, float]:
    """Flatten a JSON artifact into the numeric paths a citation can address.

    The addressing rules are the citation resolver's, not a second set: a mapping is walked by
    key, and a list element is addressed by its ``feature`` or, failing that, by its ``name``
    (D-026). A path that walks to anything but a number is dropped, because a citation to it
    could not be matched.

    Args:
        payload: The decoded JSON artifact.
        prefix: The dotted path walked so far.
        limit: How many paths to return at most.

    Returns:
        Dotted path to value, in payload order, at most ``limit`` entries.
    """
    found: dict[str, float] = {}
    _walk_json(payload, prefix, found, limit)
    return found


def _walk_json(payload: Any, prefix: str, found: dict[str, float], limit: int) -> None:
    """Depth-first walk of a JSON payload, collecting the numeric leaves a citation can name."""
    if len(found) >= limit:
        return
    if isinstance(payload, bool):
        return
    if isinstance(payload, (int, float)):
        if prefix:
            found[prefix] = float(payload)
        return
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            _walk_json(value, f"{prefix}.{key}" if prefix else str(key), found, limit)
        return
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for item in payload:
            label = _list_label(item)
            if label is None:
                continue
            _walk_json(item, f"{prefix}.{label}" if prefix else label, found, limit)


def _list_label(item: Any) -> str | None:
    """Return the segment a list element is addressed by, or ``None`` when it has none."""
    if not isinstance(item, Mapping):
        return None
    for key in ("feature", "name"):
        if key in item:
            return str(item[key])
    return None


class ArtifactBrief(BaseModel):
    """One artifact as the drafter is shown it: enough to cite it, and nothing else.

    Attributes:
        name: The logical name, the second half of every citation.
        hash8: The eight characters a citation quotes, the first half.
        kind: ``scalar``, ``table`` or ``json``.
        value: The scalar value at four significant figures, or ``None``.
        values: For a JSON artifact, its numeric paths at four significant figures.
        summary: The artifact's caption, so the drafter knows what the number is.
        truncated: Whether :data:`MAX_JSON_PATHS` cut the path list.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    hash8: str
    kind: ArtifactKind
    value: float | None = None
    values: dict[str, float] = {}
    summary: str = ""
    truncated: bool = False

    @property
    def citation(self) -> str:
        """The citation that resolves to this artifact, for a scalar."""
        return f"[[art:{self.hash8}:{self.name}]]"

    def path_citation(self, path: str) -> str:
        """Return the citation that resolves to one path of a JSON or table artifact.

        Args:
            path: The ``#`` suffix, without the ``#``.

        Returns:
            The citation text.
        """
        return f"[[art:{self.hash8}:{self.name}#{path}]]"

    def to_payload(self) -> dict[str, Any]:
        """Return the compact JSON object the prompt carries.

        Returns:
            A plain dict with the keys the drafter is told to read: ``name``, ``hash8``,
            ``citation`` and either ``value`` or ``values``.
        """
        payload: dict[str, Any] = {
            "name": self.name,
            "hash8": self.hash8,
            "kind": self.kind.value,
            "summary": self.summary,
        }
        if self.kind is ArtifactKind.scalar:
            payload["value"] = self.value
            payload["citation"] = self.citation
        elif self.kind is ArtifactKind.json:
            payload["values"] = self.values
            payload["citation_form"] = self.path_citation("<path>")
            if self.truncated:
                payload["truncated"] = True
        else:
            payload["directive"] = f"[[table:{self.name}]]"
        return payload


@dataclass(frozen=True)
class SectionBrief:
    """What one section is, what it may cite, and what the drafter is asked to do with it.

    Attributes:
        section: Which of the seven.
        heading: The level-2 heading the renderer writes, from ``REPORT_SCHEMA.json``.
        guidance_query: What the planner retrieves guidance for, so the section can open with a
            ``[[reg:...]]`` citation.
        brief: The instruction the drafter is given, in one paragraph.
        scalars: Logical names, or dotted prefixes ending in ``.``, whose scalars this section
            may cite.
        jsons: Exact names of JSON artifacts whose numeric paths this section may cite.
        tables: Exact names of table artifacts this section may direct the renderer to expand;
            only those present in the store are offered.
    """

    section: ReportSection
    heading: str
    guidance_query: str
    brief: str
    scalars: tuple[str, ...] = ()
    jsons: tuple[str, ...] = ()
    tables: tuple[str, ...] = ()
    alternative_brief: str | None = field(default=None)

    def matches(self, name: str) -> bool:
        """Whether a scalar's logical name is one this section may cite.

        Args:
            name: The logical name.

        Returns:
            ``True`` when the name is listed exactly, or begins with a listed prefix.
        """
        return any(
            name == item or (item.endswith(".") and name.startswith(item)) for item in self.scalars
        )


_SUMMARY_BRIEF = """\
Open with one sentence that says what the model is, what it predicts, and which guidance this
report follows, anchored by a [[reg:...]] citation. Then state how the subject was run and how
large each split is, then the headline result: which developer-declared thresholds the model
passes, each with the value and the bound, and how many findings were raised at which severity.
Do not describe a check that has no artifact in the JSON below."""

_CONCEPTUAL_BRIEF = """\
Assess the design: what the champion is, how many features it uses and when each is known
(the run.features paths carry the counts by timing), which features its own screen removed and
why, the largest coefficients and whether their signs are what the subject matter expects, and
the effective challenge -- the challenger's score against the champion's, and the threshold that
decides whether the difference matters. If a candidate finding below is about the champion's
functional form, say so and point the reader at the findings section."""

_DATA_BRIEF = """\
Assess the data: missingness in each split and the gap between them against its threshold,
population and characteristic stability between the training split and the others against the
declared bound, and each leakage screen -- declared timings, the strongest single feature against
the leakage threshold, the share of test rows that also appear in train, and the name screen."""

_OUTCOMES_DISCRIMINATION_FIRST = """\
Report the outcomes analysis, discrimination before calibration, because the event rate is above
the rule below. Give a metrics-by-split table in prose, one row per metric, every cell carrying
its own citation. Then the train-to-test gap against its threshold, then calibration: the slope,
the intercept, the mean predicted probability against the observed rate and the relative gap
against its tolerance. Place any table directive on a line of its own. Close with the
developer-declared threshold table, one row per rule, with the bound, the value and pass or fail."""

_OUTCOMES_CALIBRATION_FIRST = """\
Report the outcomes analysis, **calibration before discrimination**, because the event rate is
below the rule below: on a rare event, whether the probabilities mean what they say matters more
than how well they rank. Give the calibration slope, the intercept, the mean predicted probability
against the observed rate and the relative gap against its tolerance first; then discrimination as
a metrics-by-split table in prose, one row per metric, every cell carrying its own citation, and
the train-to-test gap against its threshold. Place any table directive on a line of its own. Close
with the developer-declared threshold table, one row per rule, with the bound, the value and pass
or fail."""

_SENSITIVITY_BRIEF = """\
Report sensitivity: multicollinearity among the retained features (the largest variance inflation
factor and the condition number, each against its threshold), stability across the declared
regimes where there is a regime column, and the rate-shock scenarios where the subject is a hazard
model -- the value change at the extreme shocks, whether the curve is monotone, and the convexity
against the direction the package declares. Say plainly which of these do not apply to this model
type; they are listed in Appendix D and must not be described as though they had been run."""

_FINDINGS_BRIEF = """\
Write the findings section. Open with one sentence anchored by a [[reg:...]] citation saying
how findings are ordered and what evidence each carries. Then, for each finding listed below,
copy its heading line exactly as given, on a line of its own, and beneath it write: a bold
one-sentence statement of the
defect, then the numbers that show it -- each with its citation -- then what the validator
concludes and what the developer should do. Do not invent a finding, do not merge two, and do not
change a severity."""

_MONITORING_BRIEF = """\
Recommend ongoing monitoring: which quantities to track, at what frequency, and against which
bound -- citing the same threshold artifacts the checks used rather than inventing new numbers --
and name anything this validation could not cover that monitoring should watch instead."""


SECTION_BRIEFS: Final[Mapping[ReportSection, SectionBrief]] = {
    ReportSection.summary: SectionBrief(
        section=ReportSection.summary,
        heading="## 1. Summary and scope",
        guidance_query="model validation elements scope and purpose",
        brief=_SUMMARY_BRIEF,
        scalars=(
            "profile.train.n",
            "profile.test.n",
            "metrics.",
            "calibration_slope.",
            "psi.max",
            "csi.max",
            "vif.max",
            "condition_number",
            "challenger.delta_auc",
            "threshold.package.",
        ),
    ),
    ReportSection.conceptual_soundness: SectionBrief(
        section=ReportSection.conceptual_soundness,
        heading="## 2. Conceptual soundness",
        guidance_query="evaluation of conceptual soundness model design and variables",
        brief=_CONCEPTUAL_BRIEF,
        scalars=(
            "challenger.",
            "threshold.E1.",
            "metrics.test.auc",
            "metrics.test.brier",
        ),
        jsons=("run.features", "run.model_summary"),
    ),
    ReportSection.data_integrity: SectionBrief(
        section=ReportSection.data_integrity,
        heading="## 3. Data integrity and drift",
        guidance_query="data quality accuracy completeness and representativeness",
        brief=_DATA_BRIEF,
        scalars=(
            "profile.",
            "psi.",
            "csi.",
            "leakage.",
            "threshold.D1.",
            "threshold.L1.",
            "threshold.L2.",
            "threshold.S1.",
            "threshold.package.psi.",
        ),
    ),
    ReportSection.outcomes: SectionBrief(
        section=ReportSection.outcomes,
        heading="## 4. Outcomes analysis",
        guidance_query="outcomes analysis comparing model output to actual outcomes",
        brief=_OUTCOMES_DISCRIMINATION_FIRST,
        alternative_brief=_OUTCOMES_CALIBRATION_FIRST,
        scalars=(
            "metrics.",
            "calibration.",
            "calibration_slope.",
            "calibration_intercept.",
            "deciles.",
            "cpr.",
            "threshold.C1.",
            "threshold.O1.",
            "threshold.package.",
            "rule.",
        ),
        jsons=("run.metrics",),
        tables=("calibration.test", "deciles.test", "cpr.test"),
    ),
    ReportSection.sensitivity: SectionBrief(
        section=ReportSection.sensitivity,
        heading="## 5. Sensitivity and scenario analysis",
        guidance_query="sensitivity analysis stability benchmarking alternative models",
        brief=_SENSITIVITY_BRIEF,
        scalars=(
            "vif.",
            "condition_number",
            "threshold.M1.",
            "threshold.R1.",
            "stability.",
            "scenario.",
        ),
        tables=("stability.auc_by_regime", "scenario.value_by_shock"),
    ),
    ReportSection.findings: SectionBrief(
        section=ReportSection.findings,
        heading="## 6. Findings and recommendations",
        guidance_query="model validation findings deficiencies and remediation",
        brief=_FINDINGS_BRIEF,
    ),
    ReportSection.monitoring: SectionBrief(
        section=ReportSection.monitoring,
        heading="## 7. Ongoing monitoring recommendations",
        guidance_query="ongoing monitoring model performance over time",
        brief=_MONITORING_BRIEF,
        scalars=(
            "threshold.package.",
            "psi.max",
            "metrics.test.auc",
            "calibration_slope.test",
            "rule.",
        ),
    ),
}
"""One brief per section, in report order. Spec section 3.11's list, made into prompts."""


def brief_for(section: ReportSection | str) -> SectionBrief:
    """Return one section's brief.

    Args:
        section: Which section.

    Returns:
        Its brief.
    """
    return SECTION_BRIEFS[ReportSection(section)]


def section_heading(section: ReportSection | str) -> str:
    """Return the level-2 heading of one section, as ``REPORT_SCHEMA.json`` fixes it.

    Args:
        section: Which section.

    Returns:
        The heading line, without a trailing newline.
    """
    return brief_for(section).heading


def calibration_before_discrimination(store: ArtifactStore, split: str = "test") -> bool:
    """Whether section 4 puts calibration first, by spec section 3.11's rare-event rule.

    Args:
        store: The run's artifact store.
        split: Which split's event rate decides it.

    Returns:
        ``True`` when the observed event rate is below ``rule.calibration_first_event_rate``.
        Both artifacts have to be there: with no event rate and no rule there is no decision to
        make, and discrimination first is the ordinary order.
    """
    rate_name = f"metrics.{split}.event_rate"
    if rate_name not in store or CALIBRATION_FIRST_RULE not in store:
        return False
    return store.value(rate_name) < store.value(CALIBRATION_FIRST_RULE)


def artifact_briefs(
    store: ArtifactStore,
    brief: SectionBrief,
    *,
    extra: Iterable[str] = (),
) -> list[ArtifactBrief]:
    """Return the artifacts one section may cite, in logical-name order.

    Args:
        store: The run's artifact store.
        brief: The section's brief.
        extra: Logical names to include whatever the selectors say -- section 6's findings are
            built this way, from the evidence each finding names.

    The scalar selectors select **scalars**: a table matched by one of them is not offered, or a
    section that may cite ``calibration.`` would be handed every calibration table the run
    produced and would print four of them. A section shows the tables its brief names, and only
    those.

    Returns:
        One :class:`ArtifactBrief` per artifact, scalars and JSON artifacts carrying values at
        four significant figures and tables carrying only their name and caption.
    """
    wanted = {
        name
        for name in store.names()
        if brief.matches(name) and store.entry(name).kind is ArtifactKind.scalar
    }
    wanted |= {name for name in brief.jsons if name in store}
    wanted |= {name for name in brief.tables if name in store}
    wanted |= {name for name in extra if name in store}
    briefs = [_artifact_brief(store, name) for name in sorted(wanted)]
    return [item for item in briefs if item is not None]


def _artifact_brief(store: ArtifactStore, name: str) -> ArtifactBrief | None:
    """Build one artifact's brief, or return ``None`` for a kind the drafter cannot cite."""
    entry = store.entry(name)
    hash8 = entry.hash[:8]
    if entry.kind is ArtifactKind.scalar and entry.value is not None:
        return ArtifactBrief(
            name=name,
            hash8=hash8,
            kind=entry.kind,
            value=four_significant_figures(entry.value),
            summary=entry.summary,
        )
    if entry.kind is ArtifactKind.json:
        flat = flatten_json(store.load(name))
        return ArtifactBrief(
            name=name,
            hash8=hash8,
            kind=entry.kind,
            values={path: four_significant_figures(value) for path, value in flat.items()},
            summary=entry.summary,
            truncated=len(flat) >= MAX_JSON_PATHS,
        )
    if entry.kind is ArtifactKind.table:
        return ArtifactBrief(name=name, hash8=hash8, kind=entry.kind, summary=entry.summary)
    return None


def ordered_briefs(store: ArtifactStore) -> list[SectionBrief]:
    """Return the seven briefs in report order, with section 4's order chosen for this run.

    Args:
        store: The run's artifact store, which decides whether calibration comes first.

    Returns:
        The seven briefs.
    """
    calibration_first = calibration_before_discrimination(store)
    briefs = []
    for section in SECTION_ORDER:
        brief = SECTION_BRIEFS[section]
        if (
            section is ReportSection.outcomes
            and calibration_first
            and brief.alternative_brief is not None
        ):
            brief = SectionBrief(**{**brief.__dict__, "brief": brief.alternative_brief})
        briefs.append(brief)
    return briefs
