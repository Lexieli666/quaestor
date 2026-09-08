"""The verifier component evaluation, offline half: ten fixture items, three sentences each.

`04-SEEDED-DEFECT-STUDY.md` section 6. The claim verifier is the differentiating component, so it
is evaluated on its own rather than only through a whole report. Each item is a small table, a
question and a gold answer with the arithmetic that produces it; the table's numeric cells and the
answer are loaded into an artifact store as scalars, and three report-style sentences are rendered:

(a) the gold answer, correctly cited -- expected `verified`;
(b) the gold answer perturbed by one of five perturbation types, cited to the same artifact --
    expected `mismatch`;
(c) the gold answer with no citation -- expected `unsupported`.

The extractor is the component under test; the matcher is deterministic, so a wrong status on (a)
or (c) is an extraction failure and a wrong status on (b) is either an extraction failure or the
tolerance doing its job. That second case is the number that matters and it is reported as what it
is: a +5% perturbation of a rate of 0.035 moves it by 0.00175, which is inside the 0.005 the claim
grammar allows, so the sentence is *supposed* to verify. It is counted as a **tolerance boundary**,
never as an error.

This file is the offline half only. The live half -- FinQA and TAT-QA, 150 items each, seed
20260901, cassettes committed -- is Phase 13, and nothing here downloads anything, calls a model or
reads a key: `fake_extractor` is a `FakeLLM` whose answer is computed from the prompt it was given.

The ten fixtures under `tests/fixtures/verifier_eval/` were written for this repository. No FinQA
or TAT-QA row is copied into it.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.hashing import stable_hash
from quaestor.llm import FakeLLM
from quaestor.llm.base import LLM
from quaestor.verifier import (
    ClaimStatus,
    ExtractedClaim,
    ExtractedClaims,
    Unit,
    extract,
    match_claims,
    numbered_lines,
    numeric_tokens,
    token_value,
)
from quaestor.vocab import ReportSection

__all__ = [
    "ANSWER_NAME",
    "FIXTURES",
    "PERTURBATIONS",
    "SEED",
    "EvalReport",
    "FixtureItem",
    "ItemResult",
    "SentenceResult",
    "build_store",
    "fake_extractor",
    "load_fixtures",
    "main",
    "perturb",
    "perturbation_for",
    "run_offline",
    "section_markdown",
]

FIXTURES: Final = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "verifier_eval"
"""Where the ten committed items live."""

SEED: Final = 20260901
"""The project's one seed, as `04` section 6 fixes it."""

ANSWER_NAME: Final = "answer"
"""The logical name the gold answer is stored under."""

CELL_PREFIX: Final = "table"
"""Cells are stored as `table.r<i>.c<j>`, one-based, the header row being row 1."""

PERTURBATIONS: Final = (
    "relative_up",
    "relative_down",
    "digit_transposition",
    "decimal_shift",
    "percent_ratio_confusion",
)
"""The five perturbation types. `04` section 6 writes the first two as one signed family."""

SECTION: Final = ReportSection.outcomes
"""Which section the rendered sentences claim to be in; any of the seven would do."""


class FixtureItem(BaseModel):
    """One committed evaluation item: a table, a question, a gold answer and its arithmetic.

    Attributes:
        id: The item id, which also seeds its perturbation.
        question: The question the answer answers.
        label: The noun phrase the rendered sentences use.
        table: The grid, header row included, cells as written.
        arithmetic: How the answer follows from the cells, for a human reading the fixture.
        answer: The gold answer.
        unit: The unit the answer is written in.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    question: str
    label: str
    table: list[list[str]]
    arithmetic: str
    answer: float
    unit: Unit


class SentenceResult(BaseModel):
    """What one of an item's three sentences produced.

    Attributes:
        kind: `correct`, `perturbed` or `uncited`.
        text: The sentence as rendered.
        value: The number written in it.
        expected: The status `04` section 6 expects.
        status: The status the verifier produced.
        artifact_value: What the citation resolved to, or `None`.
        tolerance: The tolerance the matcher applied.
        from_model: Whether the extractor returned this number, or the pre-pass had to.
        tolerance_boundary: Whether a perturbed sentence verified because the perturbation is
            inside tolerance, which is the tolerance doing its job and not an error.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: str
    text: str
    value: float
    expected: ClaimStatus
    status: ClaimStatus
    artifact_value: float | None = None
    tolerance: float = 0.0
    from_model: bool = True
    tolerance_boundary: bool = False

    @property
    def ok(self) -> bool:
        """Whether this sentence came out as expected, a tolerance boundary counting as expected."""
        return self.status is self.expected or self.tolerance_boundary


