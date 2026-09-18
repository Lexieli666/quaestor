"""Phase 12: the study harness -- chunks, the ledger that resumes them, and the cost ceiling.

`docs/STUDY.md` section 4. Every test here is offline: `rules_only` makes no model call at all,
and the two configurations that do are driven by `FakeLLM`, whose `cost_usd` is whatever the test
says it is. Nothing downloads, trains on real data or calls a provider.

The three properties being pinned are the ones a sitting depends on. A chunk **resumes**: the
second invocation skips what the first finished and re-attempts what it did not. A chunk **stops
on its ceiling**, both before a cell it cannot afford and inside a run that is spending more than
it was priced at. And a chunk **writes down the checks that did not run**, because since D-177 a
report can be complete but for one check and the exit code no longer says so.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from conftest import REPO_ROOT, load_module
from quaestor.configs import CONFIGURATIONS
from quaestor.errors import QuaestorError, ToolError
from quaestor.llm.base import Completion
from quaestor.llm.fake import FakeLLM
from quaestor.llm.offline import OfflineLLM
from quaestor.vocab import Configuration

sys.path.insert(0, str(REPO_ROOT / "eval"))
harness = load_module("quaestor_eval_run_study_under_test", REPO_ROOT / "eval" / "run_study.py")
seed_module = load_module("quaestor_eval_seed_under_test", REPO_ROOT / "eval" / "seed.py")

TAXONOMY_FILE = REPO_ROOT / "eval" / "taxonomy.yaml"
SUBJECTS = REPO_ROOT / "subjects"

CHEAP = "credit__T1__false_claim"
"""The one seeded variant every test here runs: a `package.yaml` edit, so it builds in a blink."""

CONTROL = "control_credit_clean"


@pytest.fixture(scope="module")
def variants(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Two variants of the credit subject, built once for the module."""
    root = tmp_path_factory.mktemp("variants")
    taxonomy = seed_module.load_taxonomy(TAXONOMY_FILE)
    for spec in taxonomy.specs:
        if spec.id in {CHEAP, CONTROL}:
            seed_module.seed(
                SUBJECTS / spec.subject, spec, root / spec.id, synthetic_n=800, taxonomy=taxonomy
            )
    return root


def _chunk(variants_dir: Path, out: Path, **kwargs: Any) -> Any:
    """Run one chunk of `rules_only` over the built variants, saying nothing on the way."""
    kwargs.setdefault("provider", OfflineLLM())
    kwargs.setdefault("configurations", [Configuration.rules_only.value])
    kwargs.setdefault("synthetic", 800)
    kwargs.setdefault("log", lambda _message: None)
    return harness.run_chunk(variants_dir, out, **kwargs)


def _ledger(out: Path) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads((out / harness.LEDGER_FILE).read_text(encoding="utf-8"))
    return payload


# --- the chunk and its ledger ---------------------------------------------------------------


def test_a_chunk_runs_every_cell_and_writes_each_one_down(variants: Path, tmp_path: Path) -> None:
    out = tmp_path / "study"
    summary = _chunk(variants, out)
    assert len(summary.ran) == 2
    assert not summary.failed and not summary.skipped
    assert summary.remaining == 0 and not summary.stopped_for_budget
    for cell in summary.ran:
        assert (Path(str(cell.out_dir)) / "report.md").is_file()
        assert cell.status == "done" and cell.attempts == 1
    ledger = _ledger(out)
    assert ledger["done"] == 2 and ledger["failed"] == 0
    assert ledger["remaining_in_last_plan"] == 0
    assert [row["variant"] for row in ledger["cells"]] == sorted([CHEAP, CONTROL])


