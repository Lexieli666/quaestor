"""Defect classes, severities and the candidate a check raises before a validator sees it.

Spec section 3.9 fixes the twelve defect codes and the four severities; the study scores detection
against those codes, so they are not extensible without changing what the published numbers mean.

Phase 2 ships the half of this module that needs no artifact store: :class:`DefectClass`,
:class:`Severity` and :class:`FindingCandidate`. :class:`~quaestor.findings.Finding` itself arrives
in Phase 7, because its validation is "every evidence hash exists in the store" and there is
nothing to promote a candidate from until the tools of Phase 5 have run.

A candidate is what a check produces; a finding is what a validator publishes. The agent may
re-severitise a candidate or merge candidates of one class, and may not invent a finding that no
candidate supports.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["PRE_RUN_TOOL", "DefectClass", "FindingCandidate", "Severity"]

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
