"""Defect classes, severities and the candidate a check raises before a validator sees it.

Spec section 3.9 fixes the twelve defect codes and the four severities; the study scores detection
against those codes, so they are not extensible without changing what the published numbers mean.

Phase 2 shipped the half of this module that needs no artifact store: :class:`DefectClass`,
:class:`Severity` and :class:`FindingCandidate`. Phase 7 adds :class:`Finding`, whose validation
is "every evidence hash exists in the store", and :class:`FindingsDocument`, the ``findings.json``
envelope ``examples/golden_report/FINDINGS_SCHEMA.json`` describes.

A candidate is what a check produces; a finding is what a validator publishes. The agent may
re-severitise a candidate or merge candidates of one class, and may not invent a finding that no
candidate supports. Those three verbs are the whole of :meth:`Finding.from_candidates`, the only
public way to make a finding: it takes candidates of one class, unions their evidence, records how
many it merged, and demands a one-sentence reason whenever the severity it publishes differs from
the one the check suggested.

:func:`open_items` is the other half of what section 6 reports, and the half that is not a defect:
the observations a validator should ask a developer about that no rule calls a finding. It is a
rule rather than a brief's examples for the reason :meth:`Finding.from_candidates` is one -- the
list a report is asked for and the list a study scores against have to be the same list -- and it
lives here because an open item is a sibling of a finding and this is the module both readers can
import (DECISIONS D-173).

The store reaches the validator through pydantic's validation **context**, not through a field: a
finding is a persisted object and the store is not part of it. Reading a persisted document back
passes ``store=None`` on purpose -- ``eval/score.py`` scores a run from ``findings.json`` alone,
often on a machine whose artifact store is long gone, and the evidence rule was enforced when the
finding was made (DECISIONS D-061).
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationInfo,
    field_validator,
    model_validator,
)

from .artifacts import SHORT_HASH_LENGTH, ArtifactStore
from .errors import ArtifactError
from .trace import EventType, TraceWriter
from .vocab import Configuration, ReportSection

__all__ = [
    "FINDING_ID_RE",
    "OPEN_ITEM_OWNER",
    "PRE_RUN_TOOL",
    "SCHEMA_VERSION",
    "SECTION_FOR_CLASS",
    "STORE_CONTEXT_KEY",
    "CandidateNotPromoted",
    "DefectClass",
    "Finding",
    "FindingCandidate",
    "FindingsDocument",
    "OpenItem",
    "OpenItemKind",
    "Severity",
    "open_items",
    "severity_rank",
]

PRE_RUN_TOOL: Final = "load_package"
"""The ``tool`` value of a candidate raised by reading ``package.yaml``, before anything runs.

The evidence rule -- a candidate names at least one artifact hash -- cannot apply to a candidate
raised by the loader, because no tool has run and so no artifact exists. Naming the loader is what
makes that exemption checkable rather than a hole: exactly one ``tool`` value may carry empty
evidence, and it is not a value any tool has (DECISIONS D-021).
"""


class DefectClass(StrEnum):
    """The twelve defect codes of spec section 3.7, fixed because the study scores against them.

    Attributes:
        L1: A feature is declared ``after_outcome``, or a single feature scores AUC > 0.90.
        L2: Train/test row overlap above the contamination threshold.
        R1: A top feature flips sign across regimes, or AUC differs materially across them.
        C1: Calibration slope outside its band, or mean predicted far from observed.
        S1: Population or score drift (PSI) above threshold.
        M1: Multicollinearity: VIF or condition number above threshold.
        D1: Data integrity: missingness differs materially between splits.
        T1: A developer-declared threshold or claim is breached.
        O1: Out-of-sample degradation: a train-to-test or holdout AUC gap above threshold.
        E1: Effective challenge: a challenger beats the champion by more than the threshold.
        X1: Scenario analysis: a non-monotone or wrong-signed value curve.
        R0: The subject run failed or breached its runtime caps.
    """

    L1 = "L1"
    L2 = "L2"
    R1 = "R1"
    C1 = "C1"
    S1 = "S1"
    M1 = "M1"
    D1 = "D1"
    T1 = "T1"
    O1 = "O1"
    E1 = "E1"
    X1 = "X1"
    R0 = "R0"


class Severity(StrEnum):
    """How serious a finding is, in the order a report lists them.

    Attributes:
        high: The model should not be used as it stands.
        medium: A material weakness with a required remediation.
        low: A weakness worth documenting; the model remains usable.
        info: An observation with no remediation attached.
    """

    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


_SEVERITY_ORDER: Final = {
    Severity.high: 0,
    Severity.medium: 1,
    Severity.low: 2,
    Severity.info: 3,
}
"""Report order, most serious first. Not the enum's definition order by accident: it is asserted."""


