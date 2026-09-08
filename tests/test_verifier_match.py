"""Phase 7: the deterministic matcher, tolerance by tolerance.

Spec section 3.10's acceptance criteria are here as tests: the 0.6 section, percent-to-ratio
normalisation in both directions, a declared rounding, a table-cell citation, a two-token delta,
and the one-token delta that has to dangle with a message rather than quietly verify against its
single operand.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.trace import EventType, TraceReader, TraceWriter
from quaestor.verifier import (
    Claim,
    ClaimStatus,
    Comparison,
    Unit,
    grounding,
    match_claim,
    match_claims,
    tolerance_for,
)
from quaestor.vocab import ReportSection

SECTION = ReportSection.outcomes


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with the scalars, the table and the JSON artifact these tests cite."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar)
    store.put("metrics.train.auc", 0.7538, ArtifactKind.scalar)
    store.put("metrics.test.event_rate", 0.22, ArtifactKind.scalar)
    store.put("metrics.test.mean_predicted", 0.2213, ArtifactKind.scalar)
    store.put("metrics.test.n", 1500, ArtifactKind.scalar)
    store.put("threshold.M1.vif", 10, ArtifactKind.scalar)
    store.put(
        "deciles.test",
        [
            {"decile": 1, "count": 150, "events": 74, "event_rate": 0.493, "lift": 2.2409},
            {"decile": 2, "count": 150, "events": 52, "event_rate": 0.347, "lift": 1.58},
        ],
        ArtifactKind.table,
    )
    store.put(
        "run.model_summary",
        {"coefficients": [{"feature": "utilisation", "value": 0.487}]},
        ArtifactKind.json,
    )
    return store


def cite(store: ArtifactStore, name: str, path: str | None = None) -> str:
    """The citation that resolves to one artifact of the fixture store."""
    return store.artifact(name).citation(path)


def claim(store: ArtifactStore, value: float, name: str | None = None, **kwargs: object) -> Claim:
    """A claim over one artifact, or with no citation when no name is given."""
    citation = cite(store, name) if name else None
    return Claim(
        text=f"the value is {value}",
        value=value,
        citation=citation,
        section=SECTION,
        **kwargs,  # type: ignore[arg-type]
    )


def test_three_cited_correct_one_mismatched_and_one_uncited_yields_0_6(
    store: ArtifactStore,
) -> None:
    """Spec 3.10's own acceptance example, end to end through the grounding figure."""
    claims = [
        claim(store, 0.7412, "metrics.test.auc"),
        claim(store, 0.7538, "metrics.train.auc"),
        claim(store, 0.22, "metrics.test.event_rate"),
        claim(store, 0.99, "metrics.test.mean_predicted"),
        claim(store, 1500, unit=Unit.count),
    ]
    matches = match_claims(claims, store)
    assert [match.status for match in matches] == [
        ClaimStatus.verified,
        ClaimStatus.verified,
        ClaimStatus.verified,
        ClaimStatus.mismatch,
        ClaimStatus.unsupported,
    ]
    figure = grounding([match.claim for match in matches])
    assert figure.precision == 0.6
    assert figure.n_claims == 5
    assert figure.per_section[SECTION.value].precision == 0.6


def test_a_percent_verifies_against_a_unit_interval_artifact(store: ArtifactStore) -> None:
    """`22.0%` against 0.22 verifies, after percent-to-ratio normalisation (D-014)."""
    match = match_claim(claim(store, 22.0, "metrics.test.event_rate", unit=Unit.percent), store)
    assert match.status is ClaimStatus.verified
    assert match.claim.artifact_value == 0.22
    assert match.claim.tolerance == 0.005


def test_a_rounded_percent_verifies_and_a_wrong_one_does_not(store: ArtifactStore) -> None:
    """`22%` against 0.2213 is inside 0.005; `23%` is not, and the message says what is."""
    ok = match_claim(claim(store, 22, "metrics.test.mean_predicted", unit=Unit.percent), store)
    bad = match_claim(claim(store, 23, "metrics.test.mean_predicted", unit=Unit.percent), store)
    assert ok.status is ClaimStatus.verified
    assert bad.status is ClaimStatus.mismatch
    assert bad.claim.artifact_value == 0.2213
    assert "0.2213" in (bad.message or "")


