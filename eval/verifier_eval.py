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

Phase 13 adds the live half in the same shape. `load_finqa` and `load_tatqa` read a dataset file
the operator names on the command line, keep the arithmetic-answer items, turn each into the same
`FixtureItem` the offline half uses, and `sample_items` draws the sample with the study's one seed.
`run_datasets` then runs both samples through the same extractor and matcher and writes
`verifier_eval.json`. The sample is **50 items per dataset, 100 in total**, and not the 150 per
dataset `04` section 6 fixes: the operator cut it to fit the study's budget (D-194), so the note
travels with the numbers -- it is a field of the report and a line of the command's output.

Nothing in this file downloads anything and nothing in it reads a dataset unless a caller hands it
a path: the offline half is `fake_extractor`, a `FakeLLM` whose answer is computed from the prompt
it was given, and the tests use only the ten committed fixtures. The live half is reached through
`quaestor verifier-eval --finqa FILE --tatqa FILE`, which refuses to run without both paths rather
than sampling nothing and reporting an accuracy over zero items.

The ten fixtures under `tests/fixtures/verifier_eval/` were written for this repository. No FinQA
or TAT-QA row is copied into it, and none is ever committed.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.errors import QuaestorError
from quaestor.hashing import stable_hash
from quaestor.llm import FakeLLM
from quaestor.llm.base import LLM
from quaestor.trace import EventType, TraceReader, TraceWriter
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
    "DATASETS",
    "EVAL_FILE",
    "FIXTURES",
    "LIVE_N",
    "PERTURBATIONS",
    "SAMPLE_NOTE",
    "SEED",
    "STORES_DIRNAME",
    "TRACE_FILE",
    "DatasetStat",
    "EvalReport",
    "FixtureItem",
    "ItemFailure",
    "ItemResult",
    "PerturbationStat",
    "SentenceResult",
    "build_store",
    "cell_value",
    "eligible",
    "evaluate_item",
    "fake_extractor",
    "label_for",
    "load_dataset",
    "load_finqa",
    "load_fixtures",
    "load_tatqa",
    "main",
    "perturb",
    "perturbation_for",
    "run_datasets",
    "run_items",
    "run_offline",
    "sample_items",
    "section_markdown",
    "summarise",
    "summary_lines",
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

DATASETS: Final = ("finqa", "tatqa")
"""The two public datasets of `04` section 6, in the order the command reads them."""

LIVE_N: Final = 50
"""How many items are drawn from each dataset.

`04` section 6 fixes 150 per dataset. The operator cut the sample to 50 per dataset -- 100 items
in total -- because the study's budget was cut, and decided it before the first live call rather
than after seeing a number (D-194). :data:`SAMPLE_NOTE` travels with every figure that follows.
"""

SAMPLE_NOTE: Final = (
    "n = 50 items per dataset, 100 in total. 04-SEEDED-DEFECT-STUDY.md section 6 fixes 150 per "
    "dataset; the operator cut the sample to fit the study's budget (D-194). Every figure in this "
    "report is over those 100 items and their 300 sentences."
)
"""The deviation, in the report and in the command's own output, beside the numbers it qualifies."""

EVAL_FILE: Final = "verifier_eval.json"
"""What a live run writes under its ``--out`` directory."""

TRACE_FILE: Final = "trace.jsonl"
"""The run's trace, which is where the re-ask rate and the cost are counted from."""

STORES_DIRNAME: Final = "stores"
"""Where the per-item artifact stores go under ``--out``."""


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
        dataset: Which public dataset the item was read from, or `None` for a committed fixture.
        source_id: The row's own identifier in that dataset, which `id` slugs into a path, or
            `None` for a committed fixture. Neither field is written into a committed fixture:
            they are how a live run says where an item came from without copying the row.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    question: str
    label: str
    table: list[list[str]]
    arithmetic: str
    answer: float
    unit: Unit
    dataset: str | None = None
    source_id: str | None = None


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
        citation: The citation the matched claim carried, or `None`.
        tolerance_boundary: Whether a perturbed sentence verified **against the answer artifact**
            because the perturbation is inside tolerance, which is the tolerance doing its job and
            not an error.
        false_verified: Whether a perturbed sentence verified for any other reason -- a citation
            the extractor moved, invented or attached to a cell that happens to carry the
            perturbed number. The matcher is deterministic, so this is an extraction failure and
            it is the one thing on (b) that is counted as an error (D-197).
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
    citation: str | None = None
    tolerance_boundary: bool = False
    false_verified: bool = False

    @property
    def ok(self) -> bool:
        """Whether this sentence came out as expected, a tolerance boundary counting as expected."""
        return self.status is self.expected or self.tolerance_boundary


