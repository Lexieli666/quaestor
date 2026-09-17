"""The rule that mints section 6's open items, and the three families it reads.

`### Open items` has been in every report since D-096, and until now the drafter decided what went
into it from two examples in a brief. That is the shape D-156 and D-165 already removed from the
findings list, and the committed real-MSR run shows why: its store holds three coefficients whose
fitted sign contradicts their univariate direction -- one of D-096's own two examples -- and its
section 6 asks about none of them. `quaestor.findings.open_items` is the rule, and these tests
pin what it mints, what it declines to mint at each boundary, and that its order is fixed, because
`eval/score.py` imports the same function and compares two runs' lists against each other.

Nothing here calls a model or reads real data: the stores are built by hand, except the one
regression that reads the artifact index committed with the real-MSR run.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.findings import OPEN_ITEM_OWNER, OpenItemKind, open_items
from quaestor.tools.leakage import FEATURE_OVERLAP_BOUND, OVERLAP_THRESHOLD
from quaestor.tools.thresholds import DEFAULT_THRESHOLDS, SLICE_GAP_BOUND, SLICE_SHARE_FLOOR

LIVE_MSR = Path(__file__).resolve().parents[1] / "eval" / "results" / "first-live" / "msr"


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store holding the two slice bounds and nothing that qualifies under them."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put(SLICE_GAP_BOUND, DEFAULT_THRESHOLDS[SLICE_GAP_BOUND], ArtifactKind.scalar)
    store.put(SLICE_SHARE_FLOOR, DEFAULT_THRESHOLDS[SLICE_SHARE_FLOOR], ArtifactKind.scalar)
    return store


def add_slice(store: ArtifactStore, stem: str, *, gap: float, share: float) -> None:
    """Store one sub-population's gap, share, AUC and its split's headline AUC."""
    head = stem.split(".sub.", 1)[0]
    store.put(f"{stem}.auc_gap", gap, ArtifactKind.scalar)
    store.put(f"{stem}.share", share, ArtifactKind.scalar)
    store.put(f"{stem}.auc", 0.7 - gap, ArtifactKind.scalar)
    store.put(f"{head}.auc", 0.7, ArtifactKind.scalar)


def add_sign(store: ArtifactStore, feature: str, *, coef: float, direction: float) -> None:
    """Store one feature's fitted sign against its univariate direction, as D-095 does."""
    store.put(f"sign_check.{feature}.coef_sign", coef, ArtifactKind.scalar)
    store.put(f"sign_check.{feature}.univariate_direction", direction, ArtifactKind.scalar)
    store.put(f"sign_check.{feature}.agrees", float(coef == direction), ArtifactKind.scalar)


def add_overlap(store: ArtifactStore, *, features: float, duplicates: float) -> None:
    """Store the feature-vector overlap, the within-train duplicates and both bounds (D-086)."""
    declared = DEFAULT_THRESHOLDS[OVERLAP_THRESHOLD]
    store.put("leakage.overlap.features", features, ArtifactKind.scalar)
    store.put("leakage.duplicates.train", duplicates, ArtifactKind.scalar)
    store.put(OVERLAP_THRESHOLD, declared, ArtifactKind.scalar)
    store.put(FEATURE_OVERLAP_BOUND, max(declared, 2.0 * duplicates), ArtifactKind.scalar)


# --- the sub-population rule (D-102) --------------------------------------------------------


def test_a_slice_past_the_gap_bound_on_enough_of_the_split_is_an_open_item(
    store: ArtifactStore,
) -> None:
    """The same rule `follow_up_for` applies to a loop step, read off the store instead."""
    add_slice(store, "metrics.test.sub.incentive_high", gap=0.09, share=0.5)
    (item,) = open_items(store, DEFAULT_THRESHOLDS)
    assert item.kind is OpenItemKind.slice_gap
    assert item.subject == "metrics.test.sub.incentive_high"
    assert item.bound == SLICE_GAP_BOUND
    assert item.owner == OPEN_ITEM_OWNER
    assert "0.09" in item.detail and "0.08" in item.detail
    assert item.artifacts == [
        "metrics.test.sub.incentive_high.auc_gap",
        "metrics.test.sub.incentive_high.share",
        "metrics.test.sub.incentive_high.auc",
        "metrics.test.auc",
        SLICE_GAP_BOUND,
        SLICE_SHARE_FLOOR,
    ]