def severity_rank(severity: Severity) -> int:
    """Return the sort key that puts the most serious finding first.

    Args:
        severity: The severity to rank.

    Returns:
        ``0`` for ``high`` through ``3`` for ``info``.
    """
    return _SEVERITY_ORDER[severity]


class FindingCandidate(BaseModel):
    """A defect a check believes it has seen, with the artifacts that show it.

    Every candidate carries at least one artifact hash, because a finding requires evidence and a
    candidate is the only thing a finding may be promoted from. The single exception is a
    **pre-run** candidate: ``timing: after_outcome`` on a feature is an ``L1`` defect that is
    visible in ``package.yaml`` before any tool has run, so there is no artifact to point at yet.
    Such a candidate declares ``tool = PRE_RUN_TOOL`` and only then may leave ``evidence`` empty;
    the check that promotes it in Phase 7 attaches the ``leakage.timing`` artifact first.

    Attributes:
        defect_class: Which of the twelve codes this is.
        evidence: Artifact hashes, non-empty unless this is a pre-run candidate.
        detail: One sentence naming what was seen and the threshold it crossed.
        suggested_severity: What the check proposes; the agent may raise or lower it with a
            traced one-sentence reason.
        tool: The tool that raised it, or :data:`PRE_RUN_TOOL` for a candidate from the loader.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    defect_class: DefectClass
    evidence: list[str] = Field(default_factory=list)
    detail: str
    suggested_severity: Severity
    tool: str

    @model_validator(mode="after")
    def _evidence_unless_pre_run(self) -> FindingCandidate:
        """Reject an empty evidence list on anything but a pre-run candidate."""
        if not self.evidence and self.tool != PRE_RUN_TOOL:
            raise ValueError(
                f"a {self.defect_class} candidate from {self.tool!r} has no evidence; only a "
                f"pre-run candidate (tool={PRE_RUN_TOOL!r}) may name no artifact"
            )
        return self

    @property
    def is_pre_run(self) -> bool:
        """Whether this candidate was raised by the loader, before any tool ran."""
        return self.tool == PRE_RUN_TOOL


SCHEMA_VERSION: Final = 1
"""Stamped on ``findings.json``, as on every file Quaestor persists."""

STORE_CONTEXT_KEY: Final = "store"
"""The pydantic validation-context key a :class:`Finding` reads its artifact store from.

``Finding.model_validate(payload, context={STORE_CONTEXT_KEY: store})`` checks the evidence rule.
``context={STORE_CONTEXT_KEY: None}`` says "this document was written by a run that checked it,
and I am reading it back without that run's store", which is what the study's scorer does. No
context at all is refused: the rule may be waived deliberately, never by forgetting it.
"""

FINDING_ID_RE: Final = re.compile(r"^F-[0-9]{3}$")
"""``F-001``: severity-ordered numbering, assigned by :class:`FindingsDocument` at render time."""

UNNUMBERED_ID: Final = "F-000"
"""The id a finding carries until a document numbers it; outside the range the renderer assigns."""

_EVIDENCE_RE: Final = re.compile(rf"^[0-9a-f]{{{SHORT_HASH_LENGTH}}}$")
"""Evidence is stored as the eight hex characters a citation quotes (FINDINGS_SCHEMA.json)."""

SECTION_FOR_CLASS: Final[Mapping[DefectClass, ReportSection]] = {
    DefectClass.R0: ReportSection.summary,
    DefectClass.E1: ReportSection.conceptual_soundness,
    DefectClass.L1: ReportSection.data_integrity,
    DefectClass.L2: ReportSection.data_integrity,
    DefectClass.D1: ReportSection.data_integrity,
    DefectClass.S1: ReportSection.data_integrity,
    DefectClass.C1: ReportSection.outcomes,
    DefectClass.O1: ReportSection.outcomes,
    DefectClass.T1: ReportSection.outcomes,
    DefectClass.M1: ReportSection.sensitivity,
    DefectClass.R1: ReportSection.sensitivity,
    DefectClass.X1: ReportSection.sensitivity,
}
"""Which section's material each defect class rests on, when the caller does not say.

