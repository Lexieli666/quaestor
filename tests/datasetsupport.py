"""Dataset-shaped files for the verifier component eval's offline tests.

`quaestor verifier-eval` reads FinQA's `dev.json` and TAT-QA's `tatqa_dataset_dev.json` from
paths a human passes on the command line. `CLAUDE.md` forbids a test from reading either: no row
of either dataset is committed, downloaded or opened here.

So the offline tests build files in the *shape* of each dataset, out of the ten items under
`tests/fixtures/verifier_eval/` that this repository wrote for itself in Phase 7, plus a handful
of rows written here to exercise a branch the ten do not reach -- an answer that is a word, a
`count` answer, a multi-span answer, a `$` answer with a thousands separator. What is being tested
is the loader's reading of a shape, which is exactly what a hand-built file can carry.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

__all__ = ["finqa_row", "tatqa_row", "written_answer", "write_finqa", "write_tatqa"]


def written_answer(answer: float, unit: str) -> str:
    """Write a gold answer the way FinQA writes one, with its sign or its symbol."""
    if unit == "percent":
        return f"{answer}%"
    if unit == "currency" and answer > 0:
        return f"$ {answer:,}"
    return f"{answer}"


def finqa_row(item: Any) -> dict[str, Any]:
    """Return one FinQA-shaped row built from a committed fixture item."""
    return {
        "id": f"TEST/{item.id}/page_1.pdf-1",
        "filename": f"TEST/{item.id}/page_1.pdf",
        "table": item.table,
        "qa": {
            "question": item.question,
            "answer": written_answer(item.answer, item.unit.value),
            "program": item.arithmetic,
            "exe_ans": item.answer,
        },
    }


def tatqa_row(item: Any, *, answer_type: str = "arithmetic") -> dict[str, Any]:
    """Return one TAT-QA-shaped table with a single question built from a fixture item."""
    return {
        "table": {"uid": f"table-{item.id}", "table": item.table},
        "paragraphs": [],
        "questions": [
            {
                "uid": item.id,
                "order": 1,
                "question": item.question,
                "answer": item.answer if answer_type == "arithmetic" else [f"{item.answer}"],
                "derivation": item.arithmetic if answer_type == "arithmetic" else "",
                "answer_type": answer_type,
                "answer_from": "table",
                "scale": "percent" if item.unit.value == "percent" else "",
                "rel_paragraphs": [],
                "req_comparison": False,
            }
        ],
    }


def write_finqa(path: Path, items: Sequence[Any], *, extra: Sequence[Any] = ()) -> Path:
    """Write a FinQA-shaped file of these items, plus any raw rows the caller wants in it."""
    rows: list[Any] = [finqa_row(item) for item in items]
    rows.extend(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def write_tatqa(path: Path, items: Sequence[Any], *, extra: Sequence[Any] = ()) -> Path:
    """Write a TAT-QA-shaped file of these items, plus any raw tables the caller wants in it."""
    rows: list[Any] = [tatqa_row(item) for item in items]
    rows.extend(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path