class ItemResult(BaseModel):
    """One item's three sentences and the perturbation it drew.

    Attributes:
        item_id: The item.
        dataset: Which dataset it was drawn from, or `None` for a committed fixture.
        source_id: The row's identifier in that dataset, or `None` for a committed fixture.
        perturbation: Which of the five types the seed chose.
        perturbed_value: The number the perturbed sentence wrote.
        sentences: The three results, in order.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str
    perturbation: str
    perturbed_value: float
    sentences: list[SentenceResult] = Field(min_length=3, max_length=3)
    dataset: str | None = None
    source_id: str | None = None

    @property
    def ok(self) -> bool:
        """Whether all three sentences came out as expected."""
        return all(sentence.ok for sentence in self.sentences)


class PerturbationStat(BaseModel):
    """What one perturbation type did to the perturbed sentences that drew it.

    Attributes:
        perturbation: The type.
        n: How many items drew it.
        mismatch: How many were caught, which is what `04` section 6 expects of (b).
        tolerance_boundary: How many verified against the answer artifact because the perturbation
            is inside the tolerance the claim grammar allows. `04` section 6 is explicit that this
            is not an error: a sentence whose number still rounds to the artifact at the precision
            the prose wrote is *supposed* to verify, so it is reported and not counted.
        false_verified: How many verified for any other reason, which is an extraction failure.
        other: How many came out neither verified nor mismatch -- unsupported, dangling or
            unattributed -- each of which is also an extraction failure, of a different shape.
        false_verified_rate: `false_verified` over the sentences that could have been caught,
            which is `n` less the tolerance boundaries. `0.0` when every item of this type landed
            inside tolerance, with `n == tolerance_boundary` saying so.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    perturbation: str
    n: int
    mismatch: int
    tolerance_boundary: int
    false_verified: int
    other: int
    false_verified_rate: float


class DatasetStat(BaseModel):
    """One dataset's half of the run, so that a single bad half is visible.

    Attributes:
        dataset: `finqa`, `tatqa`, or `fixtures` for the offline half.
        n_items: How many items of it ran.
        status_accuracy: Accuracy per expected class over this dataset's sentences.
        extraction_recall: This dataset's extraction recall.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset: str
    n_items: int
    status_accuracy: dict[str, float] = Field(default_factory=dict)
    extraction_recall: float = 0.0


class ItemFailure(BaseModel):
    """An item that could not be evaluated at all, kept rather than dropped.

    A live run of a hundred items must not lose its other ninety-nine to one model answer that did
    not validate twice, and it must not report an accuracy that quietly excludes the item either.

    Attributes:
        item_id: The item.
        dataset: Which dataset it came from.
        error: What went wrong, as the exception wrote it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str
    dataset: str | None = None
    error: str = ""