def test_the_ledger_carries_what_a_run_produced_and_not_a_word_of_its_prose(
    variants: Path, tmp_path: Path
) -> None:
    """`ledger.json` is the machine-readable half of a run: classes, grounding, cost, checks."""
    out = tmp_path / "study"
    _chunk(variants, out)
    row = next(item for item in _ledger(out)["cells"] if item["variant"] == CHEAP)
    assert "T1" in {finding["class"] for finding in row["findings"]}
    assert row["precision_pre"] == 1.0 and row["precision_post"] == 1.0
    assert row["n_claims"] > 0 and row["calls"] == 0 and row["cost_usd"] == 0.0
    assert row["checks_failed"] == [] and row["error"] is None


def test_a_second_chunk_skips_what_the_first_one_finished(variants: Path, tmp_path: Path) -> None:
    """Resumability, which is the whole reason the harness exists: 19 chunks, one study."""
    out = tmp_path / "study"
    first = _chunk(variants, out, only=[CHEAP])
    assert len(first.ran) == 1 and first.remaining == 0
    second = _chunk(variants, out)
    assert [cell.variant for cell in second.skipped] == [CHEAP]
    assert [record.cell.variant for record in second.ran] == [CONTROL]
    assert second.remaining == 0
    assert _ledger(out)["done"] == 2