``section`` on a finding is not "where the finding is printed" -- every finding is printed under
section 6 -- but which section's evidence it is about, so that the report can point a reader from
the finding back to the analysis that raised it. The mapping is the report's own structure:
leakage, contamination, drift and integrity are data questions, calibration and generalisation are
outcomes questions, collinearity, regime stability and scenarios are sensitivity questions, and
effective challenge is a question about the champion's design.
"""


class Finding(BaseModel):
    """A defect the validator publishes, with the artifacts that prove it.

    Built through :meth:`from_candidates`; validated against an artifact store passed in the
    pydantic validation context under :data:`STORE_CONTEXT_KEY`. ``CLAUDE.md``'s rule -- "a
    ``Finding`` object cannot be constructed without at least one artifact hash that exists in the
    store" -- is enforced in both halves: ``evidence`` is non-empty by the field constraint, and
    every hash in it is looked up in the store by the model validator.

    Attributes:
        id: ``F-NNN``, assigned by :class:`FindingsDocument` in severity order.
        defect_class: One of the twelve codes.
        severity: The severity the validator published.
        suggested_severity: What the check proposed; equal to ``severity`` unless it was changed.
        severity_reason: The one-sentence reason, required exactly when the two differ.
        tool: The tool whose candidate or candidates became this finding.
        title: One line, drafted or templated.
        narrative: The prose; every number in it is also a claim in section 6.
        evidence: The eight-character hashes of the artifacts that show the defect, non-empty.
        section: Which section's material the finding rests on.
        candidates_merged: How many candidates of this class were merged into it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = UNNUMBERED_ID
    defect_class: DefectClass
    severity: Severity
    suggested_severity: Severity
    severity_reason: str | None = None
    tool: str
    title: str = Field(min_length=1)
    narrative: str = Field(min_length=1)
    evidence: list[str] = Field(min_length=1)
    section: ReportSection
    candidates_merged: int = Field(default=1, ge=1)

    _evidence_checked: bool = PrivateAttr(default=False)
    """Whether the evidence rule has already been applied to this object.

    A pydantic ``mode="after"`` validator runs again whenever the instance is placed inside
    another model -- putting a finding into a :class:`FindingsDocument` re-runs it, with no
    validation context, which would fail every document ever built. The rule is applied once, when
    the object is made, and the flag records that it was; ``model_copy`` carries it, so a
    renumbered finding is not re-checked either (DECISIONS D-061).
    """

    @field_validator("evidence")
    @classmethod
    def _evidence_is_short_hashes(cls, evidence: list[str]) -> list[str]:
        """Reject anything that is not the eight hex characters a citation quotes."""
        bad = [item for item in evidence if not _EVIDENCE_RE.match(item)]
        if bad:
            raise ValueError(
                f"evidence {bad} is not written as the {SHORT_HASH_LENGTH} hex characters a "
                "citation quotes; pass Finding.short(hash) or the artifact's short_hash"
            )
        return evidence

    @model_validator(mode="after")
    def _reason_required_when_severity_changed(self) -> Finding:
        """Refuse a changed severity with no reason, and a reason with no change."""
        changed = self.severity is not self.suggested_severity
        if changed and not (self.severity_reason or "").strip():
            raise ValueError(
                f"finding {self.id} publishes severity {self.severity} where the check suggested "
                f"{self.suggested_severity}; a severity change needs a one-sentence reason, which "
                "is what the report prints and the trace records"
            )
        if not changed and self.severity_reason is not None:
            raise ValueError(
                f"finding {self.id} carries a severity_reason but did not change the check's "
                f"suggested severity ({self.severity}); a reason with no change reads as a change"
            )
        return self

    @model_validator(mode="after")
    def _evidence_is_in_the_store(self, info: ValidationInfo) -> Finding:
        """Check every evidence hash against the store in the validation context."""
        if self._evidence_checked:
            return self
        context = info.context
        if not isinstance(context, Mapping) or STORE_CONTEXT_KEY not in context:
            raise ValueError(
                f"a Finding is validated against an artifact store: pass "
                f"context={{{STORE_CONTEXT_KEY!r}: store}} to model_validate, or "
                f"context={{{STORE_CONTEXT_KEY!r}: None}} to read a document back without one"
            )
        store = context[STORE_CONTEXT_KEY]
        if store is None:
            self._evidence_checked = True
            return self
        if not isinstance(store, ArtifactStore):
            raise ValueError(
                f"the {STORE_CONTEXT_KEY!r} in the validation context is a "
                f"{type(store).__name__}, not an ArtifactStore"
            )
        for item in self.evidence:
            try:
                store.get(item)
            except ArtifactError as exc:
                raise ValueError(
                    f"finding {self.id} ({self.defect_class}) names evidence {item}, which is not "
                    f"in the store at {store.root}: {exc.message}"
                ) from exc
        self._evidence_checked = True
        return self

    @staticmethod
    def short(artifact_hash: str) -> str:
        """Return the eight characters of a hash that a citation and an evidence list carry.

        Args:
            artifact_hash: A full artifact hash, or one already shortened.

        Returns:
            Its first eight characters.
        """
        return artifact_hash[:SHORT_HASH_LENGTH]

    @classmethod
    def from_candidates(
        cls,
        candidates: Sequence[FindingCandidate],
        *,
        store: ArtifactStore,
        severity: Severity | None = None,
        severity_reason: str | None = None,
        title: str | None = None,
        narrative: str | None = None,
        section: ReportSection | None = None,
        finding_id: str = UNNUMBERED_ID,
        trace: TraceWriter | None = None,
    ) -> Finding:
        """Promote one or more candidates of a single defect class to a finding.

        Args:
            candidates: The candidates, all of one :class:`DefectClass`, at least one. Their
                evidence is unioned and ``candidates_merged`` records how many there were.
            store: The run's artifact store; every evidence hash is looked up in it.
            severity: The severity to publish. Defaults to the highest severity the candidates
                suggested; anything else needs ``severity_reason``.
            severity_reason: The one sentence that justifies a changed severity.
            title: The finding's one-line title; defaults to the first candidate's ``detail``.
            narrative: The prose; defaults to the candidates' details, one per line. Phase 8's
                drafter replaces both, and ``rules_only`` keeps them.
            section: Which section's material this rests on; defaults to
                :data:`SECTION_FOR_CLASS`.
            finding_id: The id, when the caller already knows it. A document renumbers anyway.
            trace: The run's trace. One ``finding`` event is written per promotion, carrying the
                severity the check suggested, the severity published and whether they differ.

        Returns:
            The finding.

        Raises:
            ValueError: No candidates, candidates of more than one class, a severity change with
                no reason, or an evidence hash the store does not hold. The message names the
                hash, the class or the severities, whichever failed.
        """
        merged = list(candidates)
        if not merged:
            raise ValueError(
                "a Finding is promoted from at least one FindingCandidate; the LLM writes "
                "narrative and does not mint findings"
            )
        classes = {candidate.defect_class for candidate in merged}
        if len(classes) > 1:
            raise ValueError(
                f"candidates of {sorted(classes)} cannot be merged into one finding; only "
                "candidates of a single defect class may be"
            )
        tools = sorted({candidate.tool for candidate in merged})
        evidence = sorted({cls.short(item) for c in merged for item in c.evidence})
        if not evidence:
            raise ValueError(
                f"the {classes.pop()} candidates from {tools} name no artifact between them; a "
                "pre-run candidate must have its evidence attached before it is promoted "
                f"(tool={PRE_RUN_TOOL!r})"
            )
        suggested = min((c.suggested_severity for c in merged), key=severity_rank)
        published = severity if severity is not None else suggested
        defect_class = merged[0].defect_class
        details = [candidate.detail for candidate in merged]
        finding = cls.model_validate(
            {
                "id": finding_id,
                "defect_class": defect_class,
                "severity": published,
                "suggested_severity": suggested,
                "severity_reason": severity_reason,
                "tool": tools[0] if len(tools) == 1 else "+".join(tools),
                "title": title if title is not None else details[0],
                "narrative": narrative if narrative is not None else "\n".join(details),
                "evidence": evidence,
                "section": section or SECTION_FOR_CLASS[defect_class],
                "candidates_merged": len(merged),
            },
            context={STORE_CONTEXT_KEY: store},
        )
        if trace is not None:
            trace.emit(
                EventType.finding,
                finding_id=finding.id,
                defect_class=finding.defect_class.value,
                severity=finding.severity.value,
                suggested_severity=finding.suggested_severity.value,
                severity_changed=finding.severity is not finding.suggested_severity,
                severity_reason=finding.severity_reason,
                tool=finding.tool,
                evidence=finding.evidence,
                section=finding.section.value,
                candidates_merged=finding.candidates_merged,
            )
        return finding

    def numbered(self, number: int) -> Finding:
        """Return a copy of this finding carrying ``F-NNN``.

        Args:
            number: The 1-based position in severity order.

        Returns:
            The renumbered copy.
        """
        return self.model_copy(update={"id": f"F-{number:03d}"})