class EvalReport(BaseModel):
    """A run's summary, offline or live.

    Attributes:
        seed: The seed the perturbations were drawn with.
        n_items: How many items ran.
        results: One per item.
        status_accuracy: Accuracy per expected class, over the three sentence kinds.
        extraction_recall: The fraction of numbers the extractor returned itself, rather than
            leaving to the regex pre-pass.
        tolerance_boundaries: The items whose perturbation landed inside tolerance.
        sample_note: How the sample was drawn and how it departs from the protocol, empty for the
            offline half. It is a field rather than a line of prose somewhere else so that a
            figure quoted out of this file carries its own qualification (D-194).
        n_per_dataset: How many items each dataset contributed.
        by_dataset: The same accuracy, per dataset.
        false_verified: :class:`PerturbationStat` per perturbation type.
        false_verified_rate: The same over every perturbed sentence of the run.
        n_llm_calls: How many model calls the extractions made, from the trace.
        n_reasks: How many of those were retries of an answer that did not validate.
        reask_rate: `n_reasks` over the number of extractions asked for, which is one per item.
        cost_usd: What the run's calls cost, when the provider priced them.
        failures: The items that could not be evaluated.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    seed: int
    n_items: int
    results: list[ItemResult] = Field(default_factory=list)
    status_accuracy: dict[str, float] = Field(default_factory=dict)
    extraction_recall: float = 0.0
    tolerance_boundaries: list[str] = Field(default_factory=list)
    sample_note: str = ""
    n_per_dataset: dict[str, int] = Field(default_factory=dict)
    by_dataset: dict[str, DatasetStat] = Field(default_factory=dict)
    false_verified: dict[str, PerturbationStat] = Field(default_factory=dict)
    false_verified_rate: float = 0.0
    n_llm_calls: int = 0
    n_reasks: int = 0
    reask_rate: float = 0.0
    cost_usd: float = 0.0
    failures: list[ItemFailure] = Field(default_factory=list)

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
            value = cell_value(cell)
            if value is None:
                continue
            store.put(
                f"{CELL_PREFIX}.r{row_number}.c{column_number}",
                value,
                ArtifactKind.scalar,
                summary=f"{item.id} row {row_number} column {column_number}",
            )
    store.put(ANSWER_NAME, item.answer, ArtifactKind.scalar, summary=item.question)
    return store


def cell_value(cell: str) -> float | None:
    """Return a table cell as a number, or `None` when it is not one.

    A thousands separator, a currency symbol and the surrounding whitespace are removed, because a
    published table writes ``$  1,452.4`` for a number a store holds as ``1452.4``. A per cent sign
    is **not**: a cell written ``4.5%`` could go into the store as ``4.5`` or as ``0.045`` and
    nothing in the cell says which, so it is left out rather than guessed at. The rejected
    alternative was storing it on the 0-100 scale, which would make a cell and the answer computed
    from it disagree by two orders of magnitude for no stated reason.

    Args:
        cell: The cell as the dataset wrote it.

    Returns:
        The number, or `None`.
    """
    text = cell.replace(",", "").replace("$", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


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


_CITATION_RE: Final = re.compile(r"\[\[[^\]]*\]\]")
"""Any double-bracket citation, whose hash and logical name are not claims (D-015)."""


def _blank(match: re.Match[str]) -> str:
    """Replace a matched region with spaces, keeping every offset after it where it was."""
    return " " * len(match.group(0))


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
    line **outside a citation**, and attaches the citation that follows the token on that line
    together with the line number the prompt printed beside it (D-085). That is what a competent
    extractor does, so the offline half measures the *matcher* and the pre-pass end to end while
    the live half of Phase 13 measures a model. The citation is blanked with spaces rather than
    cut, so every offset still points where it did: ``[[art:2e30351e:answer]]`` holds the token
    ``2e30351`` under the exponent-aware tokenizer of D-099, and a fake that claimed it would be
    offering the matcher a number no report wrote.

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
            for offset, token in numeric_tokens(_CITATION_RE.sub(_blank, line)):
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
    item: FixtureItem,
    llm: LLM,
    root: Path,
    seed: int = SEED,
    *,
    trace: TraceWriter | None = None,
    **params: Any,
) -> ItemResult:
    """Run one item's three sentences through the extractor and the matcher.

    Args:
        item: The fixture item.
        llm: The provider under test. Offline, this is :func:`fake_extractor`.
        root: A directory to build the item's store in.
        seed: The study's seed.
        trace: The run's trace, so that the re-ask rate and the cost are counted from the same
            ``llm_call`` events a validation writes rather than from a second tally.
        **params: Passed to the provider.

    Returns:
        The item's result.

    Raises:
        LookupError: The extractor and the pre-pass between them returned no claim for a number
            one of the three sentences writes.
    """
    store = build_store(item, root / item.id)
    markdown = section_markdown(item, store, seed)
    lines = markdown.splitlines()
    kind = perturbation_for(item.id, seed)
    perturbed = perturb(item.answer, kind, item.id, seed)
    answer_citation = store.artifact(ANSWER_NAME).citation()

    extraction = extract(SECTION, markdown, llm, trace=trace, **params)
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
        verified_perturbation = (
            sentence_kind == "perturbed" and match.claim.status is ClaimStatus.verified
        )
        boundary = (
            verified_perturbation
            and match.claim.citation == answer_citation
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
                citation=match.claim.citation,
                tolerance_boundary=boundary,
                false_verified=verified_perturbation and not boundary,
            )
        )
    return ItemResult(
        item_id=item.id,
        perturbation=kind,
        perturbed_value=perturbed,
        sentences=sentences,
        dataset=item.dataset,
        source_id=item.source_id,
    )


def run_items(
    llm: LLM,
    root: Path,
    items: Sequence[FixtureItem],
    *,
    seed: int = SEED,
    trace: TraceWriter | None = None,
    **params: Any,
) -> tuple[list[ItemResult], list[ItemFailure]]:
    """Run every item through :func:`evaluate_item`, keeping what failed rather than dropping it.

    Args:
        llm: The provider under test.
        root: A directory to build the per-item stores in.
        items: The items.
        seed: The study's seed.
        trace: The run's trace.
        **params: Passed to the provider.

    Returns:
        The results, and one :class:`ItemFailure` per item that could not be evaluated. A run of a
        hundred live items does not lose the other ninety-nine to a single model answer that did
        not validate in two attempts, and it does not silently shrink its denominator either.
    """
    results: list[ItemResult] = []
    failures: list[ItemFailure] = []
    for item in items:
        try:
            results.append(evaluate_item(item, llm, root, seed, trace=trace, **params))
        except (QuaestorError, LookupError, OSError) as exc:
            failures.append(ItemFailure(item_id=item.id, dataset=item.dataset, error=str(exc)))
    return results, failures


def _accuracy(sentences: Sequence[SentenceResult]) -> dict[str, float]:
    """Return accuracy per expected class over one set of sentences."""
    accuracy = {}
    for want in (ClaimStatus.verified, ClaimStatus.mismatch, ClaimStatus.unsupported):
        of_class = [sentence for sentence in sentences if sentence.expected is want]
        accuracy[want.value] = (
            round(sum(1 for sentence in of_class if sentence.ok) / len(of_class), 4)
            if of_class
            else 0.0
        )
    return accuracy


def _recall(sentences: Sequence[SentenceResult]) -> float:
    """Return the share of numbers the extractor returned itself, the pre-pass owning the rest."""
    if not sentences:
        return 0.0
    return round(sum(1 for sentence in sentences if sentence.from_model) / len(sentences), 4)


def _perturbation_stats(results: Sequence[ItemResult]) -> dict[str, PerturbationStat]:
    """Return one :class:`PerturbationStat` per perturbation type that was drawn."""
    stats = {}
    for kind in PERTURBATIONS:
        drew = [result for result in results if result.perturbation == kind]
        if not drew:
            continue
        sentences = [result.sentences[1] for result in drew]
        boundary = sum(1 for sentence in sentences if sentence.tolerance_boundary)
        false_verified = sum(1 for sentence in sentences if sentence.false_verified)
        mismatch = sum(1 for sentence in sentences if sentence.status is ClaimStatus.mismatch)
        catchable = len(sentences) - boundary
        stats[kind] = PerturbationStat(
            perturbation=kind,
            n=len(sentences),
            mismatch=mismatch,
            tolerance_boundary=boundary,
            false_verified=false_verified,
            other=len(sentences) - boundary - false_verified - mismatch,
            false_verified_rate=round(false_verified / catchable, 4) if catchable else 0.0,
        )
    return stats


def _call_counts(trace_path: Path | None) -> tuple[int, int, float]:
    """Return the run's model calls, its re-asks and its notional cost, read from the trace.

    The numbers come from the ``llm_call`` events :func:`~quaestor.llm.structured.structured`
    writes, which is the same place a validation's cost line comes from, rather than from a tally
    kept here that could disagree with it.
    """
    if trace_path is None or not Path(trace_path).is_file():
        return 0, 0, 0.0
    events = TraceReader(trace_path).events(EventType.llm_call)
    reasks = sum(1 for event in events if event.payload.get("purpose") == "reask")
    cost = sum(float(event.payload.get("cost_usd") or 0.0) for event in events)
    return len(events), reasks, round(cost, 6)


def summarise(
    results: Sequence[ItemResult],
    *,
    seed: int = SEED,
    sample_note: str = "",
    n_per_dataset: Mapping[str, int] | None = None,
    trace_path: Path | None = None,
    failures: Iterable[ItemFailure] = (),
) -> EvalReport:
    """Summarise a run: status accuracy, false-verified rates, extraction recall, re-asks.

    Args:
        results: The per-item results.
        seed: The study's seed.
        sample_note: How the sample was drawn and how it departs from the protocol.
        n_per_dataset: How many items each dataset contributed, for a live run.
        trace_path: The run's trace, which the call counts and the cost are read from.
        failures: The items that could not be evaluated.

    Returns:
        The report. A perturbed sentence that verified against the answer artifact counts as a
        **tolerance boundary** and not as an error, which is `04` section 6's rule and the reason
        the report carries both numbers separately.
    """
    sentences = [sentence for result in results for sentence in result.sentences]
    perturbed = [result.sentences[1] for result in results]
    boundaries = sum(1 for sentence in perturbed if sentence.tolerance_boundary)
    catchable = len(perturbed) - boundaries
    n_calls, reasks, cost = _call_counts(trace_path)
    by_dataset = {}
    for name in sorted({result.dataset or "fixtures" for result in results}):
        of_dataset = [result for result in results if (result.dataset or "fixtures") == name]
        its_sentences = [sentence for result in of_dataset for sentence in result.sentences]
        by_dataset[name] = DatasetStat(
            dataset=name,
            n_items=len(of_dataset),
            status_accuracy=_accuracy(its_sentences),
            extraction_recall=_recall(its_sentences),
        )
    return EvalReport(
        seed=seed,
        n_items=len(results),
        results=list(results),
        status_accuracy=_accuracy(sentences),
        extraction_recall=_recall(sentences),
        tolerance_boundaries=[
            result.item_id
            for result in results
            if any(sentence.tolerance_boundary for sentence in result.sentences)
        ],
        sample_note=sample_note,
        n_per_dataset=dict(n_per_dataset or {}),
        by_dataset=by_dataset,
        false_verified=_perturbation_stats(results),
        false_verified_rate=(
            round(sum(1 for sentence in perturbed if sentence.false_verified) / catchable, 4)
            if catchable
            else 0.0
        ),
        n_llm_calls=n_calls,
        n_reasks=reasks,
        reask_rate=round(reasks / len(results), 4) if results else 0.0,
        cost_usd=cost,
        failures=list(failures),
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
    results, failures = run_items(llm, root, chosen, seed=seed, **params)
    return summarise(results, seed=seed, failures=failures)


# --- the live half: FinQA and TAT-QA ----------------------------------------------------------

_SLUG_RE: Final = re.compile(r"[^A-Za-z0-9._-]+")
"""Everything a dataset's own identifier may hold that a directory name may not."""

