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

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from ..artifacts.store import ArtifactKind, ArtifactStore
from ..findings import DefectClass
from ..package import PackageSpec, Use
from ..tools.metrics import THRESHOLD_TABLE, metric_artifact_name, subpopulation_expression
from ..tools.thresholds import SLICE_GAP_BOUND, SLICE_SHARE_FLOOR
from ..vocab import SECTION_ORDER, ReportSection
from .schema import FOLLOW_UPS_HEADING, OPEN_ITEMS_HEADING

__all__ = [
    "CALIBRATION_FIRST_RULE",
    "CHALLENGER_DELTA",
    "DEFECT_CLASS_NAMES",
    "FOLLOW_UPS_HEADING",
    "SLICE_GAP_BOUND",
    "SLICE_SHARE_FLOOR",
    "MAX_JSON_PATHS",
    "OPEN_ITEMS_HEADING",
    "SECTION_BRIEFS",
    "SIGNIFICANT_FIGURES",
    "ArtifactBrief",
    "FollowUp",
    "OrderReason",
    "SectionBrief",
    "SectionOrder",
    "artifact_briefs",
    "as_written",
    "ordered_briefs",
    "brief_for",
    "calibration_before_discrimination",
    "flatten_json",
    "four_significant_figures",
    "follow_up_for",
    "monitoring_brief",
    "outcomes_brief",
    "prompt_value",
    "recomputed_for_declared_bounds",
    "section_four_order",
    "sections_for_follow_up",
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


class OrderReason(StrEnum):
    """Why section 4 is ordered the way it is; the report says which one applied (D-098).

    Attributes:
        declared_use: ``package.yaml`` declares ``use: probability`` or ``use: both``, so the
            level of the probability is relied on and calibration leads whatever the event rate is.
        event_rate: No declared use settled it, so the rare-event rule of spec section 3.11 did.
    """

    declared_use = "declared_use"
    event_rate = "event_rate"


@dataclass(frozen=True)
class SectionOrder:
    """How section 4 orders itself, and on which of the two grounds.

    Attributes:
        calibration_first: Whether calibration is reported before discrimination.
        reason: Which rule decided it. ``rule.calibration_first_event_rate`` is cited by the
            report only when this is :attr:`OrderReason.event_rate`, because a number that
            decided nothing is a number a reader is invited to misread.
    """

    calibration_first: bool
    reason: OrderReason


@dataclass(frozen=True)
class FollowUp:
    """One executed step of the bounded loop, as the drafter of a section is shown it.

    Attributes:
        tool: The tool the loop asked for.
        args: The arguments it asked for, as the registry validated them.
        why: The loop's own reason for asking, which is the question the section answers.
        artifacts: The logical names the step produced, in store order.
        tables: Those of them that are table artifacts, which the section points the renderer at
            instead of enumerating their cells (D-115).
        slice_rule: The step's sub-population as an expression over the column, ``delinq_last ==
            0``, which the section writes inside backticks so that the rule's own parameter is not
            read as a claim (D-112). Empty for a step that asked for no slice.
        material: Whether this step's result is materially worse than the headline under
            :data:`SLICE_GAP_BOUND` and large enough under :data:`SLICE_SHARE_FLOOR`, so that it
            belongs in section 6's open items as well as in the section that computed it.
        detail: One clause naming the numbers the materiality decision read and the bounds it read
            them against, or the reason it does not qualify.
    """

    tool: str
    args: Mapping[str, Any] = field(default_factory=dict)
    why: str = ""
    artifacts: tuple[str, ...] = ()
    tables: tuple[str, ...] = ()
    slice_rule: str = ""
    material: bool = False
    detail: str = ""


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


def prompt_value(value: float) -> float:
    """Return the value the drafting prompt carries: exact when integral, four figures otherwise.

    Args:
        value: The artifact value.

    Returns:
        The value the prompt shows. ``10158`` stays ``10158``; ``0.7480120…`` becomes ``0.748``.

    Four significant figures is a rule about *precision*, and a count has none to lose: rounding
    10,158 rows to 10,160 does not simplify a measurement, it states a different number of rows.
    The matcher holds a count to half a unit (spec section 0), so the rounded value cannot verify
    against the artifact it came from, and the drafter is being asked to write a number this
    pipeline will then flag. On the fifth live run that is two of the five failed claims --
    ``metrics.train.sub.limit_bal_low.n`` reached the prompt as 10160 against an artifact of 10158,
    and ``metrics.train.sub.delinq_last_eq_0.n`` as 16210 against 16207 -- and one of the two
    counts left the prose in the repair round rather than being corrected (DECISIONS D-110).
    """
    if float(value).is_integer() and abs(value) < 1e15:
        return value
    return four_significant_figures(value)


def as_written(value: float) -> float | int:
    """Return a value as the drafting prompt should print it: an integer when it is one.

    Args:
        value: The artifact value, already rounded to four significant figures.

    Returns:
        ``int(value)`` when the value is integral and small enough to be exact, the value
        otherwise. ``900`` is a count of rows and ``0`` a count of features; neither is a
        measurement, and a drafter shown ``0.0`` writes "flags 0.0 features" (DECISIONS D-106).
    """
    return int(value) if float(value).is_integer() and abs(value) < 1e15 else value


def written_number(value: float) -> str:
    """Render a number the way report prose writes it: no exponent, no trailing zeros.

    Everything here stays in positional notation, which is what a validation report writes anyway.
    The tokenizer reads ``1e-05`` as one token now (D-099), so exponent notation is no longer a way
    for a template to write one number and claim another; positional notation is still what this
    writes, because ``0.0000192`` is what a reader of a validation report expects to see.

    **The number of decimals is chosen so that the significant figures survive**, which is the
    half this got wrong until D-178. A fixed twelve-decimal format is a precision ceiling, and a
    value below it is not rounded but erased: ``challenger.brier`` of ``3.2265e-13`` on the
    ``msr__L1__eom_balance`` variant formatted to ``0.000000000000``, which this function then
    returned as ``"0.0"`` -- prose asserting that a near-perfect challenger's Brier score is zero,
    of an artifact that says it is not, in the one configuration whose grounding is meant to be
    1.0 by construction. Twelve decimals is still the floor, so every number this wrote before
    D-178 it writes identically; only a value too small for twelve decimals gets more of them.

    Args:
        value: The number to write.

    Returns:
        The number as prose writes it, always carrying at least one significant figure of a
        non-zero value.
    """
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    exponent = math.floor(math.log10(abs(value)))
    decimals = max(_MIN_DECIMALS, SIGNIFICANT_FIGURES - 1 - exponent)
    text = f"{value:.{decimals}f}".rstrip("0")
    if text.endswith("."):  # pragma: no cover - `decimals` keeps a significant figure alive
        raise ValueError(f"{value!r} rounded away to {text!r}; written_number must not erase it")
    return text


_MIN_DECIMALS: Final = 12
"""The decimal floor :func:`written_number` keeps, so that nothing it wrote before D-178 moves."""


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

        An integral value is written as an integer, so that a count of features is shown as ``0``
        and not as ``0.0``: the drafter writes what it is shown, and the third live report read
        "flags 0.0 features". D-094 made the same decision for the renderer's expanded tables and
        left the prompt out, which is the half of the report a reader most often quotes
        (DECISIONS D-106).

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
            payload["value"] = None if self.value is None else as_written(self.value)
            payload["citation"] = self.citation
        elif self.kind is ArtifactKind.json:
            payload["values"] = {path: as_written(value) for path, value in self.values.items()}
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
        tables: Names of table artifacts this section may direct the renderer to expand, or
            dotted prefixes ending in ``.`` for a family whose members one run names -- the
            bounded loop's ``metrics.<split>.sub.<slug>`` tables are one per slice it asked for
            (D-115). Only those present in the store are offered.
    """

    section: ReportSection
    heading: str
    guidance_query: str
    brief: str
    scalars: tuple[str, ...] = ()
    jsons: tuple[str, ...] = ()
    tables: tuple[str, ...] = ()

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

    def wants_table(self, name: str) -> bool:
        """Whether a table's logical name is one this section may direct the renderer to expand.

        Args:
            name: The logical name.

        Returns:
            ``True`` when the name is listed exactly, or begins with a listed prefix.
        """
        return any(
            name == item or (item.endswith(".") and name.startswith(item)) for item in self.tables
        )


_SUMMARY_BRIEF = """\
Open with one sentence that says what the model is, what it predicts, and which guidance this
report follows, anchored by a [[reg:...]] citation. Then state how the subject was run and how
large each split is, then the headline result: which developer-declared thresholds the model
passes, each with the value and the bound.
Close on this validation's findings, taken from the list below and from nothing else. Name each
one -- its id, its class in words, its severity, in the form "F-001, a C1 calibration finding at
medium severity" -- and write **no count of them as a digit**: the renderer prints the count by
severity in the scope table directly above your prose, and a count you wrote yourself would be a
number with no artifact behind it. Where that list is empty, and only then, say in one sentence
that no finding was raised. Never write that none was raised when the list is not empty, and never
describe as a finding anything the list does not name.
Do not describe a check that has no artifact in the JSON below."""

_CONCEPTUAL_BRIEF = """\
Assess the design: what the champion is, how many features it uses and when each is known
(the run.features paths carry the counts by timing), which features its own screen removed and
why, the largest coefficients and whether their signs are what the subject matter expects, and
the effective challenge -- the challenger's score against the champion's, and the threshold that
decides whether the difference matters. If a candidate finding below is about the champion's
functional form, say so and point the reader at the findings section.
Two families of artifact below are evidence for that judgement rather than the subject of any
rule. sign_check.<feature>.coef_sign is the sign of the fitted coefficient, +1 or -1;
sign_check.<feature>.univariate_direction is the sign of that feature's own relationship with the
outcome on train, taken as the sign of its single-feature AUC minus 0.5;
sign_check.<feature>.agrees is 1 when they agree and 0 when they do not; and
sign_check.n_disagreements counts the features where they do not. ablation.<feature>.delta_auc is
the change in test AUC when the champion's functional form is refitted without that feature, so a
negative number means the feature was carrying discrimination. For every coefficient whose sign
disagrees with its univariate direction, say so, and give that feature's ablation delta as the
measure of how much the disagreement matters -- a sign flip on a feature the model barely uses is
a different statement from one on a feature it depends on. No rule fires on either family: do not
describe anything here as a finding."""

_DATA_BRIEF = """\
Assess the data: missingness in each split and the gap between them against its threshold,
population and characteristic stability between the training split and the others against the
declared bound, and each leakage screen -- declared timings, the strongest single feature against
the leakage threshold, the share of test rows that also appear in train, and the name screen.
The contamination screen has two arms and each is read against its own bound. Compare
leakage.overlap.ids with threshold.L2.overlap, and compare leakage.overlap.features with
threshold.L2.overlap.features_effective, which is the bound that rule actually applied: it is the
larger of threshold.L2.overlap and twice leakage.duplicates.train, because two different subjects
writing the same discrete row is coincidence rather than contamination. Cite whichever bound you
compare a number against, and do not compare a feature-vector overlap with the declared
threshold."""

_OUTCOMES_TAIL = """\
Place every table directive on a line of its own.
Close with the developer-declared thresholds, and do **not** assemble that table yourself: write
the directive [[table:thresholds.evaluation]] on a line of its own. The tool computed it -- one
row per bound package.yaml declares, with the metric, the split, the bound, the recomputed value
and the outcome -- so it cannot disagree with what the rest of this report says was computed.
Follow the directive with at most two sentences of your own about what the table shows, and write
no number in them that is not in the JSON below."""

_OUTCOMES_DISCRIMINATION_FIRST = f"""\
Report the outcomes analysis, discrimination before calibration. Say so in the opening, and give
the reason: the observed event rate on the evaluation split is at or above
{CALIBRATION_FIRST_RULE}, the rate below which this report would lead with calibration instead.
Cite both the event rate and that rule for it.
Give a metrics-by-split table in prose, one row per metric, every cell carrying its own citation.
Then the train-to-test gap against its threshold, then calibration: the slope, the intercept, the
mean predicted probability against the observed rate and the relative gap against its tolerance.
{_OUTCOMES_TAIL}"""

_OUTCOMES_CALIBRATION_FIRST_RATE = f"""\
Report the outcomes analysis, **calibration before discrimination**. Say so in the opening, and
give the reason: the observed event rate on the evaluation split is below
{CALIBRATION_FIRST_RULE}, and on a rare event whether the probabilities mean what they say matters
more than how well they rank. Cite both the event rate and that rule for it.
Give the calibration slope, the intercept, the mean predicted probability against the observed
rate and the relative gap against its tolerance first; then discrimination as a metrics-by-split
table in prose, one row per metric, every cell carrying its own citation, and the train-to-test
gap against its threshold.
{_OUTCOMES_TAIL}"""

_OUTCOMES_CALIBRATION_FIRST_USE = f"""\
Report the outcomes analysis, **calibration before discrimination**. Say so in the opening, and
give the reason: package.yaml declares that this model's output is used as a probability and not
only as a ranking, so whether the probabilities mean what they say is the leading question
whatever the event rate is. State that reason in words. Do **not** offer an event rate as the
reason and do not cite {CALIBRATION_FIRST_RULE}: it did not decide this ordering, and it is not
among the artifacts below.
Give the calibration slope, the intercept, the mean predicted probability against the observed
rate and the relative gap against its tolerance first; then discrimination as a metrics-by-split
table in prose, one row per metric, every cell carrying its own citation, and the train-to-test
gap against its threshold.
{_OUTCOMES_TAIL}"""

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
change a severity.
Where no finding is listed below, say so in one sentence and stop there. Do **not** describe what
was reviewed, list the reviews that were carried out, or say that any review produced no defect:
the renderer prints the checks that ran and raised no candidate directly beneath your prose, from
the run's own record, and a drafted list of reviews beside it is a second account of the same fact
that nothing checked -- the fourth live report's own list named "input data lineage" and
"documentation of intended use and known limitations" on a package whose Appendix D says it has no
docs directory.
Then close the section with the heading `### Open items`, written exactly like that on a line of
its own, and under it the observations this validation made that are **not** defects under any
rule but that a developer should still answer for. The open items are the ones listed for you at
the end of this prompt and no others: one per line, in the order given, each carrying the citation
of the artifact it rests on and each naming an owner -- write "model developer" unless the item
names someone else. Do not compose an open item of your own and do not leave one of them out.
Write each as a question and not as a verdict -- conditioning on one feature also conditions on
everything correlated with it, so a segment selected on a delinquency count is also a segment of
near-constant delinquency history, and what a developer is being asked is what the model
discriminates on inside that segment rather than to accept that the model is defective there.
Cite the observation's own value, what it is compared with and the bound the comparison was made
against.
Where no open item is listed for you, write one sentence under the heading saying there is none.
Never write the word finding about an open item."""

_MONITORING_BRIEF = """\
Recommend ongoing monitoring: which quantities to track, at what frequency, and against which
bound -- citing the same threshold artifacts the checks used rather than inventing new numbers --
and name anything this validation could not cover that monitoring should watch instead."""

_MONITORING_ORDERING: Final[Mapping[SectionOrder, str]] = {
    SectionOrder(True, OrderReason.declared_use): (
        "Section 4 of this report reported **calibration before discrimination**, because "
        "package.yaml declares that this model's output is used as a probability and not only as "
        "a ranking. Where you recommend how a monitoring report should order its own evidence, "
        "say what this report did, and do not offer an event rate as the reason it did it."
    ),
    SectionOrder(True, OrderReason.event_rate): (
        "Section 4 of this report reported **calibration before discrimination**, because the "
        f"observed event rate on the evaluation split is below {CALIBRATION_FIRST_RULE}. Where "
        "you recommend how a monitoring report should order its own evidence, you may say that "
        "this report did the same."
    ),
    SectionOrder(False, OrderReason.declared_use): (
        "Section 4 of this report reported **discrimination before calibration**. Do not write "
        "that this report led with calibration."
    ),
    SectionOrder(False, OrderReason.event_rate): (
        "Section 4 of this report reported **discrimination before calibration**, because the "
        f"observed event rate on the evaluation split is at or above {CALIBRATION_FIRST_RULE}. "
        "You may recommend that a monitoring report lead with calibration for a future cohort "
        "whose rate falls below that bound, but do **not** write that this report led with "
        "calibration: it did not."
    ),
}
CHALLENGER_DELTA: Final = "challenger.delta_auc"
"""The artifact that says a challenger was compared with the champion, which section 2 reports."""

_MONITORING_CHALLENGER: Final = (
    "A challenger model was compared with the champion in this validation and section 2 reports "
    "the comparison, so do not write that benchmarking against an alternative model was not part "
    "of it. What monitoring adds is a comparison the development data cannot give: a benchmark "
    "against an external or vendor reference, or against the challenger refitted on production "
    "vintages. Say which of those you mean."
)
"""What section 7 is told when the run compared a challenger (DECISIONS D-114).

The fifth live report's section 7 wrote that "benchmarking against an alternative internal or
vendor model, or against retail credit bureau data, was not part of this validation" three pages
after section 2 reported the challenger's AUC against the champion's. The sentence is the kind
D-100 forbids -- a section calling a quantity absent because its own selection does not carry it
-- and the fix is the same shape: put the fact in the brief rather than the prohibition in the
prompt, because a drafter told only not to say it has nothing true to say instead.
"""

"""What section 7 is told about section 4's ordering, by what decided it (DECISIONS D-104).

The fourth live report's section 7 recommended that a monitoring report "order calibration
evidence ahead of discrimination evidence, as this report does" -- of a report whose section 4 led
with discrimination, on the rule's own arithmetic and in its own opening sentence. Section 4's
ordering was decided in :func:`ordered_briefs` and told to nobody else, so section 7 was asked to
describe a decision it could not see and described the one the rule it *had* been shown suggests.
"""


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
            "runtime.",
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
            "sign_check.",
            "ablation.",
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
        # Only a `--data` run holds this one, and it is the one place in the report where the
        # digest check the loader already performed becomes something the prose can cite (D-162).
        tables=("data.manifest",),
    ),
    ReportSection.outcomes: SectionBrief(
        section=ReportSection.outcomes,
        heading="## 4. Outcomes analysis",
        guidance_query="outcomes analysis comparing model output to actual outcomes",
        brief=_OUTCOMES_DISCRIMINATION_FIRST,
        scalars=(
            "metrics.",
            "calibration.",
            "calibration_slope.",
            "calibration_intercept.",
            "deciles.",
            "cpr.",
            "psi.",
            "threshold.",
            "rule.",
        ),
        jsons=("run.metrics",),
        tables=(
            "thresholds.evaluation",
            "calibration.test",
            "deciles.test",
            "cpr.test",
            "metrics.",
        ),
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


def section_four_order(
    store: ArtifactStore,
    spec: PackageSpec | None = None,
    split: str = "test",
) -> SectionOrder:
    """Decide whether section 4 leads with calibration, and on which ground (DECISIONS D-098).

    Two rules, applied in this order:

    * a declared ``use`` of ``probability`` or ``both`` puts calibration first whatever the event
      rate is, because the level of the probability is what the model is used for;
    * otherwise the rare-event rule of spec section 3.11 decides -- calibration first when the
      observed event rate is below ``rule.calibration_first_event_rate``.

    The reason is returned as well as the answer, because the report states which one applied and
    cites ``rule.calibration_first_event_rate`` only when it was the one that did.

    Args:
        store: The run's artifact store.
        spec: The package, or ``None`` where the caller has only a store; with no spec there is no
            declared use and the event-rate rule decides.
        split: Which split's event rate decides it.

    Returns:
        The ordering and the ground for it.
    """
    if spec is not None and spec.use in (Use.probability, Use.both):
        return SectionOrder(calibration_first=True, reason=OrderReason.declared_use)
    rate_name = f"metrics.{split}.event_rate"
    if rate_name not in store or CALIBRATION_FIRST_RULE not in store:
        # With no event rate and no rule there is no decision to make, and discrimination first
        # is the ordinary order; the ground is still the rule, which is what did not fire.
        return SectionOrder(calibration_first=False, reason=OrderReason.event_rate)
    below = store.value(rate_name) < store.value(CALIBRATION_FIRST_RULE)
    return SectionOrder(calibration_first=below, reason=OrderReason.event_rate)


def calibration_before_discrimination(
    store: ArtifactStore,
    spec: PackageSpec | None = None,
    split: str = "test",
) -> bool:
    """Whether section 4 puts calibration first.

    Args:
        store: The run's artifact store.
        spec: The package, for its declared ``use``.
        split: Which split's event rate decides it.

    Returns:
        ``True`` when calibration leads.
    """
    return section_four_order(store, spec, split).calibration_first


_OUTCOMES_BRIEFS: Final[Mapping[SectionOrder, str]] = {
    SectionOrder(True, OrderReason.declared_use): _OUTCOMES_CALIBRATION_FIRST_USE,
    SectionOrder(True, OrderReason.event_rate): _OUTCOMES_CALIBRATION_FIRST_RATE,
    SectionOrder(False, OrderReason.declared_use): _OUTCOMES_DISCRIMINATION_FIRST,
    SectionOrder(False, OrderReason.event_rate): _OUTCOMES_DISCRIMINATION_FIRST,
}
"""Which brief section 4 is given, by what decided its order. Discrimination first is one text:
a declared ``use`` never puts discrimination first, so the only ground it can rest on is the rate.
"""


def outcomes_brief(brief: SectionBrief, order: SectionOrder) -> SectionBrief:
    """Return section 4's brief for one run's ordering, with the selector it justifies.

    Where the declared use decided the order, ``rule.`` leaves the selector: the drafter is asked
    not to cite ``rule.calibration_first_event_rate`` as the reason, and the surest way to be
    obeyed is not to hand it the number (D-098).

    Args:
        brief: Section 4's brief as declared.
        order: What decided its order.

    Returns:
        The brief this run's section 4 is drafted from.
    """
    fields = dict(brief.__dict__)
    fields["brief"] = _OUTCOMES_BRIEFS[order]
    if order.reason is OrderReason.declared_use:
        fields["scalars"] = tuple(name for name in brief.scalars if name != "rule.")
    return SectionBrief(**fields)


def recomputed_for_declared_bounds(store: ArtifactStore, brief: SectionBrief) -> set[str]:
    """Return the recomputed values that answer the declared bounds this section is shown.

    A section shown ``threshold.package.brier.test.max`` is shown ``metrics.test.brier``, and it
    is derived rather than listed: ``thresholds.evaluation`` already holds one row per bound
    ``package.yaml`` declares, with the metric and the split it is stated on (D-092), and
    :func:`~quaestor.tools.metrics.metric_artifact_name` already says which artifact answers a
    metric on a split. Hand-listing the pair for each section is how section 7 came to be shown a
    Brier ceiling with no Brier value, and to write that "no recomputed test Brier value is
    carried in this report's artifact store" while three other sections cited it (D-100).

    Args:
        store: The run's artifact store.
        brief: The section's brief, whose selectors decide which bounds it is shown.

    Returns:
        The logical names of the recomputed scalars, empty when the run computed no threshold
        table or when this section is shown no declared bound.
    """
    if THRESHOLD_TABLE not in store:
        return set()
    rows = store.load(THRESHOLD_TABLE)
    if not isinstance(rows, Sequence):  # pragma: no cover - a table payload is always a row list
        return set()
    found: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):  # pragma: no cover - as above
            continue
        metric, split = str(row.get("metric", "")), str(row.get("split") or "")
        stem = f"threshold.package.{metric}{f'.{split}' if split else ''}"
        if not (brief.matches(f"{stem}.min") or brief.matches(f"{stem}.max")):
            continue
        name = metric_artifact_name(metric, split or None)
        if name is not None and name in store and store.entry(name).kind is ArtifactKind.scalar:
            found.add(name)
    return found


