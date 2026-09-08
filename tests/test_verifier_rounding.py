"""Phase 8: the rounding amendment (DECISIONS D-069), example by example.

The amendment is a sentence: *a claim verifies when the artifact value rounds to the written value
at the precision the prose used*, with spec section 0's three defaults as a ceiling the tolerance
never exceeds, counts exact, and `rounding` an explicit override that can only narrow. Its three
worked examples are the first three tests here; the rest are the edges the sentence leaves to an
implementation -- where the precision is read from, what happens to a per cent, and what a
declared `rounding` may and may not do.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.verifier import (
    Claim,
    ClaimStatus,
    Unit,
    default_tolerance,
    match_claim,
    normalisation_scale,
    tolerance_for,
    written_decimals,
)
from quaestor.vocab import ReportSection

SECTION = ReportSection.outcomes


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """The three artifacts the amendment's own examples are stated against."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar)
    store.put("psi.max", 0.0175, ArtifactKind.scalar)
    store.put("metrics.test.event_rate", 0.2212, ArtifactKind.scalar)
    store.put("metrics.test.n", 1500, ArtifactKind.scalar)
    store.put("vif.utilisation", 4.3149, ArtifactKind.scalar)
    store.put("ablation.utilisation.delta_auc", 1.9204697640939905e-05, ArtifactKind.scalar)
    store.put("ablation.pay_ratio_last.delta_auc", -5.589426925389773e-05, ArtifactKind.scalar)
    store.put("csi.bill_mean_6m", 9.982086887188549e-06, ArtifactKind.scalar)
    return store


def written(store: ArtifactStore, token: str, name: str, **kwargs: object) -> Claim:
    """A claim whose sentence writes `token`, cited to one artifact of the fixture store."""
    return Claim(
        text=f"the figure is {token} {store.artifact(name).citation()} on the test split.",
        value=float(token.rstrip("%")),
        citation=store.artifact(name).citation(),
        section=SECTION,
        **kwargs,  # type: ignore[arg-type]
    )


def test_0_74_verifies_against_0_7412(store: ArtifactStore) -> None:
    """Two decimals of prose, so the artifact has to round to two decimals, and it does."""
    match = match_claim(written(store, "0.74", "metrics.test.auc"), store)
    assert match.status is ClaimStatus.verified
    assert match.claim.tolerance == pytest.approx(0.005)


def test_0_021_does_not_verify_against_0_0175(store: ArtifactStore) -> None:
    """0.0175 rounds to 0.018, not to 0.021, and the flat 0.005 default used to admit it."""
    match = match_claim(written(store, "0.021", "psi.max"), store)
    assert match.status is ClaimStatus.mismatch
    assert match.claim.tolerance == pytest.approx(0.0005)
    assert default_tolerance(Unit.ratio, 0.0175) == 0.005
    assert "0.0175" in (match.message or "")


def test_22_0_percent_does_not_verify_against_0_2212(store: ArtifactStore) -> None:
    """One decimal of a per cent is a thousandth of a rate, so 22.12% is not 22.0%."""
    match = match_claim(
        written(store, "22.0%", "metrics.test.event_rate", unit=Unit.percent), store
    )
    assert match.status is ClaimStatus.mismatch
    assert match.claim.artifact_value == 0.2212
    assert match.claim.tolerance == pytest.approx(0.0005)


def test_22_percent_still_verifies_against_0_2212(store: ArtifactStore) -> None:
    """The same number written with no decimal claims less and is held to less."""
    match = match_claim(written(store, "22%", "metrics.test.event_rate", unit=Unit.percent), store)
    assert match.status is ClaimStatus.verified
    assert match.claim.tolerance == pytest.approx(0.005)


def test_the_precision_is_read_from_the_sentence_not_from_the_float() -> None:
    """`22.0` and `22` are one float and two statements; only the prose tells them apart."""
    assert written_decimals(22.0, "the rate is 22.0% in test") == 1
    assert written_decimals(22.0, "the rate is 22% in test") == 0
    assert written_decimals(0.7412, "0.7538 against 0.7412") == 4


def test_trailing_zeros_before_the_point_claim_less_and_not_more() -> None:
    """A currency amount written to four significant figures claims nothing below the fifth."""
    assert written_decimals(3500.0, "the split holds 3,500 clients") == -2
    assert written_decimals(-1130000.0, "the value change is -1130000 at the down shock") == -4
    assert tolerance_for(Unit.ratio, -1129931.65, decimals=-4) == pytest.approx(5000.0)
    # The ceiling still binds: a threshold of 10 written "10" is held to 1% of 10, not to five.
    assert tolerance_for(Unit.ratio, 10.0, decimals=-1) == pytest.approx(0.1)