_LEAD_RE: Final = (
    re.compile(r"^what\s+(?:is|was|are|were)\s+(?:the\s+)?", re.IGNORECASE),
    re.compile(r"^how\s+much\s+(?:is|was|are|were)\s+(?:the\s+)?", re.IGNORECASE),
    re.compile(r"^how\s+many\s+", re.IGNORECASE),
)
"""The question stems that leave a noun phrase behind when they are removed."""

_VERB_RE: Final = re.compile(
    r"^(?:did|do|does|was|were|is|are|has|have|had|will|would|should|could|can)\b",
    re.IGNORECASE,
)
"""What a stripped question must not begin with, or the sentence built from it is not English."""

_ANSWER_RE: Final = re.compile(r"^(?P<sign>-?)\s*\$?\s*(?P<body>[\d,]*\.?\d+)\s*(?P<pct>%?)$")
"""A gold answer as it is written: an optional sign, an optional ``$``, an optional ``%``."""


def _slug(text: str) -> str:
    """Return an identifier that is safe as one path segment."""
    return _SLUG_RE.sub("_", text).strip("_")[:96]


def label_for(question: str) -> str:
    """Return the noun phrase the three sentences are built around.

    A question whose stem strips cleanly leaves a noun phrase -- "what is the average payment
    volume per transaction" becomes "average payment volume per transaction", and the sentence
    reads as a report sentence. A question that does not, because what is left begins with a verb
    or because it has no stem this function knows, is quoted instead, so that the sentence reads
    "the answer to ... is 300". The rejected alternative was a parser that rewrote any question
    into a noun phrase, which would put this file in the business of generating English and make
    the extractor's score depend on how well it did.

    Args:
        question: The dataset's question.

    Returns:
        The label.
    """
    text = " ".join(question.split()).rstrip("?").strip()
    for pattern in _LEAD_RE:
        stripped = pattern.sub("", text, count=1).strip()
        if stripped and stripped != text and not _VERB_RE.match(stripped):
            return stripped[0].lower() + stripped[1:]
    return f'answer to "{text}"'


