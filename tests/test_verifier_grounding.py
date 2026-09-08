"""Phase 7: grounding precision, including the two properties that keep it honest."""

from __future__ import annotations

from quaestor.verifier import (
    ClaimSource,
    ClaimStatus,
    VerifiedClaim,
    grounding,
    precision_of,
)
from quaestor.vocab import ReportSection


def claim(
    section: ReportSection, status: ClaimStatus, value: float = 0.7, **kwargs: object
) -> VerifiedClaim:
    """One verified claim of a given section and status."""
    return VerifiedClaim(
        text=f"{section.value} {status.value} {value}",
        value=value,
        section=section,
        status=status,
        **kwargs,  # type: ignore[arg-type]
    )


def test_precision_is_verified_over_all_five_counted_statuses() -> None:
    """Spec 3.10's definition, with each of the four failures counting the same."""
    claims = [
        claim(ReportSection.outcomes, ClaimStatus.verified),
        claim(ReportSection.outcomes, ClaimStatus.mismatch),
        claim(ReportSection.outcomes, ClaimStatus.unsupported),
        claim(ReportSection.outcomes, ClaimStatus.dangling),
        claim(ReportSection.outcomes, ClaimStatus.unattributed),
    ]
    figure = grounding(claims)
    assert figure.precision == 0.2
    assert figure.n_claims == 5
    assert figure.status_counts == {
        "verified": 1,
        "mismatch": 1,
        "unsupported": 1,
        "dangling": 1,
        "unattributed": 1,
    }


def test_the_per_section_rows_are_in_report_order_and_omit_empty_sections() -> None:
    """Appendix A prints the sections a report actually has, in the order it prints them."""
    claims = [
        claim(ReportSection.monitoring, ClaimStatus.verified),
        claim(ReportSection.summary, ClaimStatus.verified),
        claim(ReportSection.summary, ClaimStatus.mismatch),
    ]
    figure = grounding(claims)
    assert list(figure.per_section) == ["summary", "monitoring"]
    assert figure.per_section["summary"].precision == 0.5
    assert figure.per_section["monitoring"].precision == 1.0


def test_a_report_with_no_claims_scores_zero_rather_than_one() -> None:
    """A vacuous 1.0000 on an empty report is the one number that could flatter (D-066)."""
    figure = grounding([])
    assert figure.precision == 0.0
    assert figure.n_claims == 0
    assert figure.per_section == {}
    assert precision_of(0, 0) == 0.0


def test_a_not_evaluated_developer_claim_is_counted_neither_way() -> None:
    """It was never compared to anything, so counting it would be an opinion (D-016)."""
    claims = [
        claim(ReportSection.outcomes, ClaimStatus.verified),
        VerifiedClaim(
            text="AUC on the test split is 0.755",
            value=0.755,
            section=ReportSection.outcomes,
            source=ClaimSource.developer,
            status=ClaimStatus.not_evaluated,
        ),
    ]
    figure = grounding(claims)
    assert (figure.precision, figure.n_claims) == (1.0, 1)


def test_precision_is_rounded_to_four_decimals() -> None:
    """The width the front matter prints; 12 of 13 is 0.9231, as the golden states."""
    claims = [claim(ReportSection.summary, ClaimStatus.verified, value=i) for i in range(12)]
    claims.append(claim(ReportSection.summary, ClaimStatus.unsupported, value=99))
    assert grounding(claims).precision == 0.9231


def test_a_figure_serialises_to_the_shape_claims_json_holds() -> None:
    """`to_payload` is what `ClaimsDocument` writes and `eval/score.py` reads."""
    figure = grounding([claim(ReportSection.outcomes, ClaimStatus.verified)])
    assert figure.to_payload() == {
        "precision": 1.0,
        "n_claims": 1,
        "status_counts": {
            "verified": 1,
            "mismatch": 0,
            "unsupported": 0,
            "dangling": 0,
            "unattributed": 0,
        },
        "per_section": {"outcomes": {"verified": 1, "n_claims": 1, "precision": 1.0}},
    }