OPEN_ITEM_OWNER: Final = "model developer"
"""Who a minted open item asks for an answer, unless the artifacts name someone else (D-096)."""

_SLICE_SEGMENT: Final = ".sub."
"""What marks a sub-population's artifact stem, as ``compute_metrics`` writes it (D-102)."""

_SLICE_GAP_SUFFIX: Final = ".auc_gap"
"""The tail of the artifact that says how far a sub-population fell below its split."""

_SLICE_SHARE_SUFFIX: Final = ".share"
"""The tail of the artifact that says how much of the split a sub-population holds."""

_SIGN_PREFIX: Final = "sign_check."
"""The family ``check_collinearity`` stores a fitted sign against its univariate direction under."""

_AGREES_SUFFIX: Final = ".agrees"
"""The tail of the artifact that is 1 when the two signs agree and 0 when they do not (D-095)."""

_FEATURE_OVERLAP: Final = "leakage.overlap.features"
"""The share of test rows whose feature vector also appears in train (D-086)."""

_TRAIN_DUPLICATES: Final = "leakage.duplicates.train"
"""The within-train duplicate share, which is what raises the feature-overlap bound (D-086)."""


class OpenItemKind(StrEnum):
    """Which rule minted an open item, in the order :func:`open_items` returns them.

    Attributes:
        slice_gap: A sub-population materially worse than its split's headline, large enough to
            be worth answering for (D-102).
        sign_disagreement: A fitted coefficient whose sign contradicts the feature's own
            univariate direction (D-095).
        feature_overlap: A feature-vector overlap between the splits that the within-train
            duplicate share explains, so no ``L2`` candidate was raised (D-086).
    """

    slice_gap = "slice_gap"
    sign_disagreement = "sign_disagreement"
    feature_overlap = "feature_overlap"