def _parse_answer(text: str) -> tuple[float, Unit] | None:
    """Return a written gold answer as a number and the unit it is written in, or `None`.

    FinQA writes its answers as prose does -- ``127.40``, ``93.5%``, ``$ 40444920``, ``-1.9`` --
    and a row whose answer is a word, a sentence or an escaped newline is not an arithmetic item
    and is dropped here rather than coerced.
    """
    match = _ANSWER_RE.match(" ".join(text.split()))
    if match is None:
        return None
    body = match.group("body").replace(",", "")
    try:
        value = float(f"{match.group('sign')}{body}")
    except ValueError:  # pragma: no cover - the pattern admits nothing float() refuses
        return None
    if match.group("pct"):
        return value, Unit.percent
    return value, Unit.currency if "$" in text else Unit.ratio


def eligible(item: FixtureItem, seed: int = SEED) -> bool:
    """Whether an item can carry the three sentences of `04` section 6 without confounding them.

    Five rules (D-196), each of which exists because breaking it would make a sentence come out
    right or wrong for a reason that is not the extractor's doing:

    1. The table must hold at least one number, or there is nothing but the answer in the store
       and a moved citation has nowhere to land.
    2. The answer must not be zero: every relative perturbation of zero is zero, so (b) would be
       (a) and would verify by construction.
    3. The perturbed answer must not be *written* the way the gold answer is written, for the same
       reason one decimal place further out.
    4. A percentage of at most one is excluded. The matcher normalises a per cent against an
       artifact in the unit interval, so an answer of ``0.2%`` stored as ``0.2`` would be compared
       as ``0.002`` and (a) would come out a mismatch; the fixtures' convention is that a per cent
       is stored as the prose writes it, and this rule is what keeps it true.
    5. The label must not itself write the gold or the perturbed number, which would put two
       claims of the same value on one line and make which one carries the citation a coin toss.

    Args:
        item: The candidate.
        seed: The study's seed, which fixes the perturbation.

    Returns:
        Whether to keep it.
    """
    if not any(cell_value(cell) is not None for row in item.table for cell in row):
        return False
    if item.answer == 0.0:
        return False
    perturbed = perturb(item.answer, perturbation_for(item.id, seed), item.id, seed)
    written_answer = _written(item.answer, item.unit)
    if _written(perturbed, item.unit) == written_answer:
        return False
    if item.unit is Unit.percent and abs(item.answer) <= 1.0:
        return False
    values = {token_value(written_answer), token_value(_written(perturbed, item.unit))}
    return not any(token_value(token) in values for _, token in numeric_tokens(item.label))