class ItemResult(BaseModel):
    """One item's three sentences and the perturbation it drew.

    Attributes:
        item_id: The item.
        perturbation: Which of the five types the seed chose.
        perturbed_value: The number the perturbed sentence wrote.
        sentences: The three results, in order.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str
    perturbation: str
    perturbed_value: float
    sentences: list[SentenceResult] = Field(min_length=3, max_length=3)

    @property
    def ok(self) -> bool:
        """Whether all three sentences came out as expected."""
        return all(sentence.ok for sentence in self.sentences)


class EvalReport(BaseModel):
    """The offline run's summary.

    Attributes:
        seed: The seed the perturbations were drawn with.
        n_items: How many items ran.
        results: One per item.
        status_accuracy: Accuracy per expected class, over the three sentence kinds.
        extraction_recall: The fraction of numbers the extractor returned itself, rather than
            leaving to the regex pre-pass.
        tolerance_boundaries: The items whose perturbation landed inside tolerance.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    seed: int
    n_items: int
    results: list[ItemResult] = Field(default_factory=list)
    status_accuracy: dict[str, float] = Field(default_factory=dict)
    extraction_recall: float = 0.0
    tolerance_boundaries: list[str] = Field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        """Return the report as a plain JSON object.

        Returns:
            The summary, ready to write beside a run.
        """
        return self.model_dump(mode="json")