class OpenItem(BaseModel):
    """One observation a developer should answer for that no rule calls a defect.

    A sibling of :class:`Finding`, and deliberately not one: D-096 refuses to promote an open item
    to an ``info``-severity finding, because that would put it in ``findings.json``, in the
    severity counts and in the study's precision denominator, so a helpful observation would score
    as a false alarm. It is minted by :func:`open_items` from artifacts that are already in the
    store, so every number in it is citable and none of it was invented by a model.

    Attributes:
        kind: Which rule minted it.
        subject: What it is about -- a sub-population's artifact stem, a feature name, or the
            pair of splits the overlap was measured between.
        artifacts: The logical names section 6 may cite for it, the observed quantities first and
            the bound last, deduplicated and in that order.
        bound: The logical name of the artifact the observation was read against. A threshold for
            two of the three kinds; for a sign disagreement it is the univariate direction, which
            is the thing the fitted sign was compared with and is an artifact like any other.
        detail: The sentence-sized facts section 6 needs, with every number written as the store
            holds it.
        owner: Who is asked to answer, :data:`OPEN_ITEM_OWNER` unless the artifacts name someone
            else.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: OpenItemKind
    subject: str = Field(min_length=1)
    artifacts: list[str] = Field(min_length=1)
    bound: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    owner: str = OPEN_ITEM_OWNER


def _figure(value: float) -> str:
    """Render one number for an open item's prose at the four figures the drafter is shown."""
    return f"{value:.4g}"


