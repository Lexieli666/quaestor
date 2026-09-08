"""Phase 7: the offline half of the verifier component eval, over ten committed fixtures.

`04-SEEDED-DEFECT-STUDY.md` section 6. Each item is a table this repository wrote, a question, a
gold answer and its arithmetic; no FinQA or TAT-QA row is copied here. Three sentences per item --
correctly cited, perturbed, uncited -- must come out `verified`, `mismatch`, `unsupported`, with
one exception that is the point of the exercise: a perturbation that lands inside the 0.005 the
claim grammar allows is *supposed* to verify, and is reported as a tolerance boundary rather than
as an error.

The live half, over 150 sampled FinQA and 150 sampled TAT-QA items with cassettes committed, is
Phase 13. Nothing here calls a model: the extractor is a `FakeLLM` that computes its answer from
the prompt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT, load_module
from quaestor.verifier import ClaimStatus, Unit

sys.path.insert(0, str(REPO_ROOT / "eval"))
verifier_eval = load_module("quaestor_verifier_eval", REPO_ROOT / "eval" / "verifier_eval.py")

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "verifier_eval"


def test_ten_items_are_committed_and_load() -> None:
    """`04` section 6 asks for ten; the count is asserted so a lost file is a failure."""
    items = verifier_eval.load_fixtures(FIXTURES)
    assert len(items) == 10
    assert [item.id for item in items] == [f"vq{i:02d}" for i in range(1, 11)]
    for item in items:
        assert item.arithmetic and item.question and item.label
        assert len(item.table) >= 2


def test_no_fixture_quotes_a_public_dataset() -> None:
    """The tables are this repository's own, which is the licence position `04` section 6 takes."""
    text = " ".join(path.read_text(encoding="utf-8") for path in sorted(FIXTURES.glob("*.json")))
    assert "finqa" not in text.lower()
    assert "tatqa" not in text.lower()


def test_the_builder_loads_cells_as_scalars_and_the_answer_as_answer(tmp_path: Path) -> None:
    """One logical name per numeric cell, `table.r<i>.c<j>`, and the gold answer as `answer`."""
    item = verifier_eval.load_fixtures(FIXTURES)[0]
    store = verifier_eval.build_store(item, tmp_path / "store")
    assert store.value("answer") == item.answer
    assert store.value("table.r2.c2") == 1200.0
    assert store.value("table.r2.c3") == 1500.0
    assert "table.r2.c1" not in store


def test_each_item_draws_one_of_the_five_perturbation_types() -> None:
    """The type is a function of the item and the seed, so a run reproduces exactly."""
    kinds = {
        item.id: verifier_eval.perturbation_for(item.id)
        for item in verifier_eval.load_fixtures(FIXTURES)
    }
    assert set(kinds.values()) <= set(verifier_eval.PERTURBATIONS)
    assert len(set(kinds.values())) >= 3
    assert kinds == {
        item.id: verifier_eval.perturbation_for(item.id)
        for item in verifier_eval.load_fixtures(FIXTURES)
    }


def test_every_perturbation_type_moves_the_value() -> None:
    """A perturbation that returned the value unchanged would make (b) verify by construction."""
    for kind in verifier_eval.PERTURBATIONS:
        assert verifier_eval.perturb(0.42, kind, "vq09") != 0.42
    assert verifier_eval.perturb(1000.0, "digit_transposition", "vq01") == 100.0


def test_an_unknown_perturbation_is_refused() -> None:
    """The five are the five `04` section 6 names."""
    with pytest.raises(ValueError, match="not one of"):
        verifier_eval.perturb(1.0, "noise", "vq01")


def test_the_three_sentences_come_out_verified_mismatch_unsupported(tmp_path: Path) -> None:
    """The acceptance of `04` section 6, item by item, with the boundary case named."""
    report = verifier_eval.run_offline(verifier_eval.fake_extractor(), tmp_path)
    assert report.n_items == 10
    for result in report.results:
        statuses = [sentence.status for sentence in result.sentences]
        assert statuses[0] is ClaimStatus.verified, result.item_id
        assert statuses[2] is ClaimStatus.unsupported, result.item_id
        if result.item_id in report.tolerance_boundaries:
            assert statuses[1] is ClaimStatus.verified, result.item_id
        else:
            assert statuses[1] is ClaimStatus.mismatch, result.item_id
        assert result.ok, result.item_id
    assert report.status_accuracy == {"verified": 1.0, "mismatch": 1.0, "unsupported": 1.0}
    assert report.extraction_recall == 1.0


def test_no_perturbation_now_lands_inside_tolerance(tmp_path: Path) -> None:
    """Under D-069 there is no boundary left: all thirty sentences come out as `04` expects.

    Phase 7 measured two of the ten items -- `vq04`, whose 0.035 was perturbed to 0.03255, and
    `vq10`, whose 0.0725 was perturbed to 0.076125 -- as tolerance boundaries: both moves were
    inside the flat 0.005 D-014 allowed a unit-interval ratio, so the perturbed sentence verified
    and was reported as a boundary rather than as an error. The amendment holds a number to the
    precision its prose wrote, and both sentences write four decimals, so both are now caught as
    the mismatches they are. The boundary machinery stays, because the live half of the component
    eval (Phase 13) will meet coarser prose.
    """
    report = verifier_eval.run_offline(verifier_eval.fake_extractor(), tmp_path)
    assert report.tolerance_boundaries == []
    for result in report.results:
        perturbed = result.sentences[1]
        assert perturbed.status is ClaimStatus.mismatch, result.item_id
        assert perturbed.artifact_value is not None
        assert abs(perturbed.value - perturbed.artifact_value) > perturbed.tolerance


def test_an_extractor_that_omits_a_number_is_caught_by_the_pre_pass(tmp_path: Path) -> None:
    """Extraction recall is a measurement, not an assumption: a silent extractor scores zero."""
    from quaestor.llm import FakeLLM

    silent = FakeLLM(default='{"claims": []}')
    report = verifier_eval.run_offline(silent, tmp_path / "silent")
    assert report.extraction_recall == 0.0
    for result in report.results:
        assert [sentence.status for sentence in result.sentences] == [ClaimStatus.unattributed] * 3


def test_the_offline_entry_point_writes_its_summary(tmp_path: Path) -> None:
    """`eval/verifier_eval.py` runs as a script and reports a status code."""
    code = verifier_eval.main(
        [
            "--fixtures",
            str(FIXTURES),
            "--work",
            str(tmp_path / "work"),
            "--out",
            str(tmp_path / "summary.json"),
        ]
    )
    assert code == 0
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["n_items"] == 10
    assert summary["seed"] == verifier_eval.SEED


def test_a_percent_fixture_is_written_with_its_sign(tmp_path: Path) -> None:
    """The rendered sentence has to look like report prose, per cent sign included."""
    item = next(item for item in verifier_eval.load_fixtures(FIXTURES) if item.unit is Unit.percent)
    store = verifier_eval.build_store(item, tmp_path / "store")
    markdown = verifier_eval.section_markdown(item, store)
    assert "%" in markdown.splitlines()[0]