SLICE_GAP_SUFFIX: Final = ".auc_gap"
"""The tail of the artifact that says how far a sub-population fell below its split (D-102)."""

SLICE_SHARE_SUFFIX: Final = ".share"
"""The tail of the artifact that says how much of the split a sub-population holds (D-102)."""


def follow_up_for(
    store: ArtifactStore,
    tool: str,
    args: Mapping[str, Any],
    why: str,
    artifacts: Sequence[str],
) -> FollowUp:
    """Describe one executed step of the bounded loop, and say where its result belongs.

    A step that produced a sub-population AUC gap is read against :data:`SLICE_GAP_BOUND` and
    :data:`SLICE_SHARE_FLOOR`, both of which the tool stored: a gap over the bound on a slice at or
    above the floor is an open item in section 6, and anything else is supporting evidence in the
    section that computed it. A step that produced no such pair is never material -- there is no
    rule here for a re-profiled feature, and inventing one would be a rule with no bound to cite
    (DECISIONS D-102).

    Args:
        store: The run's artifact store, which holds the gap, the share and the two bounds.
        tool: The tool the loop asked for.
        args: The arguments it asked for.
        why: The loop's own stated reason.
        artifacts: The logical names the step produced.

    Returns:
        The follow-up, with :attr:`FollowUp.material` and :attr:`FollowUp.detail` filled in.
    """
    names = tuple(artifacts)
    tables = tuple(
        name for name in names if name in store and store.entry(name).kind is ArtifactKind.table
    )
    rule = _slice_rule(args)
    if SLICE_GAP_BOUND not in store or SLICE_SHARE_FLOOR not in store:
        return FollowUp(
            tool=tool, args=dict(args), why=why, artifacts=names, tables=tables, slice_rule=rule
        )
    bound, floor = store.value(SLICE_GAP_BOUND), store.value(SLICE_SHARE_FLOOR)
    reasons: list[str] = []
    material = False
    for gap_name in [name for name in names if name.endswith(SLICE_GAP_SUFFIX)]:
        stem = gap_name[: -len(SLICE_GAP_SUFFIX)]
        share_name = f"{stem}{SLICE_SHARE_SUFFIX}"
        if share_name not in store:  # pragma: no cover - the tool stores the pair together
            continue
        gap, share = store.value(gap_name), store.value(share_name)
        if share < floor:
            reasons.append(
                f"{stem} holds {share:.4g} of the split, below {SLICE_SHARE_FLOOR} at "
                f"{floor:.4g}, so it cannot raise an open item however large its gap"
            )
        elif gap > bound:
            material = True
            reasons.append(
                f"{stem} falls {gap:.4g} below the split's own AUC, above {SLICE_GAP_BOUND} at "
                f"{bound:.4g}, on {share:.4g} of the split -- materially worse than the headline, "
                "so it belongs in section 6's open items as a question for the model developer as "
                "well as here"
            )
        else:
            reasons.append(
                f"{stem} falls {gap:.4g} below the split's own AUC, within {SLICE_GAP_BOUND} at "
                f"{bound:.4g}, so it is supporting evidence for this section and not an open item"
            )
    return FollowUp(
        tool=tool,
        args=dict(args),
        why=why,
        artifacts=names,
        tables=tables,
        slice_rule=rule,
        material=material,
        detail="; ".join(reasons),
    )