def test_a_cell_that_failed_is_attempted_again_by_the_next_chunk(
    variants: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A study with a missing cell is not the study that was budgeted, so a failure is retried."""
    out = tmp_path / "study"
    broken = QuaestorError("run_model: the subject exited 1", fix="cat trace.jsonl")

    def refuse(*_args: Any, **_kwargs: Any) -> None:
        raise broken

    monkeypatch.setattr(harness, "validate", refuse)
    first = _chunk(variants, out, only=[CHEAP])
    assert not first.ran and len(first.failed) == 1
    assert first.failed[0].status == "failed" and first.remaining == 1
    assert "run_model" in str(first.failed[0].error)
    assert not first.failed[0].budget_stopped

    monkeypatch.undo()
    second = _chunk(variants, out, only=[CHEAP])
    assert len(second.ran) == 1 and second.remaining == 0
    assert second.ran[0].attempts == 2


def test_a_check_that_did_not_run_reaches_the_ledger_and_the_summary(
    variants: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D-177: a caller judging a run reads `checks_failed`, because exit 0 no longer says."""
    out = tmp_path / "study"
    from quaestor.tools import registry as registry_module

    original = registry_module.ToolRegistry.call

    def crash(self: Any, name: str, args: Any, ctx: Any) -> Any:
        if name == "check_collinearity":
            raise ToolError("the design matrix has one column")
        result: Any = original(self, name, args, ctx)
        return result

    monkeypatch.setattr(registry_module.ToolRegistry, "call", crash)
    summary = _chunk(variants, out, only=[CHEAP])
    assert len(summary.ran) == 1
    assert [record.cell.variant for record in summary.checks_failed] == [CHEAP]
    failure = summary.ran[0].checks_failed[0]
    assert failure["tool"] == "check_collinearity"
    assert "one column" in failure["message"]
    row = next(item for item in _ledger(out)["cells"] if item["variant"] == CHEAP)
    assert row["status"] == "done" and row["checks_failed"] == [failure]


def test_a_killed_chunk_leaves_a_ledger_that_parses(variants: Path, tmp_path: Path) -> None:
    """The write is a rename, so the file is either the old ledger or the new one, never half."""
    out = tmp_path / "study"
    _chunk(variants, out, only=[CHEAP])
    assert json.loads((out / harness.LEDGER_FILE).read_text(encoding="utf-8"))
    assert not list(out.glob("*.tmp"))


# --- the cost ceiling ------------------------------------------------------------------------


def _priced(cost: float | None) -> FakeLLM:
    """A provider that answers anything and reports one cost per call."""
    return FakeLLM(None, None, cost_usd=cost)


def test_the_wrapper_stops_before_the_call_that_would_cross_the_line() -> None:
    llm = harness.BudgetedLLM(_priced(0.60), max_cost_usd=1.00)
    assert isinstance(llm.complete("one"), Completion)
    assert llm.complete("two").text is not None
    assert llm.spent_usd == pytest.approx(1.20) and llm.calls == 2
    with pytest.raises(harness.StudyBudgetError, match=r"\$1.0000 is reached"):
        llm.complete("three")
    assert llm.calls == 2


def test_an_unpriced_call_under_a_ceiling_is_refused_rather_than_counted_as_free() -> None:
    """`Completion.cost_usd` is `None` for "unknown"; a zero would make the ceiling always pass."""
    llm = harness.BudgetedLLM(_priced(None), max_cost_usd=1.00)
    with pytest.raises(harness.StudyBudgetError, match="priced no call"):
        llm.complete("one")


def test_an_unpriced_call_with_no_ceiling_is_fine() -> None:
    llm = harness.BudgetedLLM(_priced(None))
    assert llm.complete("one").cost_usd is None
    assert llm.spent_usd == 0.0 and llm.remaining_usd == float("inf")


def test_the_wrapper_reports_the_provider_it_wraps() -> None:
    inner = _priced(0.1)
    assert harness.BudgetedLLM(inner).name == inner.name


def test_a_cell_that_does_not_fit_the_ceiling_is_not_started(
    variants: Path, tmp_path: Path
) -> None:
    """The soft ceiling: a chunk ends on a cell boundary instead of stranding a half-paid run."""
    out = tmp_path / "study"
    lines: list[str] = []
    summary = _chunk(
        variants,
        out,
        configurations=[Configuration.full_agent.value],
        provider=_priced(0.01),
        max_cost_usd=0.50,
        log=lines.append,
    )
    assert not summary.ran and not summary.failed
    assert summary.stopped_for_budget and summary.remaining == 2
    assert any("does not fit" in line for line in lines)
    assert _ledger(out)["cells"] == []


def test_the_ceiling_stops_a_run_that_is_spending_more_than_it_was_priced_at(
    variants: Path, tmp_path: Path
) -> None:
    """The hard ceiling, which is D-179's argument: a per-study total cannot see one run double."""
    out = tmp_path / "study"
    summary = _chunk(
        variants,
        out,
        only=[CHEAP],
        configurations=[Configuration.plain_llm.value],
        provider=_priced(3.00),
        max_cost_usd=2.00,
    )
    assert not summary.ran and len(summary.failed) == 1
    record = summary.failed[0]
    assert record.budget_stopped and record.status == "failed"
    assert "--max-cost" in str(record.error)
    assert summary.stopped_for_budget and summary.remaining == 1
    assert _ledger(out)["cells"][0]["budget_stopped"] is True


def test_the_ceiling_counts_across_the_cells_of_one_chunk_and_not_across_chunks(
    variants: Path, tmp_path: Path
) -> None:
    """`--max-cost` is per chunk (D-174): a new invocation starts the count again, by design."""
    out = tmp_path / "study"
    first = _chunk(variants, out, max_cost_usd=1.00)
    assert len(first.ran) == 2 and first.spent_usd == 0.0
    second = _chunk(variants, out, max_cost_usd=1.00)
    assert not second.ran and len(second.skipped) == 2


def test_the_estimate_prefers_the_ledger_s_own_runs_to_the_measured_table(
    variants: Path, tmp_path: Path
) -> None:
    """D-179's table prices the first cell; what a cell actually cost prices the next one."""
    out = tmp_path / "study"
    ledger = harness.Ledger(out / harness.LEDGER_FILE)
    cell = harness.Cell(Configuration.full_agent.value, CHEAP)
    subjects = {CHEAP: "credit_default", CONTROL: "credit_default"}
    assert harness._estimate(cell, "credit_default", ledger, subjects) == pytest.approx(5.2635)
    ledger.record(harness.CellRecord(cell=cell, status="done", cost_usd=2.00), remaining=0)
    assert harness._estimate(cell, "credit_default", ledger, subjects) == pytest.approx(2.00)


def test_the_measured_table_is_the_one_the_pricing_runs_produced() -> None:
    """D-179 and D-180, so that a figure edited in one place is not quietly disagreed with."""
    table = harness.ESTIMATED_COST_USD
    assert table["rules_only"] == {"credit_default": 0.0, "msr_prepayment": 0.0}
    assert table["plain_llm"]["credit_default"] == pytest.approx(1.5622)
    assert table["full_agent"]["credit_default"] == pytest.approx(5.2635)
    assert table["full_agent"]["msr_prepayment"] == pytest.approx(5.5033)
    ratio = table["full_agent"]["msr_prepayment"] / table["full_agent"]["credit_default"]
    assert table["plain_llm"]["msr_prepayment"] == pytest.approx(
        table["plain_llm"]["credit_default"] * ratio, abs=5e-4
    )


# --- the cells, and what a chunk refuses to start at all --------------------------------------


def test_the_cells_are_ordered_configuration_by_configuration(variants: Path) -> None:
    cells = harness.plan_cells(variants, ["rules_only", "plain_llm"])
    assert [cell.key for cell in cells] == [
        f"rules_only/{CONTROL}",
        f"rules_only/{CHEAP}",
        f"plain_llm/{CONTROL}",
        f"plain_llm/{CHEAP}",
    ]


def test_only_restricts_the_chunk_and_names_a_variant_that_is_not_there(variants: Path) -> None:
    assert [
        cell.variant for cell in harness.plan_cells(variants, ["rules_only"], only=[CHEAP])
    ] == [CHEAP]
    with pytest.raises(QuaestorError, match="no variant named nope"):
        harness.plan_cells(variants, ["rules_only"], only=["nope"])


@pytest.mark.parametrize(
    ("make", "needle"),
    [
        (lambda root: root / "nowhere", "no variants directory"),
        (lambda root: root, "holds no model package"),
    ],
    ids=["no-directory", "no-package"],
)
def test_a_variants_directory_that_is_not_one_is_a_usage_error(
    tmp_path: Path, make: Any, needle: str
) -> None:
    with pytest.raises(QuaestorError, match=needle):
        harness.plan_cells(make(tmp_path), ["rules_only"])


def test_a_variant_with_no_answer_key_is_priced_as_the_cheaper_subject(tmp_path: Path) -> None:
    assert harness.subject_of_variant(tmp_path) == "credit_default"


def test_the_subject_is_read_from_the_answer_key(variants: Path) -> None:
    assert harness.subject_of_variant(variants / CHEAP) == "credit_default"


@pytest.mark.parametrize(
    ("rows", "data", "expected"),
    [(None, None, 5000), (1200, None, 1200), (None, "/data", None), (1200, "/data", None)],
    ids=["default", "named", "real", "real-wins"],
)
def test_a_bare_synthetic_means_each_subject_s_own_documented_size(
    rows: int | None, data: str | None, expected: int | None
) -> None:
    assert harness._rows_for("credit_default", rows, data) == expected


def test_a_subject_with_no_documented_size_asks_the_human_for_a_number() -> None:
    with pytest.raises(QuaestorError, match="no documented synthetic size"):
        harness._rows_for("something_else", None, None)


# --- recording -------------------------------------------------------------------------------


def test_each_cell_records_into_a_store_of_its_own(variants: Path, tmp_path: Path) -> None:
    """Cassette keys hash the request, so two runs in one directory are ambiguous: never pool."""
    out = tmp_path / "study"
    cassettes = tmp_path / "cassettes"
    _chunk(
        variants,
        out,
        configurations=[Configuration.plain_llm.value],
        provider=OfflineLLM(),
        cassettes_dir=cassettes,
    )
    for variant in (CHEAP, CONTROL):
        store = cassettes / "plain_llm" / variant
        assert store.is_dir() and list(store.glob("*.json"))


# --- the ledger as a file --------------------------------------------------------------------


def test_a_ledger_reads_back_everything_it_wrote(tmp_path: Path) -> None:
    path = tmp_path / harness.LEDGER_FILE
    cell = harness.Cell("full_agent", CHEAP)
    first = harness.Ledger(path)
    first.record(
        harness.CellRecord(
            cell=cell,
            status="done",
            cost_usd=5.26,
            calls=20,
            seconds=1019.0,
            out_dir="somewhere",
            precision_pre=1.0,
            precision_post=1.0,
            n_claims=267,
            findings=[{"class": "T1", "severity": "high"}],
            checks_failed=[{"tool": "check_collinearity", "message": "one column"}],
        ),
        remaining=61,
    )
    second = harness.Ledger(path)
    assert second.is_done(cell) and second.attempts(cell) == 1
    record = second.records[cell.key]
    assert record.cost_usd == pytest.approx(5.26) and record.calls == 20
    assert record.findings == [{"class": "T1", "severity": "high"}]
    assert record.checks_failed[0]["tool"] == "check_collinearity"
    assert json.loads(path.read_text(encoding="utf-8"))["remaining_in_last_plan"] == 61


def test_a_failed_cell_is_not_done(tmp_path: Path) -> None:
    path = tmp_path / harness.LEDGER_FILE
    cell = harness.Cell("full_agent", CHEAP)
    ledger = harness.Ledger(path)
    ledger.record(harness.CellRecord(cell=cell, status="failed", error="no"), remaining=1)
    assert not harness.Ledger(path).is_done(cell)


# --- the command line ------------------------------------------------------------------------


def _run_cli(argv: Sequence[str]) -> int:
    from quaestor.cli import main as cli_main

    return int(cli_main(list(argv)))


def test_study_run_from_the_command_line_writes_a_ledger_and_says_what_is_left(
    variants: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "study"
    code = _run_cli(
        [
            "study",
            "run",
            "--variants",
            str(variants),
            "--out",
            str(out),
            "--config",
            "rules_only",
            "--synthetic",
            "800",
            "--llm",
            "fake",
        ]
    )
    printed = capsys.readouterr().out
    assert code == 0
    assert "2 cell(s) run, 0 failed, 0 already done" in printed
    assert "0 cell(s) of this plan remaining" in printed
    assert harness.LEDGER_FILE in printed
    assert _ledger(out)["done"] == 2


def test_study_run_names_the_harness_it_cannot_find(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    elsewhere = tmp_path / "eval" / "taxonomy.yaml"
    elsewhere.parent.mkdir(parents=True)
    elsewhere.write_text(TAXONOMY_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    code = _run_cli(
        [
            "study",
            "run",
            "--variants",
            str(tmp_path),
            "--out",
            str(tmp_path / "study"),
            "--synthetic",
            "--llm",
            "fake",
            "--taxonomy",
            str(elsewhere),
        ]
    )
    assert code == 2
    assert "run_study.py" in capsys.readouterr().err


def test_study_run_reports_a_cell_that_produced_no_report(
    variants: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 1 for a chunk one of whose cells produced nothing, as `validate` exits 1 for one.

    The cell here is a directory that looks like a package from outside and does not load from
    inside -- a `package.yaml` with no `code/` beside it -- which is the cheapest honest way to
    make a run produce no report without calling anything.
    """
    broken = tmp_path / "broken"
    (broken / CHEAP).mkdir(parents=True)
    (broken / CHEAP / "package.yaml").write_text(
        (variants / CHEAP / "package.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    out = tmp_path / "study"
    code = _run_cli(
        [
            "study",
            "run",
            "--variants",
            str(broken),
            "--out",
            str(out),
            "--config",
            "rules_only",
            "--synthetic",
            "800",
            "--llm",
            "fake",
        ]
    )
    printed = capsys.readouterr().out
    assert code == 1
    assert "0 cell(s) run, 1 failed" in printed and "1 cell(s) of this plan" in printed
    assert "code/" in str(_ledger(out)["cells"][0]["error"])


def test_the_default_configuration_order_is_cheapest_first() -> None:
    """`docs/STUDY.md` section 4's order, not the vocabulary's: a free arm rehearses the harness."""
    from quaestor.cli import STUDY_ORDER

    assert STUDY_ORDER == ("rules_only", "plain_llm", "full_agent")
    assert set(STUDY_ORDER) == {name.value for name in CONFIGURATIONS}


def test_study_run_names_a_variants_directory_that_is_not_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _run_cli(
        [
            "study",
            "run",
            "--variants",
            str(tmp_path / "nowhere"),
            "--out",
            str(tmp_path / "study"),
            "--config",
            "rules_only",
            "--synthetic",
            "--llm",
            "fake",
        ]
    )
    assert code == 2
    assert "no variants directory" in capsys.readouterr().err


def test_study_run_says_it_stopped_on_the_ceiling_and_how_to_continue(
    variants: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The operator's cue that the sitting ended on money and not on the study running out."""
    code = _run_cli(
        [
            "study",
            "run",
            "--variants",
            str(variants),
            "--out",
            str(tmp_path / "study"),
            "--config",
            "full_agent",
            "--synthetic",
            "800",
            "--llm",
            "fake",
            "--max-cost",
            "0.50",
        ]
    )
    printed = capsys.readouterr().out
    assert code == 0
    assert "stopped on --max-cost $0.5000; rerun the same command to continue" in printed
    assert "2 cell(s) of this plan remaining" in printed


def test_study_run_prints_the_cells_that_reported_without_a_check(
    variants: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: Any
) -> None:
    """D-177 through the front door: exit 0, and the missing check said out loud."""
    from quaestor.tools import registry as registry_module

    original = registry_module.ToolRegistry.call

    def crash(self: Any, name: str, args: Any, ctx: Any) -> Any:
        if name == "check_collinearity":
            raise ToolError("the design matrix has one column")
        result: Any = original(self, name, args, ctx)
        return result

    monkeypatch.setattr(registry_module.ToolRegistry, "call", crash)
    code = _run_cli(
        [
            "study",
            "run",
            "--variants",
            str(variants),
            "--out",
            str(tmp_path / "study"),
            "--config",
            "rules_only",
            "--only",
            CHEAP,
            "--synthetic",
            "800",
            "--llm",
            "fake",
        ]
    )
    printed = capsys.readouterr().out
    assert code == 0
    assert f"rules_only/{CHEAP}: reported without check_collinearity" in printed


# --- a cell owns its directory ----------------------------------------------------------------


def _kill_after(out: Path) -> None:
    """Simulate the chunk being killed: the cell's directory is on disk, the ledger is not.

    This is exactly the state D-174's seventh sitting ended in, and the state a retry has to work
    from. Removing the ledger is the smallest faithful way to produce it, because the ledger is
    written only *after* a cell finishes.
    """
    (out / harness.LEDGER_FILE).unlink()


def test_a_cell_killed_mid_attempt_can_be_retried(variants: Path, tmp_path: Path) -> None:
    """The defect chunk 2 found: without this, a killed chunk's cell can never be run again.

    The artifact store refuses to rebind a logical name to a new hash -- correctly, because every
    citation against the old one would stop resolving -- so a second attempt in the same directory
    collides on `run.duration_s`, the first thing the subject stores, before anything else happens.
    """
    out = tmp_path / "study"
    first = _chunk(variants, out, only=[CHEAP])
    assert len(first.ran) == 1
    store = out / "rules_only" / CHEAP / "artifacts"
    assert (store / "index.json").is_file()

    _kill_after(out)
    lines: list[str] = []
    second = _chunk(variants, out, only=[CHEAP], log=lines.append)
    assert len(second.ran) == 1 and not second.failed
    assert second.ran[0].status == "done"
    assert any("discarded an unfinished earlier attempt" in line for line in lines)


def test_the_retry_starts_from_nothing_rather_than_from_what_was_left(
    variants: Path, tmp_path: Path
) -> None:
    """A stale file from the killed attempt does not survive into the run that replaces it."""
    out = tmp_path / "study"
    _chunk(variants, out, only=[CHEAP])
    stale = out / "rules_only" / CHEAP / "artifacts" / "stale-from-the-killed-attempt.json"
    stale.write_text("{}", encoding="utf-8")
    _kill_after(out)

    _chunk(variants, out, only=[CHEAP])
    assert not stale.exists()
    assert (out / "rules_only" / CHEAP / "report.md").is_file()


def test_a_finished_cell_and_its_tapes_are_never_cleared(variants: Path, tmp_path: Path) -> None:
    """The clearing is reachable only for a cell the ledger does not call `done`.

    A resumed chunk must not touch what an earlier chunk paid for: nineteen chunks over 62 cells,
    and a rule that deleted finished work would lose the study one sitting at a time. The case
    this pins is real -- chunk 2 banked one `plain_llm` cell at $1.61 and eight tapes before the
    chunk died on the cell beside it, and every later chunk has to leave both alone.
    """
    out, cassettes = tmp_path / "study", tmp_path / "cassettes"
    _chunk(
        variants,
        out,
        only=[CHEAP],
        configurations=[Configuration.plain_llm.value],
        cassettes_dir=cassettes,
    )
    report = out / "plain_llm" / CHEAP / "report.md"
    tapes = sorted((cassettes / "plain_llm" / CHEAP).glob("*.json"))
    stamp = report.stat().st_mtime_ns
    assert tapes

    second = _chunk(
        variants, out, configurations=[Configuration.plain_llm.value], cassettes_dir=cassettes
    )
    assert CHEAP in [cell.variant for cell in second.skipped]
    assert report.stat().st_mtime_ns == stamp
    assert sorted((cassettes / "plain_llm" / CHEAP).glob("*.json")) == tapes


def test_a_retry_does_not_pool_the_killed_attempt_s_cassettes(
    variants: Path, tmp_path: Path
) -> None:
    """A cassette is keyed on a hash of the request, so two attempts in one store are ambiguous."""
    out, cassettes = tmp_path / "study", tmp_path / "cassettes"
    _chunk(
        variants,
        out,
        only=[CHEAP],
        configurations=[Configuration.plain_llm.value],
        cassettes_dir=cassettes,
    )
    store = cassettes / "plain_llm" / CHEAP
    orphan = store / "0000000000000000.json"
    orphan.write_text("{}", encoding="utf-8")
    _kill_after(out)

    _chunk(
        variants,
        out,
        only=[CHEAP],
        configurations=[Configuration.plain_llm.value],
        cassettes_dir=cassettes,
    )
    assert not orphan.exists()
    assert list(store.glob("*.json"))


def test_clearing_says_what_it_removed_and_nothing_when_there_is_nothing(tmp_path: Path) -> None:
    assert harness._clear_previous_attempt(tmp_path / "nowhere", None) == []
    cell, tapes = tmp_path / "cell", tmp_path / "tapes"
    (cell / "artifacts").mkdir(parents=True)
    tapes.mkdir()
    assert harness._clear_previous_attempt(cell, tapes) == [str(cell), str(tapes)]
    assert not cell.exists() and not tapes.exists()


def test_the_ledger_field_names_the_plan_it_counted(variants: Path, tmp_path: Path) -> None:
    """`remaining_in_last_plan`, because a chunk restricted by arm leaves a number about that arm.

    The case that named the field: `rules_only` finishes, a `plain_llm` chunk leaves cells
    outstanding, and then a `rules_only` chunk is rerun -- which writes **zero** over the ledger
    while the `plain_llm` cells are still to do. The zero is true of the plan it counted and false
    of the study, and a driver reads it correctly only by rerunning one command line until that
    command line's own number is zero (D-181, amended).
    """
    out = tmp_path / "study"
    _chunk(variants, out, configurations=[Configuration.rules_only.value])
    assert _ledger(out)["remaining_in_last_plan"] == 0

    outstanding = _chunk(
        variants,
        out,
        configurations=[Configuration.plain_llm.value],
        provider=_priced(0.01),
        max_cost_usd=0.001,
    )
    assert outstanding.remaining == 2
    assert _ledger(out)["remaining_in_last_plan"] == 2

    again = _chunk(variants, out, configurations=[Configuration.rules_only.value])
    assert not again.ran and len(again.skipped) == 2
    assert _ledger(out)["remaining_in_last_plan"] == 0
    assert _ledger(out)["schema_version"] == 2


# --- the study lock ---------------------------------------------------------------------------


def test_a_second_chunk_against_a_live_study_refuses_to_start(
    variants: Path, tmp_path: Path
) -> None:
    """The stale-snapshot race, closed: a ledger is read and written under one lock.

    Two chunks against one `--out` are last-writer-wins over a snapshot taken at construction, so
    the loser's finished cells vanish from the ledger while their output stays on disk -- and the
    next chunk pays for them again. On 2026-09-18 that came within seconds of erasing a finished
    `$1.784082` cell of a live study.
    """
    out = tmp_path / "study"
    out.mkdir()
    with harness.study_lock(out):
        with pytest.raises(harness.StudyLockedError, match="locked by another"):
            _chunk(variants, out, only=[CHEAP])
    assert not (out / harness.LEDGER_FILE).exists()

    summary = _chunk(variants, out, only=[CHEAP])
    assert len(summary.ran) == 1


def test_the_lock_names_the_process_holding_it(tmp_path: Path) -> None:
    """So an operator can tell a live sitting from something they have forgotten about."""
    tmp_path.joinpath("study").mkdir()
    root = tmp_path / "study"
    with harness.study_lock(root):
        held = (root / harness.LOCK_FILE).read_text(encoding="utf-8")
        assert f"pid {os.getpid()} since " in held
        with pytest.raises(harness.StudyLockedError) as raised:
            with harness.study_lock(root):
                pass
    assert f"pid {os.getpid()}" in str(raised.value.message)
    assert "paid for twice" in str(raised.value.message)


def test_a_released_lock_is_taken_again_and_the_file_is_left_behind(tmp_path: Path) -> None:
    """Releasing leaves the file: deleting is a race of its own and costs nothing to skip."""
    root = tmp_path / "study"
    root.mkdir()
    with harness.study_lock(root):
        pass
    assert (root / harness.LOCK_FILE).is_file()
    with harness.study_lock(root):
        pass


def test_a_lock_left_by_a_killed_chunk_does_not_block_the_next_one(tmp_path: Path) -> None:
    """A kill is how a sitting normally ends (D-174), so the lock has to survive being killed.

    `flock` is held by the open file description, so the kernel drops it when the process dies
    however it dies -- there is nothing to reap, which is the reason it is not a PID file. A file
    left behind by a process that is gone is taken straight over.
    """
    root = tmp_path / "study"
    root.mkdir()
    (root / harness.LOCK_FILE).write_text("pid 999999 since 2026-09-18T00:00:00+00:00\n", "utf-8")
    with harness.study_lock(root):
        assert f"pid {os.getpid()}" in (root / harness.LOCK_FILE).read_text(encoding="utf-8")


def test_the_lock_is_released_when_the_body_raises(tmp_path: Path) -> None:
    """A chunk that dies inside the lock must not leave the study locked to itself."""
    root = tmp_path / "study"
    root.mkdir()
    with pytest.raises(ToolError), harness.study_lock(root):
        raise ToolError("the subject would not run")
    with harness.study_lock(root):
        pass


def test_a_bad_request_is_refused_before_the_lock_is_ever_taken(tmp_path: Path) -> None:
    """`plan_cells` validates first, so a mistyped `--variants` leaves no lock file at all."""
    out = tmp_path / "study"
    with pytest.raises(QuaestorError, match="no variants directory"):
        harness.run_chunk(
            tmp_path / "nowhere",
            out,
            provider=OfflineLLM(),
            configurations=[Configuration.rules_only.value],
            log=lambda _m: None,
        )
    assert not out.exists()