def _bound_value(store: ArtifactStore, thresholds: Mapping[str, float], name: str) -> float | None:
    """Return the value of a bound that is citable, or ``None`` when it is not.

    The resolved thresholds are the authority for a bound the run *decided*; a derived bound such
    as ``threshold.L2.overlap.features_effective`` is not among them and is read from the store,
    which is the only place it exists. Either way the bound must be **in the store**, because an
    open item names the bound it was read against and a comparison against an unstored number is
    a comparison nothing can check (D-091).

    Args:
        store: The run's artifact store.
        thresholds: The resolved thresholds, keyed by logical artifact name.
        name: The bound's logical name.

    Returns:
        The value, or ``None`` when the store does not hold the bound.
    """
    if name not in store:
        return None
    declared = thresholds.get(name)
    return float(declared) if declared is not None else store.value(name)


def _slice_items(store: ArtifactStore, thresholds: Mapping[str, float]) -> list[OpenItem]:
    """Mint one open item per sub-population materially worse than its split and large enough."""
    from .tools.thresholds import SLICE_GAP_BOUND, SLICE_SHARE_FLOOR

    bound = _bound_value(store, thresholds, SLICE_GAP_BOUND)
    floor = _bound_value(store, thresholds, SLICE_SHARE_FLOOR)
    if bound is None or floor is None:
        return []
    items: list[OpenItem] = []
    for gap_name in store.names():
        if _SLICE_SEGMENT not in gap_name or not gap_name.endswith(_SLICE_GAP_SUFFIX):
            continue
        stem = gap_name[: -len(_SLICE_GAP_SUFFIX)]
        share_name = f"{stem}{_SLICE_SHARE_SUFFIX}"
        if share_name not in store:  # pragma: no cover - the tool stores the pair together
            continue
        gap, share = store.value(gap_name), store.value(share_name)
        if share < floor or gap <= bound:
            continue
        head, _, _slug = stem.partition(_SLICE_SEGMENT)
        split = head.removeprefix("metrics.")
        headline = f"{head}.auc"
        names = [gap_name, share_name, f"{stem}.auc", headline, SLICE_GAP_BOUND, SLICE_SHARE_FLOOR]
        items.append(
            OpenItem(
                kind=OpenItemKind.slice_gap,
                subject=stem,
                artifacts=[name for name in dict.fromkeys(names) if name in store],
                bound=SLICE_GAP_BOUND,
                detail=(
                    f"on the {split} split this sub-population's AUC falls {_figure(gap)} below "
                    f"the split's own, past {SLICE_GAP_BOUND} at {_figure(bound)}, on "
                    f"{_figure(share)} of the split, which is at or above {SLICE_SHARE_FLOOR} at "
                    f"{_figure(floor)}"
                ),
            )
        )
    return sorted(items, key=lambda item: item.subject)


def _sign_items(store: ArtifactStore) -> list[OpenItem]:
    """Mint one open item per retained feature whose fitted sign contradicts its direction."""
    items: list[OpenItem] = []
    for agrees_name in store.names():
        if not (agrees_name.startswith(_SIGN_PREFIX) and agrees_name.endswith(_AGREES_SUFFIX)):
            continue
        if store.value(agrees_name) != 0.0:
            continue
        feature = agrees_name[len(_SIGN_PREFIX) : -len(_AGREES_SUFFIX)]
        coef = f"{_SIGN_PREFIX}{feature}.coef_sign"
        direction = f"{_SIGN_PREFIX}{feature}.univariate_direction"
        if coef not in store or direction not in store:  # pragma: no cover - stored as a triple
            continue
        items.append(
            OpenItem(
                kind=OpenItemKind.sign_disagreement,
                subject=feature,
                artifacts=[agrees_name, coef, direction],
                bound=direction,
                detail=(
                    f"the fitted coefficient on `{feature}` carries sign "
                    f"{_figure(store.value(coef))} where that feature's own univariate direction "
                    f"is {_figure(store.value(direction))}, so the model conditions on it against "
                    "the direction it shows on its own"
                ),
            )
        )
    return sorted(items, key=lambda item: item.subject)