def test_a_slice_at_the_gap_bound_is_not_an_open_item(store: ArtifactStore) -> None:
    """`follow_up_for` is strict -- `gap > bound` -- and the minting rule has to be too."""
    add_slice(store, "metrics.test.sub.incentive_high", gap=0.08, share=0.5)
    assert open_items(store, DEFAULT_THRESHOLDS) == []


def test_a_slice_below_the_share_floor_cannot_raise_one_however_large_its_gap(
    store: ArtifactStore,
) -> None:
    """D-102's floor: a slice of thirty rows can differ from its split by anything at all."""
    add_slice(store, "metrics.test.sub.tiny", gap=0.4, share=0.09)
    assert open_items(store, DEFAULT_THRESHOLDS) == []


def test_a_threshold_named_auc_gap_is_not_read_as_a_sub_population(
    store: ArtifactStore,
) -> None:
    """`threshold.O1.auc_gap` ends in the same six characters and is not a slice."""
    store.put("threshold.O1.auc_gap", 0.08, ArtifactKind.scalar)
    assert open_items(store, DEFAULT_THRESHOLDS) == []


def test_without_the_two_bounds_in_the_store_no_slice_is_minted(tmp_path: Path) -> None:
    """A comparison against an unstored number is one nothing can check (D-091)."""
    bare = ArtifactStore(tmp_path / "bare")
    add_slice(bare, "metrics.test.sub.incentive_high", gap=0.09, share=0.5)
    assert open_items(bare, DEFAULT_THRESHOLDS) == []


# --- the sign rule (D-095) ------------------------------------------------------------------


def test_a_fitted_sign_that_contradicts_its_univariate_direction_is_an_open_item(
    store: ArtifactStore,
) -> None:
    """D-096 named this as an example; it is now a rule, and the feature is in backticks."""
    add_sign(store, "orig_ltv", coef=-1.0, direction=1.0)
    (item,) = open_items(store, DEFAULT_THRESHOLDS)
    assert item.kind is OpenItemKind.sign_disagreement
    assert item.subject == "orig_ltv"
    assert "`orig_ltv`" in item.detail
    assert item.bound == "sign_check.orig_ltv.univariate_direction"
    assert item.artifacts == [
        "sign_check.orig_ltv.agrees",
        "sign_check.orig_ltv.coef_sign",
        "sign_check.orig_ltv.univariate_direction",
    ]


def test_a_fitted_sign_that_agrees_raises_nothing(store: ArtifactStore) -> None:
    """Most features agree, and a rule that fired on them would be D-086's false alarm again."""
    add_sign(store, "credit_score", coef=1.0, direction=1.0)
    assert open_items(store, DEFAULT_THRESHOLDS) == []


# --- the overlap rule (D-086) ---------------------------------------------------------------


def test_an_overlap_the_duplicate_share_explains_is_an_open_item(store: ArtifactStore) -> None:
    """Above the declared bound, within the effective one: D-086's "no candidate" case."""
    add_overlap(store, features=0.012667, duplicates=0.012857)
    (item,) = open_items(store, DEFAULT_THRESHOLDS)
    assert item.kind is OpenItemKind.feature_overlap
    assert item.bound == FEATURE_OVERLAP_BOUND
    assert item.artifacts == [
        "leakage.overlap.features",
        "leakage.duplicates.train",
        OVERLAP_THRESHOLD,
        FEATURE_OVERLAP_BOUND,
    ]


