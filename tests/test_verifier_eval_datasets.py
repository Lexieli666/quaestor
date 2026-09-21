"""Phase 13: the live half of the verifier component eval, run offline.

`04-SEEDED-DEFECT-STUDY.md` section 6 evaluates the claim verifier on its own, on FinQA and
TAT-QA, because the verifier is the differentiating component and a whole-report number cannot
say whether it is the extractor or the matcher that was right. This module tests the code that
does that -- the two loaders, the eligibility rules, the seeded sample, the metrics and the
summary the command prints -- **without either dataset**: every file here is built in the shape
of a dataset out of the ten items this repository wrote for itself in Phase 7 (`datasetsupport`).

Nothing here calls a model. The extractor under test is `verifier_eval.fake_extractor`, a
`FakeLLM` that computes its answer from the prompt, except where a test deliberately gives a
worse one: an extractor that says nothing, one that cannot answer at all, and one that moves a
citation from the answer to a table cell that happens to carry the perturbed number, which is the
one way a perturbed sentence can verify for a reason that is not the tolerance (D-197).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from conftest import REPO_ROOT, load_module
from datasetsupport import write_finqa, write_tatqa
from quaestor.llm import FakeLLM
from quaestor.llm.recording import ReplayLLM
from quaestor.verifier import ClaimStatus, Unit

sys.path.insert(0, str(REPO_ROOT / "eval"))
verifier_eval = load_module("quaestor_verifier_eval", REPO_ROOT / "eval" / "verifier_eval.py")

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "verifier_eval"


@pytest.fixture(scope="module")
def items() -> list[Any]:
    """The ten committed fixture items, which every dataset-shaped file here is built from."""
    return verifier_eval.load_fixtures(FIXTURES)


@pytest.fixture
def datasets(tmp_path: Path, items: list[Any]) -> tuple[Path, Path]:
    """A FinQA-shaped and a TAT-QA-shaped file, each holding the ten items."""
    return (
        write_finqa(tmp_path / "finqa" / "dev.json", items),
        write_tatqa(tmp_path / "tatqa" / "tatqa_dataset_dev.json", items),
    )


# --- the loaders --------------------------------------------------------------------------------


def test_a_finqa_row_becomes_an_item_that_says_where_it_came_from(
    datasets: tuple[Path, Path],
) -> None:
    """The row id is kept beside a slug of it, because an id with a `/` is not a path segment."""
    loaded = verifier_eval.load_finqa(datasets[0])
    assert len(loaded) == 10
    first = loaded[0]
    assert first.dataset == "finqa"
    assert first.source_id == "TEST/vq01/page_1.pdf-1"
    assert first.id == "finqa-TEST_vq01_page_1.pdf-1"
    assert "/" not in first.id


def test_finqa_keeps_only_the_arithmetic_answer_rows(tmp_path: Path, items: list[Any]) -> None:
    """A yes/no answer, an answer that is prose, a row with no program and a row with no table."""
    path = write_finqa(
        tmp_path / "dev.json",
        items[:1],
        extra=[
            {
                "id": "A",
                "table": items[0].table,
                "qa": {"question": "q?", "answer": "no", "program": "greater(1, 2)"},
            },
            {
                "id": "B",
                "table": items[0].table,
                "qa": {"question": "q?", "answer": "4.9\\n", "program": "add(1, 2)"},
            },
            {"id": "C", "table": items[0].table, "qa": {"question": "q?", "answer": "7"}},
            {
                "id": "D",
                "table": [["only one row"]],
                "qa": {"question": "q?", "answer": "7", "program": "add(1, 2)"},
            },
            {"id": "E", "qa": None},
        ],
    )
    assert [item.source_id for item in verifier_eval.load_finqa(path)] == ["TEST/vq01/page_1.pdf-1"]


def test_a_currency_answer_keeps_its_separator_and_loses_its_symbol(
    tmp_path: Path, items: list[Any]
) -> None:
    """FinQA writes `$ 40,444,920`; the store holds a number and the unit records the dollars."""
    path = write_finqa(
        tmp_path / "dev.json",
        [],
        extra=[
            {
                "id": "F",
                "table": items[0].table,
                "qa": {
                    "question": "what is the total consideration?",
                    "answer": "$ 1,234.5",
                    "program": "add(1000, 234.5)",
                },
            }
        ],
    )
    (loaded,) = verifier_eval.load_finqa(path)
    assert loaded.answer == 1234.5
    assert loaded.unit is Unit.currency


def test_tatqa_keeps_arithmetic_and_span_numbers_and_nothing_else(
    tmp_path: Path, items: list[Any]
) -> None:
    """`04` section 6's `span-number` is a `span` answer that is one number (D-195)."""
    table = {"uid": "t", "table": items[0].table}

    def question(uid: str, kind: str, answer: Any) -> dict[str, Any]:
        return {
            "uid": uid,
            "question": "What is the revenue?",
            "answer": answer,
            "answer_type": kind,
            "answer_from": "table",
            "derivation": "",
            "scale": "",
        }

    path = write_tatqa(
        tmp_path / "dev.json",
        [],
        extra=[
            {
                "table": table,
                "paragraphs": [],
                "questions": [
                    question("span-number", "span", ["1500"]),
                    question("span-words", "span", ["a fixed price contract"]),
                    question("multi", "multi-span", ["1500", "1200"]),
                    question("count", "count", 3),
                    question("arith", "arithmetic", 300.0),
                    question("no-answer", "arithmetic", None),
                    question("boolean", "arithmetic", True),
                ],
            }
        ],
    )
    assert sorted(item.source_id for item in verifier_eval.load_tatqa(path)) == [
        "arith",
        "span-number",
    ]