def _overlap_item(store: ArtifactStore, thresholds: Mapping[str, float]) -> list[OpenItem]:
    """Mint the open item for a feature-vector overlap the within-train duplicates explain."""
    from .tools.leakage import FEATURE_OVERLAP_BOUND, OVERLAP_THRESHOLD

    declared = _bound_value(store, thresholds, OVERLAP_THRESHOLD)
    effective = _bound_value(store, thresholds, FEATURE_OVERLAP_BOUND)
    if declared is None or effective is None or _FEATURE_OVERLAP not in store:
        return []
    overlap = store.value(_FEATURE_OVERLAP)
    if not declared < overlap <= effective:
        return []
    names = [_FEATURE_OVERLAP, _TRAIN_DUPLICATES, OVERLAP_THRESHOLD, FEATURE_OVERLAP_BOUND]
    return [
        OpenItem(
            kind=OpenItemKind.feature_overlap,
            subject=_FEATURE_OVERLAP,
            artifacts=[name for name in names if name in store],
            bound=FEATURE_OVERLAP_BOUND,
            detail=(
                f"{_figure(overlap)} of the held-out rows repeat a feature vector of the training "
                f"split, above {OVERLAP_THRESHOLD} at {_figure(declared)} but within "
                f"{FEATURE_OVERLAP_BOUND} at {_figure(effective)}, the bound the within-train "
                "duplicate share raised, so no contamination candidate was raised and the "
                "repetition is unexplained rather than innocent"
            ),
        )
    ]


def open_items(store: ArtifactStore, thresholds: Mapping[str, float]) -> list[OpenItem]:
    """Mint section 6's open items by rule from what a run already stored.

    D-096 put ``### Open items`` at the end of section 6 and named two examples in the drafter's
    brief; a brief's examples are not a rule, and the committed real-MSR run shows the gap --
    its three open items are the three sub-populations, and the three coefficients whose fitted
    sign contradicts their univariate direction, which is one of D-096's own two examples, are not
    among them. This function is the rule, and it has one home: the report drafter is handed what
    it returns and ``eval/score.py`` imports the same function rather than re-deriving it, so the
    list a report was asked for and the list a study scores against cannot come apart (D-173).

    Three families, and no fourth. Each reads quantities a tool already stored against a bound
    that tool already stored, so nothing here computes a number the store does not hold:

    * a sub-population whose AUC gap exceeds ``threshold.O1.slice_auc_gap`` on a share at or above
      ``threshold.O1.slice_min_share`` (D-102);
    * a retained feature whose ``sign_check.<feature>.agrees`` is 0 (D-095);
    * a feature-vector overlap above ``threshold.L2.overlap`` but within
      ``threshold.L2.overlap.features_effective``, which is the case D-086 declines to call
      contamination (D-086).

    The two threshold modules are imported inside the functions that need them rather than at the
    top of this one: ``quaestor.tools`` imports this module for :class:`FindingCandidate`, so a
    module-level import here is a cycle. The names are still read from the modules that own their
    spelling, which is what the import is for.

    Args:
        store: The run's artifact store, which holds every quantity and every bound read here.
        thresholds: The resolved thresholds, keyed by logical artifact name -- ``Thresholds.values``
            for a run, and the defaults for a store read back off disk. A derived bound is not
            among them and is read from the store.

    Returns:
        The open items: the sub-populations first, by artifact stem, then the sign disagreements by
        feature, then the feature overlap. The order is fixed so that a scorer comparing two runs
        compares like with like.
    """
    return [
        *_slice_items(store, thresholds),
        *_sign_items(store),
        *_overlap_item(store, thresholds),
    ]