def test_an_overlap_within_the_declared_bound_is_not_an_open_item(store: ArtifactStore) -> None:
    """Zero overlap is what every synthetic panel has, and it is nothing to answer for."""
    add_overlap(store, features=0.0, duplicates=0.0)
    assert open_items(store, DEFAULT_THRESHOLDS) == []


def test_an_overlap_past_the_effective_bound_is_a_finding_and_not_an_open_item(
    store: ArtifactStore,
) -> None:
    """Past the bound the rule applied, `check_leakage` raises `L2` and an open item doubles it."""
    add_overlap(store, features=0.04, duplicates=0.005)
    assert open_items(store, DEFAULT_THRESHOLDS) == []


def test_the_effective_bound_is_read_from_the_store_because_it_is_not_a_threshold(
    store: ArtifactStore,
) -> None:
    """D-086 derives it from the data, so the resolved thresholds do not carry it."""
    assert FEATURE_OVERLAP_BOUND not in DEFAULT_THRESHOLDS
    add_overlap(store, features=0.012667, duplicates=0.012857)
    assert open_items(store, DEFAULT_THRESHOLDS)[0].bound == FEATURE_OVERLAP_BOUND


# --- the order, which a scorer depends on ----------------------------------------------------


def test_the_order_is_slices_then_signs_then_the_overlap_each_by_name(
    store: ArtifactStore,
) -> None:
    """`eval/score.py` compares two runs' lists, so the order cannot depend on store order."""
    add_overlap(store, features=0.012667, duplicates=0.012857)
    add_sign(store, "sato", coef=-1.0, direction=1.0)
    add_sign(store, "orig_ltv", coef=-1.0, direction=1.0)
    add_slice(store, "metrics.test.sub.b_high", gap=0.09, share=0.5)
    add_slice(store, "metrics.test.sub.a_high", gap=0.12, share=0.5)
    assert [(item.kind.value, item.subject) for item in open_items(store, DEFAULT_THRESHOLDS)] == [
        ("slice_gap", "metrics.test.sub.a_high"),
        ("slice_gap", "metrics.test.sub.b_high"),
        ("sign_disagreement", "orig_ltv"),
        ("sign_disagreement", "sato"),
        ("feature_overlap", "leakage.overlap.features"),
    ]


# --- the regression against the committed real-MSR run ---------------------------------------


def test_the_rule_mints_the_msr_runs_three_slices_and_the_three_signs_it_did_not_write() -> None:
    """The measurement the rule exists for, over the committed run's own artifact store.

    The excerpt run's `### Open items` carries the three sub-populations and nothing else. The
    rule mints those three -- the same three, by name -- and three more: `orig_ltv`, `sato` and
    `season_sin`, whose fitted signs contradict their univariate directions in that run's own
    store, which `sign_check.n_disagreements` records as 3. It mints **more** than the run
    reported and not fewer: a rule that dropped an observation a validator made would be a
    regression, and adding the three the brief's examples named and the drafter did not write is
    the point of having a rule at all (D-173).
    """
    minted = open_items(ArtifactStore(LIVE_MSR / "artifacts"), DEFAULT_THRESHOLDS)
    slices = [item.subject for item in minted if item.kind is OpenItemKind.slice_gap]
    signs = [item.subject for item in minted if item.kind is OpenItemKind.sign_disagreement]
    assert slices == [
        "metrics.out_of_time.sub.incentive_high",
        "metrics.out_of_time.sub.incentive_low",
        "metrics.vintage_holdout.sub.incentive_low",
    ]
    assert signs == ["orig_ltv", "sato", "season_sin"]
    assert [item for item in minted if item.kind is OpenItemKind.feature_overlap] == []
    reported = (LIVE_MSR / "report.md").read_text(encoding="utf-8")
    written = reported.split("### Open items", 1)[1].split("\n## 7.", 1)[0]
    for stem in slices:
        assert f"{stem}.auc_gap]]" in written
    assert "sign_check." not in written