def test_a_number_the_sentence_does_not_hold_falls_back_to_its_own_shortest_form() -> None:
    """A developer claim rebuilt from `package.yaml` has no token to read (D-069)."""
    assert written_decimals(0.76, None) == 2
    assert written_decimals(0.76, "AUC on test is high") == 2
    assert written_decimals(1500.0) == -2
    assert written_decimals(1e-05) == 5


def test_the_default_for_the_unit_is_a_ceiling_and_never_a_floor(store: ArtifactStore) -> None:
    """Ten decimals of prose cannot make a tolerance wider than spec section 0 allows."""
    assert tolerance_for(Unit.ratio, 0.5, decimals=0) == 0.005
    assert tolerance_for(Unit.ratio, 0.5, decimals=4) == pytest.approx(0.00005)
    assert tolerance_for(Unit.ratio, 40.0, decimals=0) == pytest.approx(0.4)
    assert tolerance_for(Unit.ratio, 40.0, decimals=2) == pytest.approx(0.005)


def test_a_tolerance_in_written_units_is_carried_into_the_artifact_s_units() -> None:
    """Half a tenth of a per cent is 0.0005 against a rate; 25 bp against a rate is 0.0025."""
    assert normalisation_scale(Unit.percent, 0.22) == pytest.approx(0.01)
    assert normalisation_scale(Unit.bp, 0.0025) == pytest.approx(0.0001)
    assert normalisation_scale(Unit.percent, 22.0) == 1.0
    assert normalisation_scale(Unit.bp, -300.0) == 1.0
    assert normalisation_scale(Unit.ratio, 0.22) == 1.0
    assert tolerance_for(Unit.bp, 0.0025, decimals=0) == pytest.approx(5e-05)


def test_a_count_stays_exact_however_it_was_written(store: ArtifactStore) -> None:
    """`counts stay exact`: half a unit, whatever precision the prose chose."""
    assert tolerance_for(Unit.count, 1500.0, decimals=3) == 0.5
    near = match_claim(written(store, "1500", "metrics.test.n", unit=Unit.count), store)
    off = match_claim(written(store, "1502", "metrics.test.n", unit=Unit.count), store)
    assert near.status is ClaimStatus.verified
    assert off.status is ClaimStatus.mismatch


def test_a_declared_rounding_narrows_and_cannot_widen(store: ArtifactStore) -> None:
    """D-014 let `rounding` widen a tolerance; D-069 keeps the field and reverses its direction."""
    assert tolerance_for(Unit.ratio, 4.3149, rounding=2, decimals=2) == pytest.approx(0.005)
    assert tolerance_for(Unit.ratio, 4.3149, rounding=0, decimals=2) == pytest.approx(0.005)
    assert tolerance_for(Unit.ratio, 4.3149, rounding=4, decimals=2) == pytest.approx(0.00005)
    loose = match_claim(written(store, "4.31", "vif.utilisation", rounding=0), store)
    tight = match_claim(written(store, "4.31", "vif.utilisation", rounding=4), store)
    assert loose.status is ClaimStatus.verified
    assert tight.status is ClaimStatus.mismatch


# --- exponent notation (DECISIONS D-099) --------------------------------------------------------


@pytest.mark.parametrize(
    ("token", "decimals"),
    [("1.92e-05", 7), ("-5.589e-05", 8), ("9.982e-06", 9), ("1.920e-05", 8), ("5e3", -3)],
)
def test_the_exponent_shifts_the_place_value_of_the_last_digit(token: str, decimals: int) -> None:
    """The mantissa keeps the precision and the exponent moves it: 1.920e-05 claims 10^-8."""
    assert written_decimals(float(token), f"the figure is {token} on the test split.") == decimals


@pytest.mark.parametrize(
    ("token", "name"),
    [
        ("1.92e-05", "ablation.utilisation.delta_auc"),
        ("1.920e-05", "ablation.utilisation.delta_auc"),
        ("-5.589e-05", "ablation.pay_ratio_last.delta_auc"),
        ("9.982e-06", "csi.bill_mean_6m"),
    ],
)
def test_the_fourth_live_run_s_exponent_claims_verify(
    store: ArtifactStore, token: str, name: str
) -> None:
    """The three literals of the fourth live run, and the extra decimal D-099's test asks for.

    Every one of them was `unattributed` on that run -- the tokenizer split `1.92e-05` into 1.92
    and 05, so no claim could ever have covered either half.
    """
    match = match_claim(written(store, token, name), store)
    assert match.status is ClaimStatus.verified, match.message
    assert match.claim.value == pytest.approx(float(token))


def test_an_exponent_claim_one_order_out_still_does_not_verify(store: ArtifactStore) -> None:
    """The tolerance is the mantissa's precision scaled, not the mantissa's precision."""
    match = match_claim(written(store, "1.92e-04", "ablation.utilisation.delta_auc"), store)
    assert match.status is ClaimStatus.mismatch