def load_finqa(path: Path | str, *, seed: int = SEED) -> list[FixtureItem]:
    """Read FinQA's `dev.json` and return its eligible arithmetic-answer items.

    An item is arithmetic-answer when the row carries a program -- the FinQA annotation of how the
    answer is computed from the table -- and its gold answer parses as a number. The rows whose
    answer is ``yes``, ``no`` or a sentence are the dataset's non-arithmetic half and are dropped.

    Args:
        path: The dataset file, which the operator names on the command line. It is never
            committed and no test reads it.
        seed: The study's seed, which :func:`eligible` needs.

    Returns:
        The items, in file order, each with its dataset and its row id recorded.

    Raises:
        ValueError: The file is not a JSON list of rows.
    """
    items = []
    for row in _rows(path):
        qa = row.get("qa") if isinstance(row, Mapping) else None
        if not isinstance(qa, Mapping) or not qa.get("program") or not qa.get("question"):
            continue
        parsed = _parse_answer(str(qa.get("answer", "")))
        table = row.get("table")
        if parsed is None or not _is_grid(table):
            continue
        source_id = str(row.get("id", ""))
        item = FixtureItem(
            id=f"finqa-{_slug(source_id)}",
            question=str(qa["question"]),
            label=label_for(str(qa["question"])),
            table=[[str(cell) for cell in line] for line in table],
            arithmetic=str(qa["program"]),
            answer=parsed[0],
            unit=parsed[1],
            dataset="finqa",
            source_id=source_id,
        )
        if eligible(item, seed):
            items.append(item)
    return items


