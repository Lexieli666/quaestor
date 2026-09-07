"""The vocabulary the study is scored in, and the one rule that keeps a finding honest.

`CLAUDE.md`: "A finding requires evidence." Phase 2 ships the candidate half of that rule, with the
single exemption the spec's own design forces -- an `after_outcome` feature is an `L1` defect that
is visible before any tool has run, so there is no artifact to name yet. Making the exemption a
named tool value rather than a flag is what keeps it from becoming a hole.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from quaestor.findings import (
    PRE_RUN_TOOL,
    DefectClass,
    FindingCandidate,
    Severity,
    severity_rank,
)


def test_the_twelve_defect_codes_are_exactly_the_spec_list() -> None:
    # Spec section 3.7 fixes these; the study's precision and recall are reported per class, so a
    # thirteenth code, or a renamed one, changes what a published number means.
    assert [member.value for member in DefectClass] == [
        "L1",
        "L2",
        "R1",
        "C1",
        "S1",
        "M1",
        "D1",
        "T1",
        "O1",
        "E1",
        "X1",
        "R0",
    ]


def test_the_four_severities_are_exactly_the_spec_list() -> None:
    assert [member.value for member in Severity] == ["high", "medium", "low", "info"]


def test_severity_rank_orders_most_serious_first() -> None:
    ordered = sorted(Severity, key=severity_rank)
    assert ordered == [Severity.high, Severity.medium, Severity.low, Severity.info]


def test_a_candidate_carries_its_evidence() -> None:
    candidate = FindingCandidate(
        defect_class=DefectClass.E1,
        evidence=["02d4d1a8f0e10b2c"],
        detail="the challenger beats the champion by 0.0323 AUC",
        suggested_severity=Severity.low,
        tool="challenger_compare",
    )
    assert candidate.evidence == ["02d4d1a8f0e10b2c"]
    assert not candidate.is_pre_run


def test_a_candidate_from_a_tool_may_not_have_empty_evidence() -> None:
    with pytest.raises(ValidationError, match="has no evidence"):
        FindingCandidate(
            defect_class=DefectClass.S1,
            evidence=[],
            detail="PSI is high",
            suggested_severity=Severity.medium,
            tool="profile_data",
        )


def test_only_a_pre_run_candidate_may_have_empty_evidence() -> None:
    candidate = FindingCandidate(
        defect_class=DefectClass.L1,
        evidence=[],
        detail="feature 'collections_flag' is declared timing: after_outcome",
        suggested_severity=Severity.high,
        tool=PRE_RUN_TOOL,
    )
    assert candidate.is_pre_run


def test_a_candidate_is_frozen_and_closed() -> None:
    with pytest.raises(ValidationError):
        FindingCandidate(
            defect_class=DefectClass.M1,
            evidence=["abc"],
            detail="VIF",
            suggested_severity=Severity.low,
            tool="check_collinearity",
            confidence=0.9,
        )


def test_an_unknown_defect_class_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FindingCandidate(
            defect_class="Z9",
            evidence=["abc"],
            detail="something",
            suggested_severity=Severity.low,
            tool="check_leakage",
        )