def test_a_declared_rounding_lets_a_lift_of_2_24_verify_against_2_2409(
    store: ArtifactStore,
) -> None:
    """A drafter that writes fewer decimals is being honest; rounding widens, never narrows."""
    match = match_claim(
        Claim(
            text="a lift of 2.24",
            value=2.24,
            rounding=2,
            citation=cite(store, "deciles.test", "1.lift"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.verified
    assert match.claim.artifact_value == 2.2409


def test_a_table_cell_citation_resolves(store: ArtifactStore) -> None:
    """`#<row_key>.<column>` addresses a cell by the value in the table's first column."""
    match = match_claim(
        Claim(
            text="the top decile defaults at 0.493",
            value=0.493,
            citation=cite(store, "deciles.test", "1.event_rate"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.verified


def test_a_json_path_citation_resolves(store: ArtifactStore) -> None:
    """A dotted path addresses a list element by its `feature` (D-026)."""
    match = match_claim(
        Claim(
            text="the coefficient on utilisation is 0.487",
            value=0.487,
            citation=cite(store, "run.model_summary", "coefficients.utilisation.value"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.verified


def test_a_two_token_delta_verifies_against_second_minus_first(store: ArtifactStore) -> None:
    """The claimed value is `second - first`, in the order the two citations are written."""
    match = match_claim(
        Claim(
            text="the train-to-test gap is 0.0126",
            value=0.0126,
            comparison=Comparison.delta,
            citation=cite(store, "metrics.test.auc") + cite(store, "metrics.train.auc"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.verified
    assert match.claim.artifact_value == pytest.approx(0.0126)


def test_a_one_token_delta_dangles_with_a_message(store: ArtifactStore) -> None:
    """A delta with one operand is not a delta; it dangles rather than verifying by accident."""
    match = match_claim(
        Claim(
            text="the train-to-test gap is 0.0126",
            value=0.0126,
            comparison=Comparison.delta,
            citation=cite(store, "metrics.test.auc"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling
    assert "two adjacent" in (match.message or "")
    assert match.claim.artifact_value is None


def test_a_ratio_comparison_divides_second_by_first(store: ArtifactStore) -> None:
    """`ratio` is `second / first`, the counterpart of `delta`."""
    match = match_claim(
        Claim(
            text="test AUC is 0.983 of train",
            value=0.7412 / 0.7538,
            comparison=Comparison.ratio,
            citation=cite(store, "metrics.train.auc") + cite(store, "metrics.test.auc"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.verified


def test_a_citation_to_a_hash_that_is_not_the_artifact_s_dangles(store: ArtifactStore) -> None:
    """A number cited to another run's hash is not grounded in this run."""
    match = match_claim(
        Claim(
            text="AUC is 0.7412",
            value=0.7412,
            citation="[[art:deadbeef:metrics.test.auc]]",
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling
    assert "deadbeef" in (match.message or "")


def test_a_citation_to_an_unknown_logical_name_dangles(store: ArtifactStore) -> None:
    """The message names what was cited, which is what the repair loop hands back."""
    match = match_claim(
        Claim(
            text="AUC is 0.7412",
            value=0.7412,
            citation="[[art:deadbeef:metrics.oot.auc]]",
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling
    assert "metrics.oot.auc" in (match.message or "")


def test_a_regulatory_citation_on_a_number_dangles(store: ArtifactStore) -> None:
    """A number is grounded in an artifact; guidance is not evidence for a value."""
    match = match_claim(
        Claim(
            text="the guidance is at V.1.c",
            value=1.0,
            citation="[[reg:SR11-7:V.1.c]]",
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling
    assert "names no artifact" in (match.message or "")


def test_a_malformed_citation_dangles_rather_than_raising(store: ArtifactStore) -> None:
    """A malformed citation is a drafting failure, not a crash."""
    match = match_claim(
        Claim(text="AUC is 0.7412", value=0.7412, citation="[[art:nocolon]]", section=SECTION),
        store,
    )
    assert match.status is ClaimStatus.dangling
    assert "does not parse" in (match.message or "")


def test_a_pre_pass_claim_is_unattributed_not_unsupported(store: ArtifactStore) -> None:
    """The two are different failures and the study counts them separately."""
    match = match_claim(claim(store, 1500, unit=Unit.count), store, unattributed=True)
    assert match.status is ClaimStatus.unattributed
    assert "did not return it" in (match.message or "")


def test_a_count_matches_to_half_a_unit(store: ArtifactStore) -> None:
    """1% of 1,500 rows would verify a claim of 1,510, which is simply false (D-014)."""
    assert tolerance_for(Unit.count, 1500.0) == 0.5
    near = match_claim(claim(store, 1500, "metrics.test.n", unit=Unit.count), store)
    off_by_ten = match_claim(claim(store, 1510, "metrics.test.n", unit=Unit.count), store)
    assert near.status is ClaimStatus.verified
    assert off_by_ten.status is ClaimStatus.mismatch


def test_a_ratio_above_one_uses_the_relative_default(store: ArtifactStore) -> None:
    """A VIF threshold of 10 is matched to 1%, not to 0.005."""
    assert tolerance_for(Unit.ratio, 10.0) == pytest.approx(0.1)
    match = match_claim(claim(store, 10, "threshold.M1.vif"), store)
    assert match.claim.tolerance == pytest.approx(0.1)
    assert match.status is ClaimStatus.verified


def test_basis_points_normalise_against_a_rate() -> None:
    """25 bp is 0.0025 when what it is compared to is a rate rather than a shock."""
    from quaestor.verifier import normalise

    assert normalise(Unit.bp, 25.0, 0.0025) == pytest.approx(0.0025)
    assert normalise(Unit.bp, -300.0, -300.0) == -300.0


def test_a_ratio_comparison_by_zero_dangles(tmp_path: Path) -> None:
    """Dividing by a zero artifact is reported, not raised."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("a", 0.0, ArtifactKind.scalar)
    store.put("b", 1.0, ArtifactKind.scalar)
    match = match_claim(
        Claim(
            text="b is infinitely more than a",
            value=2.0,
            comparison=Comparison.ratio,
            citation=cite(store, "a") + cite(store, "b"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling
    assert "is zero" in (match.message or "")


def test_a_citation_that_resolves_to_a_table_without_a_cell_dangles(
    store: ArtifactStore,
) -> None:
    """A table has no single value; the message says to address a cell."""
    match = match_claim(
        Claim(
            text="the deciles are 10",
            value=10,
            citation=cite(store, "deciles.test"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling


def test_every_match_writes_one_claim_check_event(store: ArtifactStore, tmp_path: Path) -> None:
    """`eval/score.py` reads the trace; a claim check that left no trace is uncounted."""
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="r1")
    match_claims(
        [claim(store, 0.7412, "metrics.test.auc"), claim(store, 1500, unit=Unit.count)],
        store,
        trace=trace,
    )
    events = TraceReader(tmp_path / "trace.jsonl").events(EventType.claim_check)
    assert [event.payload["status"] for event in events] == ["verified", "unsupported"]


def test_a_citation_that_resolves_to_a_figure_dangles(tmp_path: Path) -> None:
    """A figure is evidence a reader looks at; it holds no number to match a claim against."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("plot.calibration", b"\x89PNG\r\n\x1a\n", ArtifactKind.figure)
    match = match_claim(
        Claim(
            text="the plot shows 0.5",
            value=0.5,
            citation=cite(store, "plot.calibration"),
            section=SECTION,
        ),
        store,
    )
    assert match.status is ClaimStatus.dangling


def test_a_json_path_that_resolves_to_text_dangles(store: ArtifactStore, tmp_path: Path) -> None:
    """Nothing can be compared to a string, so the claim dangles with a message that says so."""
    other = ArtifactStore(tmp_path / "second")
    other.put("run.status", {"memory_cap": "unenforced"}, ArtifactKind.json)
    match = match_claim(
        Claim(
            text="the memory cap is 4096",
            value=4096,
            citation=other.artifact("run.status").citation("memory_cap"),
            section=SECTION,
        ),
        other,
    )
    assert match.status is ClaimStatus.dangling
    assert "not a number" in (match.message or "")


def test_with_citation_keeps_the_claim_s_identity(store: ArtifactStore) -> None:
    """The id names `[section, text, value]`, none of which a repaired citation moves."""
    original = claim(store, 0.7412)
    recited = original.with_citation(cite(store, "metrics.test.auc"))
    assert recited.id == original.id
    assert match_claim(recited, store).status is ClaimStatus.verified


def test_a_verified_claim_reports_whether_it_is_counted(store: ArtifactStore) -> None:
    """`is_verified` and `counts_towards_grounding` are what the renderer reads."""
    match = match_claim(claim(store, 0.7412, "metrics.test.auc"), store)
    assert match.claim.is_verified
    assert match.claim.counts_towards_grounding