class CandidateNotPromoted(BaseModel):
    """A candidate the validator judged not to warrant a finding, with its reason.

    ``findings.json`` carries these beside the findings so that the study's miss list can say what
    a report did *instead* of raising the seeded class, from structured data rather than from
    prose (D-012).

    Attributes:
        defect_class: The class the check raised.
        tool: The tool that raised it.
        evidence: The eight-character hashes it named, non-empty.
        reason: Why it was not promoted.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    defect_class: DefectClass
    tool: str
    evidence: list[str] = Field(min_length=1)
    reason: str = Field(min_length=1)

    @classmethod
    def of(cls, candidate: FindingCandidate, reason: str) -> CandidateNotPromoted:
        """Record one candidate as not promoted.

        Args:
            candidate: The candidate. Its evidence is shortened to citation length.
            reason: The one sentence that says why.

        Returns:
            The record.
        """
        return cls(
            defect_class=candidate.defect_class,
            tool=candidate.tool,
            evidence=sorted({Finding.short(item) for item in candidate.evidence}),
            reason=reason,
        )


class FindingsDocument(BaseModel):
    """``findings.json``: the findings, what was not promoted, and what raised nothing.

    The envelope is exactly ``examples/golden_report/FINDINGS_SCHEMA.json``. Findings are
    severity-ordered and numbered ``F-001..`` by :meth:`build`, which is the only place the order
    and the numbering are decided, so the ids in the prose, in Appendix A and in this file cannot
    disagree.

    Attributes:
        schema_version: Always :data:`SCHEMA_VERSION`.
        package: The package name.
        version: The package version.
        configuration: Which of the three configurations ran.
        run_id: Joins this file to ``trace.jsonl`` and to the report's front matter.
        illustrative: ``true`` only in ``examples/golden_report/``.
        findings: Severity-ordered.
        candidates_not_promoted: Candidates the validator declined, with reasons.
        checks_without_candidates: Tool name to the defect classes it screened for and did not
            raise.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = SCHEMA_VERSION
    package: str
    version: str
    configuration: Configuration
    run_id: str
    illustrative: bool = False
    findings: list[Finding] = Field(default_factory=list)
    candidates_not_promoted: list[CandidateNotPromoted] = Field(default_factory=list)
    checks_without_candidates: dict[str, list[DefectClass]] = Field(default_factory=dict)

    @classmethod
    def build(
        cls,
        *,
        package: str,
        version: str,
        configuration: Configuration,
        run_id: str,
        findings: Iterable[Finding],
        candidates_not_promoted: Iterable[CandidateNotPromoted] = (),
        checks_without_candidates: Mapping[str, Iterable[DefectClass]] | None = None,
        illustrative: bool = False,
    ) -> FindingsDocument:
        """Severity-order the findings, number them ``F-001..`` and build the document.

        Args:
            package: The package name.
            version: The package version.
            configuration: Which configuration ran.
            run_id: The run identifier.
            findings: The findings in any order; ties inside one severity keep the order given,
                which is the order the tools ran in.
            candidates_not_promoted: The declined candidates.
            checks_without_candidates: Tool name to the classes it screened for and did not raise.
            illustrative: ``true`` only for the golden report.

        Returns:
            The document, ready to write.
        """
        ordered = sorted(findings, key=lambda finding: severity_rank(finding.severity))
        return cls(
            package=package,
            version=version,
            configuration=configuration,
            run_id=run_id,
            illustrative=illustrative,
            findings=[finding.numbered(number) for number, finding in enumerate(ordered, start=1)],
            candidates_not_promoted=list(candidates_not_promoted),
            checks_without_candidates={
                tool: list(classes) for tool, classes in (checks_without_candidates or {}).items()
            },
        )

    def by_severity(self, severity: Severity) -> list[Finding]:
        """Return the findings of one severity, in document order.

        Args:
            severity: The severity to filter on.

        Returns:
            The findings.
        """
        return [finding for finding in self.findings if finding.severity is severity]

    def counts_by_severity(self) -> dict[str, int]:
        """Return ``{high, medium, low, info}`` counts, for the report's front matter.

        Returns:
            One entry per severity, in report order, zeros included.
        """
        return {
            severity.value: len(self.by_severity(severity))
            for severity in sorted(Severity, key=severity_rank)
        }

    def to_payload(self) -> dict[str, Any]:
        """Return the document as the JSON object ``FINDINGS_SCHEMA.json`` validates.

        Returns:
            A plain dict, with the enums as their string values.
        """
        return self.model_dump(mode="json")

    def write(self, path: Path | str) -> Path:
        """Write ``findings.json``.

        Args:
            path: The file to write; parent directories are created.

        Returns:
            The path written.
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_payload(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
        return target

    @classmethod
    def read(cls, path: Path | str, *, store: ArtifactStore | None = None) -> FindingsDocument:
        """Read a ``findings.json`` back.

        Args:
            path: The file to read.
            store: The run's artifact store, when it is at hand and the evidence rule should be
                re-checked. ``None`` -- the default -- reads the document without it, which is
                what ``eval/score.py`` does on a machine that has the file and not the run.

        Returns:
            The document.
        """
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(payload, context={STORE_CONTEXT_KEY: store})