def _slice_rule(args: Mapping[str, Any]) -> str:
    """Return a step's sub-population as an expression, or empty where it asked for no slice."""
    slice_ = args.get("subpopulation")
    if not isinstance(slice_, Mapping):
        return ""
    column, rule = slice_.get("column"), slice_.get("rule")
    if not isinstance(column, str) or not isinstance(rule, str):  # pragma: no cover - validated
        return ""
    return subpopulation_expression(column, rule)


def sections_for_follow_up(
    briefs: Sequence[SectionBrief], follow_up: FollowUp
) -> list[ReportSection]:
    """Return the sections asked to report one follow-up step.

    A section is asked when its own selector matched at least one of the step's artifacts, which
    is the same rule that decides whether it was shown them: a section cannot report a number it
    may not cite. **The summary is never one of them.** Section 1 states the headline result and
    the findings count, so it is derivative by construction, and an analysis reported there before
    it has been reported anywhere is a headline with no body. Section 6 is not one either -- a
    material step reaches it as an open item, which is a different sentence with a different point
    (DECISIONS D-101).

    Args:
        briefs: The seven briefs, in report order.
        follow_up: The executed step.

    Returns:
        The sections, in report order.
    """
    return [
        brief.section
        for brief in briefs
        if brief.section not in (ReportSection.summary, ReportSection.findings)
        and any(brief.matches(name) for name in follow_up.artifacts)
    ]