def load_tatqa(path: Path | str, *, seed: int = SEED) -> list[FixtureItem]:
    """Read TAT-QA's `tatqa_dataset_dev.json` and return its eligible numeric-answer questions.

    `04` section 6 asks for ``answer_type ∈ {arithmetic, span-number}``. The released file spells
    only ``arithmetic``, ``span``, ``multi-span`` and ``count``: a *span-number* is a ``span``
    answer that is a single number, which is what this function keeps, and a ``count`` answer is
    not one -- it is the number of spans, not a quantity read out of the table (D-195). A question
    whose ``scale`` is ``percent`` is a percentage and is written with its sign; the other scale
    words -- thousand, million, billion -- are the table's units and are dropped, the number being
    written and stored exactly as the dataset writes it.

    Args:
        path: The dataset file, named on the command line, never committed, never read by a test.
        seed: The study's seed, which :func:`eligible` needs.

    Returns:
        The items, in file order.

    Raises:
        ValueError: The file is not a JSON list of tables.
    """
    items = []
    for row in _rows(path):
        table = row.get("table") if isinstance(row, Mapping) else None
        grid = table.get("table") if isinstance(table, Mapping) else None
        if not _is_grid(grid):
            continue
        for question in row.get("questions", []):
            parsed = _tatqa_answer(question)
            if parsed is None:
                continue
            source_id = str(question.get("uid", ""))
            item = FixtureItem(
                id=f"tatqa-{_slug(source_id)}",
                question=str(question["question"]),
                label=label_for(str(question["question"])),
                table=[[str(cell) for cell in line] for line in grid],
                arithmetic=str(question.get("derivation") or f"{question['answer_type']} answer"),
                answer=parsed[0],
                unit=parsed[1],
                dataset="tatqa",
                source_id=source_id,
            )
            if eligible(item, seed):
                items.append(item)
    return items


def _tatqa_answer(question: Any) -> tuple[float, Unit] | None:
    """Return one TAT-QA question's gold answer, or `None` when it is not a numeric one."""
    if not isinstance(question, Mapping) or not question.get("question"):
        return None
    kind = question.get("answer_type")
    if kind not in ("arithmetic", "span"):
        return None
    raw = question.get("answer")
    if isinstance(raw, list):
        if len(raw) != 1:
            return None
        raw = raw[0]
    if isinstance(raw, bool) or raw is None:
        return None
    parsed = (float(raw), Unit.ratio) if isinstance(raw, (int, float)) else _parse_answer(str(raw))
    if parsed is None:
        return None
    value, unit = parsed
    if question.get("scale") == "percent":
        unit = Unit.percent
    return value, unit


def _is_grid(table: Any) -> bool:
    """Whether a row's table is a grid of at least two rows, the header row being the first."""
    return (
        isinstance(table, list)
        and len(table) >= 2
        and all(isinstance(line, list) for line in table)
    )