def test_a_tatqa_percent_scale_is_the_unit_and_the_other_scale_words_are_not(
    tmp_path: Path, items: list[Any]
) -> None:
    """A percentage is written with its sign; `million` is the table's unit, not the number's."""
    table = {"uid": "t", "table": items[0].table}

    def question(uid: str, scale: str, answer: float) -> dict[str, Any]:
        return {
            "uid": uid,
            "question": "What is the change in revenue?",
            "answer": answer,
            "answer_type": "arithmetic",
            "answer_from": "table",
            "derivation": "1500 - 1200",
            "scale": scale,
        }

    path = write_tatqa(
        tmp_path / "dev.json",
        [],
        extra=[
            {
                "table": table,
                "paragraphs": [],
                "questions": [question("pct", "percent", 22.2), question("mm", "million", -12.6)],
            }
        ],
    )
    units = {item.source_id: item.unit for item in verifier_eval.load_tatqa(path)}
    assert units == {"pct": Unit.percent, "mm": Unit.ratio}


def test_a_file_that_is_not_a_list_of_rows_is_refused(tmp_path: Path) -> None:
    """Both datasets ship as a JSON list; anything else is a file the operator did not mean."""
    path = tmp_path / "dev.json"
    path.write_text(json.dumps({"rows": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="list of rows"):
        verifier_eval.load_finqa(path)


def test_an_unknown_dataset_name_is_refused() -> None:
    """`load_dataset` dispatches on the two names `04` section 6 fixes and invents no third."""
    with pytest.raises(ValueError, match="not one of"):
        verifier_eval.load_dataset("drop", Path("nowhere.json"))


# --- the label and the eligibility rules --------------------------------------------------------


@pytest.mark.parametrize(
    ("question", "label"),
    [
        ("What is the average payment volume?", "average payment volume"),
        ("what was the total revenue in 2019?", "total revenue in 2019"),
        ("How many shares were outstanding?", "shares were outstanding"),
        ("By how much did revenue grow?", 'answer to "By how much did revenue grow"'),
        ("what is the change?", "change"),
        ("Revenue?", 'answer to "Revenue"'),
    ],
)
def test_the_label_is_a_noun_phrase_when_the_stem_strips_and_a_quotation_otherwise(
    question: str, label: str
) -> None:
    """A stem that leaves a verb behind is not stripped: the sentence has to be English."""
    assert verifier_eval.label_for(question) == label


def _item(**changes: Any) -> Any:
    """A minimal candidate item, with the fields a test wants to break replaced."""
    fields: dict[str, Any] = {
        "id": "cand-01",
        "question": "What is the total?",
        "label": "total",
        "table": [["item", "value"], ["revenue", "1500"]],
        "arithmetic": "1500",
        "answer": 1500.0,
        "unit": Unit.ratio,
        "dataset": "finqa",
        "source_id": "cand-01",
    }
    fields.update(changes)
    return verifier_eval.FixtureItem(**fields)


def test_eligibility_refuses_the_shapes_that_would_confound_a_sentence() -> None:
    """Each rule of `eligible` exists because breaking it decides a sentence for a wrong reason."""
    assert verifier_eval.eligible(_item())
    assert not verifier_eval.eligible(_item(table=[["item", "value"], ["revenue", "n/a"]]))
    assert not verifier_eval.eligible(_item(answer=0.0))
    assert not verifier_eval.eligible(_item(answer=0.2, unit=Unit.percent))
    assert verifier_eval.eligible(_item(answer=20.0, unit=Unit.percent))
    assert not verifier_eval.eligible(_item(label="total of 1500 and the rest"))


def test_a_perturbation_that_the_prose_cannot_write_apart_is_refused() -> None:
    """Rule three: if (b) is written the way (a) is, it verifies by construction, saying nothing."""
    tiny = _item(answer=1e-9)
    assert verifier_eval._written(tiny.answer, tiny.unit) == verifier_eval._written(
        verifier_eval.perturb(tiny.answer, verifier_eval.perturbation_for(tiny.id), tiny.id),
        tiny.unit,
    )
    assert not verifier_eval.eligible(tiny)


# --- the sample ---------------------------------------------------------------------------------


def test_the_sample_is_the_same_under_the_same_seed_and_bounded_by_what_is_eligible(
    datasets: tuple[Path, Path],
) -> None:
    """The draw is `stable_hash([seed, id])`, so it reproduces in every process and version."""
    loaded = verifier_eval.load_finqa(datasets[0])
    drawn = verifier_eval.sample_items(loaded, 4)
    assert [item.id for item in drawn] == [
        item.id for item in verifier_eval.sample_items(loaded, 4)
    ]
    assert [item.id for item in verifier_eval.sample_items(loaded, 4, seed=1)] != [
        item.id for item in drawn
    ]
    assert len(verifier_eval.sample_items(loaded, 50)) == 10
    with pytest.raises(ValueError, match="not a sample"):
        verifier_eval.sample_items(loaded, 0)


# --- a run --------------------------------------------------------------------------------------


def test_a_run_over_both_datasets_scores_every_sentence_and_writes_its_summary(
    tmp_path: Path, datasets: tuple[Path, Path]
) -> None:
    """The acceptance of `04` section 6, over dataset-shaped items rather than fixtures."""
    report = verifier_eval.run_datasets(
        verifier_eval.fake_extractor(),
        tmp_path / "out",
        finqa=datasets[0],
        tatqa=datasets[1],
        n=5,
    )
    assert report.n_items == 10
    assert report.n_per_dataset == {"finqa": 5, "tatqa": 5}
    assert report.status_accuracy == {"verified": 1.0, "mismatch": 1.0, "unsupported": 1.0}
    assert set(report.by_dataset) == {"finqa", "tatqa"}
    assert report.by_dataset["finqa"].n_items == 5
    assert report.extraction_recall == 1.0
    assert report.failures == []
    assert report.n_llm_calls == 10 and report.n_reasks == 0 and report.reask_rate == 0.0
    assert sum(stat.n for stat in report.false_verified.values()) == 10
    assert all(stat.false_verified == 0 for stat in report.false_verified.values())
    written = json.loads((tmp_path / "out" / verifier_eval.EVAL_FILE).read_text(encoding="utf-8"))
    assert written["n_items"] == 10 and written["seed"] == verifier_eval.SEED
    assert (tmp_path / "out" / verifier_eval.TRACE_FILE).is_file()


def test_the_run_carries_the_note_that_the_sample_was_cut(
    tmp_path: Path, datasets: tuple[Path, Path]
) -> None:
    """D-194: the deviation travels with the numbers, in the file and in the printed lines."""
    report = verifier_eval.run_datasets(
        verifier_eval.fake_extractor(), tmp_path / "out", finqa=datasets[0], tatqa=datasets[1], n=2
    )
    assert report.sample_note == "n = 2 items per dataset."
    assert "50 items per dataset, 100 in total" in verifier_eval.SAMPLE_NOTE
    assert verifier_eval.LIVE_N == 50
    lines = verifier_eval.summary_lines(report)
    assert lines[0] == report.sample_note
    assert any(line.startswith("status accuracy:") for line in lines)
    assert any("is not counted as an error" in line for line in lines)
    assert any(line.startswith("re-asks:") for line in lines)


def test_a_dataset_with_no_eligible_item_is_refused_rather_than_sampled_empty(
    tmp_path: Path, items: list[Any], datasets: tuple[Path, Path]
) -> None:
    """An accuracy over nothing reads like a result, which is the whole reason for the guard."""
    empty = write_finqa(
        tmp_path / "empty.json",
        [],
        extra=[
            {
                "id": "A",
                "table": items[0].table,
                "qa": {"question": "q?", "answer": "no", "program": "greater(1, 2)"},
            }
        ],
    )
    with pytest.raises(ValueError, match="no eligible finqa item"):
        verifier_eval.run_datasets(
            verifier_eval.fake_extractor(), tmp_path / "out", finqa=empty, tatqa=datasets[1]
        )


def test_an_item_that_cannot_be_evaluated_is_kept_as_a_failure(
    tmp_path: Path, datasets: tuple[Path, Path]
) -> None:
    """One provider error must not cost the run its other items, nor shrink its denominator."""
    cassettes = tmp_path / "cassettes"
    cassettes.mkdir()
    report = verifier_eval.run_datasets(
        ReplayLLM(cassettes), tmp_path / "out", finqa=datasets[0], tatqa=datasets[1], n=2
    )
    assert report.n_items == 0
    assert [failure.dataset for failure in report.failures] == ["finqa"] * 2 + ["tatqa"] * 2
    assert all("no recorded call" in failure.error for failure in report.failures)
    assert report.status_accuracy == {"verified": 0.0, "mismatch": 0.0, "unsupported": 0.0}
    assert report.reask_rate == 0.0
    assert any("not evaluated" in line for line in verifier_eval.summary_lines(report))


def test_a_silent_extractor_scores_zero_recall_and_no_false_verification(
    tmp_path: Path, datasets: tuple[Path, Path]
) -> None:
    """The pre-pass owns the denominator (D-064), so omission cannot flatter the extractor."""
    report = verifier_eval.run_datasets(
        FakeLLM(default='{"claims": []}'),
        tmp_path / "out",
        finqa=datasets[0],
        tatqa=datasets[1],
        n=2,
    )
    assert report.extraction_recall == 0.0
    assert report.status_accuracy == {"verified": 0.0, "mismatch": 0.0, "unsupported": 0.0}
    assert report.false_verified_rate == 0.0
    assert all(
        sentence.status is ClaimStatus.unattributed
        for result in report.results
        for sentence in result.sentences
    )


# --- the two ways (b) can verify ----------------------------------------------------------------


def test_a_moved_citation_is_a_false_verification_and_not_a_tolerance_boundary(
    tmp_path: Path,
) -> None:
    """D-197. The matcher is deterministic, so this can only be the extractor's doing.

    The item's table carries a cell whose value *is* the perturbed answer, and the extractor
    attaches that cell's citation to the perturbed sentence. The claim then resolves, matches and
    comes out `verified` -- against the wrong artifact. Counting it as a tolerance boundary would
    file an extraction failure under "the tolerance working as designed".
    """
    identifier = "moved-01"
    kind = verifier_eval.perturbation_for(identifier)
    perturbed = verifier_eval.perturb(100.0, kind, identifier)
    item = _item(
        id=identifier,
        source_id=identifier,
        table=[["item", "value"], ["a near miss", repr(perturbed)]],
        answer=100.0,
    )
    store = verifier_eval.build_store(item, tmp_path / "store" / item.id)
    cell = store.artifact("table.r2.c2").citation()
    inner = verifier_eval.fake_extractor()

    def moved(prompt: str) -> str:
        payload = json.loads(inner.complete(prompt).text)
        for claim in payload["claims"]:
            if claim["line"] == 2 and claim["citation"]:
                claim["citation"] = cell
        return json.dumps(payload)

    result = verifier_eval.evaluate_item(item, FakeLLM(default=moved), tmp_path / "store")
    sentence = result.sentences[1]
    assert sentence.status is ClaimStatus.verified
    assert sentence.citation == cell
    assert sentence.false_verified and not sentence.tolerance_boundary
    assert not sentence.ok and not result.ok
    report = verifier_eval.summarise([result])
    assert report.false_verified[kind].false_verified == 1
    assert report.false_verified[kind].false_verified_rate == 1.0
    assert report.false_verified_rate == 1.0
    assert report.status_accuracy["mismatch"] == 0.0


def test_a_perturbation_inside_tolerance_is_reported_and_not_counted_as_an_error() -> None:
    """`04` section 6's one exemption, asserted on the arithmetic rather than on a live draw.

    Under D-069 the construction no longer produces one -- a perturbed number is written to the
    precision that catches it -- so the case is built here rather than fished for, and what is
    tested is that the counting keeps it out of the numerator *and* out of the denominator.
    """
    kinds = ("correct", "perturbed", "uncited")
    expected = (ClaimStatus.verified, ClaimStatus.mismatch, ClaimStatus.unsupported)
    statuses = (ClaimStatus.verified, ClaimStatus.verified, ClaimStatus.unsupported)
    sentences = [
        verifier_eval.SentenceResult(
            kind=kind,
            text=f"the {kind} sentence",
            value=0.0525 if kind == "perturbed" else 0.05,
            expected=want,
            status=status,
            artifact_value=0.05,
            tolerance=0.005,
            tolerance_boundary=kind == "perturbed",
        )
        for kind, want, status in zip(kinds, expected, statuses, strict=True)
    ]
    result = verifier_eval.ItemResult(
        item_id="boundary-01",
        perturbation="relative_up",
        perturbed_value=0.0525,
        sentences=sentences,
        dataset="finqa",
    )
    report = verifier_eval.summarise([result], sample_note="n = 1 items per dataset.")
    stat = report.false_verified["relative_up"]
    assert (stat.n, stat.tolerance_boundary, stat.false_verified, stat.other) == (1, 1, 0, 0)
    assert stat.false_verified_rate == 0.0 and report.false_verified_rate == 0.0
    assert report.status_accuracy["mismatch"] == 1.0
    assert report.tolerance_boundaries == ["boundary-01"]