def monitoring_brief(
    brief: SectionBrief, order: SectionOrder, store: ArtifactStore | None = None
) -> SectionBrief:
    """Return section 7's brief for one run's section-4 ordering and effective challenge.

    Args:
        brief: Section 7's brief as declared.
        order: What section 4 did, and on which ground (D-104).
        store: The run's artifact store, so that a run which compared a challenger says so and
            section 7 cannot write that benchmarking was not part of it (D-114). With no store
            the paragraph is left out, which is what a caller holding only an ordering asserts.

    Returns:
        The brief this run's section 7 is drafted from: the declared paragraph with one more
        sentence saying what section 4 did, and one more about the challenger where there was one.
        They are appended rather than substituted into a placeholder so that the declared brief is
        a brief a drafter could be sent as it stands.
    """
    fields = dict(brief.__dict__)
    text = f"{brief.brief}\n{_MONITORING_ORDERING[order]}"
    if store is not None and CHALLENGER_DELTA in store:
        text = f"{text}\n{_MONITORING_CHALLENGER}"
    fields["brief"] = text
    return SectionBrief(**fields)


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
    produced and would print four of them. A section shows the tables its own ``tables`` list
    names, exactly or by a prefix ending in ``.``, and only those.

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
    wanted |= {
        name
        for name in store.names()
        if store.entry(name).kind is ArtifactKind.table and brief.wants_table(name)
    }
    wanted |= {name for name in extra if name in store}
    wanted |= recomputed_for_declared_bounds(store, brief)
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
            value=prompt_value(entry.value),
            summary=entry.summary,
        )
    if entry.kind is ArtifactKind.json:
        flat = flatten_json(store.load(name))
        return ArtifactBrief(
            name=name,
            hash8=hash8,
            kind=entry.kind,
            values={path: prompt_value(value) for path, value in flat.items()},
            summary=entry.summary,
            truncated=len(flat) >= MAX_JSON_PATHS,
        )
    if entry.kind is ArtifactKind.table:
        return ArtifactBrief(name=name, hash8=hash8, kind=entry.kind, summary=entry.summary)
    return None


def ordered_briefs(store: ArtifactStore, spec: PackageSpec | None = None) -> list[SectionBrief]:
    """Return the seven briefs in report order, with section 4's order chosen for this run.

    Args:
        store: The run's artifact store, which carries the event rate and the rule.
        spec: The package, whose declared ``use`` outranks the event rate (D-098).

    Returns:
        The seven briefs.
    """
    order = section_four_order(store, spec)
    briefs = []
    for section in SECTION_ORDER:
        brief = SECTION_BRIEFS[section]
        if section is ReportSection.outcomes:
            brief = outcomes_brief(brief, order)
        elif section is ReportSection.monitoring:
            brief = monitoring_brief(brief, order, store)
        briefs.append(brief)
    return briefs