def _rows(path: Path | str) -> list[Any]:
    """Read one dataset file into its list of rows.

    Raises:
        ValueError: The file is not a JSON list, which is the shape both datasets ship in.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(
            f"{path} is a JSON {type(payload).__name__} and not the list of rows FinQA and TAT-QA "
            f"both ship; see data/README.md for which file each dataset's dev split is"
        )
    return payload


def load_dataset(name: str, path: Path | str, *, seed: int = SEED) -> list[FixtureItem]:
    """Load one of the two datasets by name.

    Args:
        name: ``finqa`` or ``tatqa``.
        path: The dataset file.
        seed: The study's seed.

    Returns:
        The eligible items.

    Raises:
        ValueError: The name is not one of the two.
    """
    if name == "finqa":
        return load_finqa(path, seed=seed)
    if name == "tatqa":
        return load_tatqa(path, seed=seed)
    raise ValueError(f"{name!r} is not one of {list(DATASETS)}")


def sample_items(
    items: Sequence[FixtureItem], n: int = LIVE_N, *, seed: int = SEED
) -> list[FixtureItem]:
    """Draw `n` items deterministically.

    The draw orders the candidates by `stable_hash([seed, id])` and takes the first `n`, which is
    the same primitive the perturbations use: canonical JSON to SHA-256, identical in every process
    and every Python version, which `random.Random` does not promise across versions.

    Args:
        items: The eligible items.
        n: How many to draw. Fewer are returned when fewer are eligible, and the caller reports
            the number it actually got rather than the number it asked for.
        seed: The study's seed.

    Returns:
        The sample, in the drawn order.

    Raises:
        ValueError: `n` is not positive.
    """
    if n <= 0:
        raise ValueError(f"a sample of {n} items is not a sample")
    return sorted(items, key=lambda item: stable_hash([seed, item.id]))[:n]


def run_datasets(
    llm: LLM,
    out: Path | str,
    *,
    finqa: Path | str,
    tatqa: Path | str,
    n: int = LIVE_N,
    seed: int = SEED,
    **params: Any,
) -> EvalReport:
    """Run the component eval over both datasets and write `verifier_eval.json`.

    Args:
        llm: The provider under test -- the extractor is the one model step of the verifier.
        out: Where the summary, the trace and the per-item stores go.
        finqa: FinQA's `dev.json`, named on the command line.
        tatqa: TAT-QA's `tatqa_dataset_dev.json`, named the same way.
        n: How many items to draw from each dataset; :data:`LIVE_N` by default.
        seed: The study's seed.
        **params: Passed to the provider, such as ``model``.

    Returns:
        The report, which has also been written to `out/verifier_eval.json`.

    Raises:
        ValueError: A dataset yielded no eligible item, which is the one thing a component eval
            must not do quietly: an accuracy over an empty sample is `0.0` and reads like a result.
    """
    root = Path(out)
    root.mkdir(parents=True, exist_ok=True)
    trace = TraceWriter(
        root / TRACE_FILE,
        run_id=stable_hash({"verifier_eval": sorted(DATASETS), "n": n, "seed": seed}),
    )
    items: list[FixtureItem] = []
    counts: dict[str, int] = {}
    for name, path in zip(DATASETS, (finqa, tatqa), strict=True):
        drawn = sample_items(load_dataset(name, path, seed=seed), n, seed=seed)
        if not drawn:
            raise ValueError(
                f"no eligible {name} item in {path}: nothing was sampled, so there is nothing to "
                f"report; check that the file is the dataset's dev split"
            )
        counts[name] = len(drawn)
        items.extend(drawn)
    results, failures = run_items(
        llm, root / STORES_DIRNAME, items, seed=seed, trace=trace, **params
    )
    report = summarise(
        results,
        seed=seed,
        sample_note=SAMPLE_NOTE if n == LIVE_N else f"n = {n} items per dataset.",
        n_per_dataset=counts,
        trace_path=root / TRACE_FILE,
        failures=failures,
    )
    (root / EVAL_FILE).write_text(
        json.dumps(report.to_payload(), indent=2) + "\n", encoding="utf-8"
    )
    return report


def summary_lines(report: EvalReport) -> list[str]:
    """Return the lines `quaestor verifier-eval` prints, the sample note first.

    The note leads because every number under it is over a hundred items rather than the three
    hundred `04` section 6 planned, and a figure read off a terminal carries no footnote (D-194).

    Args:
        report: A finished run.

    Returns:
        The lines, in order.
    """
    lines = [report.sample_note] if report.sample_note else []
    for name, count in report.n_per_dataset.items():
        lines.append(f"{name}: {count} item(s)")
    accuracy = ", ".join(f"{name} {value:.4f}" for name, value in report.status_accuracy.items())
    lines.append(f"status accuracy: {accuracy}")
    for kind, stat in report.false_verified.items():
        lines.append(
            f"false-verified on {kind}: {stat.false_verified}/{stat.n - stat.tolerance_boundary} "
            f"({stat.false_verified_rate:.4f}); {stat.tolerance_boundary} of {stat.n} inside "
            f"tolerance, which is the tolerance working and is not counted as an error"
        )
    lines.append(f"extraction recall: {report.extraction_recall:.4f}")
    lines.append(
        f"re-asks: {report.n_reasks} over {report.n_items} extraction(s) "
        f"({report.reask_rate:.4f}); {report.n_llm_calls} model call(s), ${report.cost_usd:.4f}"
    )
    for failure in report.failures:
        lines.append(f"{failure.item_id}: not evaluated -- {failure.error}")
    return lines


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