def load_fixtures(directory: Path | str = FIXTURES) -> list[FixtureItem]:
    """Load every committed fixture item, in id order.

    Args:
        directory: Where the items live.

    Returns:
        The items.
    """
    return [
        FixtureItem.model_validate(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(Path(directory).glob("*.json"))
    ]


def build_store(item: FixtureItem, root: Path | str) -> ArtifactStore:
    """Load an item's numeric cells and its gold answer into an artifact store.

    Args:
        item: The fixture item.
        root: Where to put the store.

    Returns:
        The store: one scalar per numeric cell as `table.r<i>.c<j>`, one-based with the header row
        as row 1, and the gold answer as `answer`.
    """
    store = ArtifactStore(root)
    for row_number, row in enumerate(item.table, start=1):
        for column_number, cell in enumerate(row, start=1):
            try:
                value = float(cell.replace(",", ""))
            except ValueError:
                continue
            store.put(
                f"{CELL_PREFIX}.r{row_number}.c{column_number}",
                value,
                ArtifactKind.scalar,
                summary=f"{item.id} row {row_number} column {column_number}",
            )
    store.put(ANSWER_NAME, item.answer, ArtifactKind.scalar, summary=item.question)
    return store


def _draw(item_id: str, seed: int, modulus: int) -> int:
    """Draw one deterministic integer for an item, without a random-number generator.

    `stable_hash` is canonical JSON to SHA-256, so the draw is the same in every process and every
    Python version -- which `random.Random` is not guaranteed to be across versions.
    """
    return int(stable_hash([seed, item_id])[:8], 16) % modulus


def perturbation_for(item_id: str, seed: int = SEED) -> str:
    """Return the perturbation type this item draws.

    Args:
        item_id: The item.
        seed: The study's seed.

    Returns:
        One of :data:`PERTURBATIONS`.
    """
    return PERTURBATIONS[_draw(item_id, seed, len(PERTURBATIONS))]


def _transpose_digits(value: float) -> float | None:
    """Swap the last two adjacent distinct digits of a number's decimal form."""
    text = f"{value:g}"
    digits = list(text)
    for index in range(len(digits) - 1, 0, -1):
        left, right = digits[index - 1], digits[index]
        if left.isdigit() and right.isdigit() and left != right:
            digits[index - 1], digits[index] = right, left
            return float("".join(digits))
    return None


def perturb(value: float, kind: str, item_id: str, seed: int = SEED) -> float:
    """Perturb a gold answer by one of the five types.

    Args:
        value: The gold answer.
        kind: One of :data:`PERTURBATIONS`.
        item_id: The item, which sets the relative magnitude.
        seed: The study's seed.

    Returns:
        The perturbed value. A relative perturbation moves the value by 5 to 15 per cent, the
        magnitude drawn from the item and the seed; a digit transposition that has no two adjacent
        distinct digits to swap falls back to a relative perturbation, which is recorded as the
        type that ran.

    Raises:
        ValueError: `kind` is not one of the five.
    """
    if kind not in PERTURBATIONS:
        raise ValueError(f"{kind!r} is not one of {list(PERTURBATIONS)}")
    magnitude = 0.05 + _draw(item_id, seed, 11) / 100.0
    if kind == "relative_up":
        return value * (1.0 + magnitude)
    if kind == "relative_down":
        return value * (1.0 - magnitude)
    if kind == "decimal_shift":
        return value * 10.0
    if kind == "percent_ratio_confusion":
        return value * 100.0 if abs(value) <= 1.0 else value / 100.0
    transposed = _transpose_digits(value)
    return transposed if transposed is not None else value * (1.0 + magnitude)


def _written(value: float, unit: Unit) -> str:
    """Render a number the way a report would write it, with a per cent sign where one belongs."""
    text = f"{value:.4f}".rstrip("0").rstrip(".") if value != int(value) else f"{int(value)}"
    return f"{text}%" if unit is Unit.percent else text


def section_markdown(item: FixtureItem, store: ArtifactStore, seed: int = SEED) -> str:
    """Render an item's three sentences as one section of report prose.

    Args:
        item: The fixture item.
        store: The store built by :func:`build_store`, whose `answer` artifact is cited.
        seed: The study's seed, which chooses the perturbation.

    Returns:
        Three lines: the correctly cited answer, the perturbed answer cited to the same artifact,
        and the answer with no citation.
    """
    citation = store.artifact(ANSWER_NAME).citation()
    kind = perturbation_for(item.id, seed)
    perturbed = perturb(item.answer, kind, item.id, seed)
    return "\n".join(
        (
            f"The {item.label} is {_written(item.answer, item.unit)} {citation}.",
            f"On the same basis the {item.label} is {_written(perturbed, item.unit)} {citation}.",
            f"Stated without a citation, the {item.label} is {_written(item.answer, item.unit)}.",
        )
    )


def fake_extractor(unit: Unit = Unit.ratio) -> FakeLLM:
    """Return a `FakeLLM` that extracts the numbers of a prompt's prose deterministically.

    It reads the numbered prose out of the extraction prompt, takes every numeric token of every
    line, and attaches the citation that follows the token on that line together with the line
    number the prompt printed beside it (D-085). That is what a competent extractor
    does, so the offline half measures the *matcher* and the pre-pass end to end while the live
    half of Phase 13 measures a model.

    Args:
        unit: The unit to report for a token that carries no per cent sign.

    Returns:
        A fake provider, offline and deterministic.
    """

    def answer(prompt: str) -> str:
        prose = prompt.split("Prose:\n", 1)[-1].split("\n\nAnswer with one JSON object", 1)[0]
        claims = []
        for number, line in sorted(numbered_lines(prose).items()):
            if not line.strip():
                continue
            for offset, token in numeric_tokens(line):
                rest = line[offset + len(token) :].lstrip()
                citation = rest.split("]]", 1)[0] + "]]" if rest.startswith("[[art:") else None
                claims.append(
                    ExtractedClaim(
                        line=number,
                        value=token_value(token),
                        unit=Unit.percent if token.endswith("%") else unit,
                        citation=citation,
                    )
                )
        return ExtractedClaims(claims=claims).model_dump_json()

    return FakeLLM(default=answer)


def _claim_for(matches: Sequence[Any], value: float, line: str) -> Any:
    """Return the match for one number of a sentence that may hold several.

    A rendered sentence carries the answer and, often, an ordinal that is part of its label
    ("in year 2"). The sentence under test is the one whose value is the answer, so it is picked
    by value rather than by position.

    Raises:
        LookupError: The extractor and the pre-pass between them returned no claim for the number
            the sentence writes, which cannot happen while the pre-pass owns the denominator.
    """
    for match in matches:
        if abs(match.claim.value - value) < 1e-9:
            return match
    raise LookupError(f"no claim for {value:g} in {line!r}")


def evaluate_item(
    item: FixtureItem, llm: LLM, root: Path, seed: int = SEED, **params: Any
) -> ItemResult:
    """Run one item's three sentences through the extractor and the matcher.

    Args:
        item: The fixture item.
        llm: The provider under test. Offline, this is :func:`fake_extractor`.
        root: A directory to build the item's store in.
        seed: The study's seed.
        **params: Passed to the provider.

    Returns:
        The item's result.
    """
    store = build_store(item, root / item.id)
    markdown = section_markdown(item, store, seed)
    lines = markdown.splitlines()
    kind = perturbation_for(item.id, seed)
    perturbed = perturb(item.answer, kind, item.id, seed)

    extraction = extract(SECTION, markdown, llm, **params)
    matches = match_claims(extraction.claims, store, unattributed=extraction.unattributed_ids)
    by_line: dict[str, list[Any]] = {}
    for match in matches:
        by_line.setdefault(match.claim.text, []).append(match)

    expected = (ClaimStatus.verified, ClaimStatus.mismatch, ClaimStatus.unsupported)
    kinds = ("correct", "perturbed", "uncited")
    values = tuple(
        token_value(_written(number, item.unit)) for number in (item.answer, perturbed, item.answer)
    )
    sentences = []
    for line, sentence_kind, want, value in zip(lines, kinds, expected, values, strict=True):
        match = _claim_for(by_line[line], value, line)
        boundary = (
            sentence_kind == "perturbed"
            and match.claim.status is ClaimStatus.verified
            and match.claim.artifact_value is not None
        )
        sentences.append(
            SentenceResult(
                kind=sentence_kind,
                text=line,
                value=value,
                expected=want,
                status=match.claim.status,
                artifact_value=match.claim.artifact_value,
                tolerance=match.claim.tolerance,
                from_model=match.claim.id not in extraction.unattributed_ids,
                tolerance_boundary=boundary,
            )
        )
    return ItemResult(
        item_id=item.id, perturbation=kind, perturbed_value=perturbed, sentences=sentences
    )


def run_offline(
    llm: LLM,
    root: Path,
    *,
    items: Sequence[FixtureItem] | None = None,
    seed: int = SEED,
    **params: Any,
) -> EvalReport:
    """Run every fixture item and summarise.

    Args:
        llm: The provider under test.
        root: A directory to build the per-item stores in.
        items: The items, defaulting to the ten committed ones.
        seed: The study's seed.
        **params: Passed to the provider.

    Returns:
        The report: per-item results, status accuracy per expected class, extraction recall, and
        the items whose perturbation landed inside tolerance.
    """
    chosen = list(items if items is not None else load_fixtures())
    results = [evaluate_item(item, llm, root, seed, **params) for item in chosen]
    sentences = [sentence for result in results for sentence in result.sentences]
    accuracy = {}
    for want in (ClaimStatus.verified, ClaimStatus.mismatch, ClaimStatus.unsupported):
        of_class = [s for s in sentences if s.expected is want]
        accuracy[want.value] = (
            round(sum(1 for s in of_class if s.ok) / len(of_class), 4) if of_class else 0.0
        )
    return EvalReport(
        seed=seed,
        n_items=len(results),
        results=results,
        status_accuracy=accuracy,
        extraction_recall=(
            round(sum(1 for s in sentences if s.from_model) / len(sentences), 4)
            if sentences
            else 0.0
        ),
        tolerance_boundaries=[
            result.item_id
            for result in results
            if any(sentence.tolerance_boundary for sentence in result.sentences)
        ],
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the offline half and print its summary.

    The live half -- `quaestor verifier-eval --finqa ... --tatqa ...` over 300 sampled items with
    a real provider -- is Phase 13. This entry point never calls a model.

    Args:
        argv: Command-line arguments, or `None` for `sys.argv[1:]`.

    Returns:
        `0` when every item came out as expected, `1` otherwise.
    """
    parser = argparse.ArgumentParser(description="Verifier component eval, offline half.")
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--work", type=Path, required=True, help="scratch directory for stores")
    args = parser.parse_args(argv)

    report = run_offline(
        fake_extractor(), args.work, items=load_fixtures(args.fixtures), seed=args.seed
    )
    text = json.dumps(report.to_payload(), indent=2)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if all(result.ok for result in report.results) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
