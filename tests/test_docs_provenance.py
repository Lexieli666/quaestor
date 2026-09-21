"""Phase 16: ``docs/PROVENANCE.md`` is the index of every number in the documentation.

`CLAUDE.md` forbids a figure in `README.md`, under `docs/` or in a report that a committed run did
not produce. This module makes that rule checkable rather than aspirational, in the shape Probatio
uses: it reads `docs/PROVENANCE.md`, runs each row's check against the file the row names, asserts
the figure really is printed in every document the row claims, and then **sweeps** `README.md` for
any numeral that neither table accounts for.

The sweep is the half that cannot be satisfied by writing more prose. A number added to the README
fails the suite until somebody names the committed file it came from.

Scope is stated in the document and enforced by :func:`test_every_document_that_prints_a_number_is
_either_indexed_or_declared_unswept`: the README is indexed numeral by numeral, `docs/EVALUATION.md`
is guarded by the live-run modules that re-derive its figures from traces, and the documents that
are argument or history rather than measurement are named as unswept with the reason. A document
added under `docs/` without an entry in one of those three lists fails here.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any, Final

import pytest

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
DOC: Final = REPO_ROOT / "docs" / "PROVENANCE.md"
TEXT: Final = DOC.read_text(encoding="utf-8")

PUBLISHED: Final = REPO_ROOT / "eval" / "results" / "published"

NUMERAL: Final = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")
CITATION: Final = re.compile(r"\[\[(?:art|reg):[^\]]+\]\]")
CONFIGS: Final = ("full_agent", "rules_only", "plain_llm")


# --------------------------------------------------------------------------- the document's tables


def rows(heading: str) -> list[list[str]]:
    """The cells of every body row of the markdown table under ``heading``."""
    section = TEXT.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]
    parsed = []
    for line in section.splitlines():
        if not line.startswith("| `") and not line.startswith("| [`"):
            continue
        parsed.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return parsed


MEASUREMENTS: Final = rows("Measurements")
NOT_MEASUREMENTS: Final = rows("Numerals that are not measurements")
GUARDS: Final = rows("Which test guards which document")
UNSWEPT: Final = rows("Documents that are not swept, and why")


def unticked(cell: str) -> str:
    return cell.strip().strip("`")


def prose(path: Path) -> str:
    """A document's text with emphasis markers removed, as the table's `number` column reads it."""
    return path.read_text(encoding="utf-8").replace("**", "")


# ------------------------------------------------------------------------------------ derivations


def load(source: Path) -> Any:
    return json.loads(source.read_text(encoding="utf-8"))


def json_at(source: Path, path: str) -> Any:
    value: Any = load(source)
    for key in path.split("."):
        value = value[key]
    return value


def decimals(number: str) -> int:
    return len(number.split(".")[1]) if "." in number else 0


def configuration(source: Path, name: str) -> dict[str, Any]:
    payload: dict[str, Any] = load(source)["configurations"][name]
    return payload


def collateral(source: Path, name: str, verdict: str) -> list[dict[str, Any]]:
    names = CONFIGS if name == "all" else (name,)
    found: list[dict[str, Any]] = []
    for one in names:
        found += [f for f in configuration(source, one)["collateral"] if f["verdict"] == verdict]
    return found


def cells(source: Path, name: str) -> list[dict[str, Any]]:
    everything: list[dict[str, Any]] = load(source)["cells"]
    if name == "all":
        return everything
    return [cell for cell in everything if cell["configuration"] == name]


def median_seconds(values: list[float]) -> float:
    return float(median(values))


def formatted(value: float, number: str) -> str:
    return f"{value:,.{decimals(number)}f}" if "," in number else f"{value:.{decimals(number)}f}"


def run_check(number: str, source: Path, check: str) -> None:
    """Assert ``number`` is what ``source`` holds, by whichever derivation ``check`` names."""
    bare = number.lstrip("$").rstrip("%")
    kind, _, argument = check.partition(" ")

    if kind == "text":
        assert bare in source.read_text(encoding="utf-8"), f"{number} is not in {source}"
        return

    if kind == "json":
        assert formatted(float(json_at(source, unticked(argument))), bare) == bare
        return

    if kind == "json-int":
        assert f"{int(json_at(source, unticked(argument))):,}".replace(",", "") == bare.replace(
            ",", ""
        )
        return

    if kind == "json-len":
        assert str(len(json_at(source, unticked(argument)))) == bare
        return

    if kind == "detected":
        assert str(len(configuration(source, argument)["detected"])) == bare
        return

    if kind == "seeded-scored":
        assert str(configuration(source, argument)["seeded_scored"]) == bare
        return

    if kind == "missed":
        assert str(len(configuration(source, argument)["missed"])) == bare
        return

    if kind == "false-alarms":
        name, _, control = argument.partition(" ")
        alarms = configuration(source, name)["false_alarms"]
        if control:
            alarms = [a for a in alarms if a["variant"] == control]
        assert str(len(alarms)) == bare
        return

    if kind == "per-class":
        name, defect, column = argument.split()
        assert str(configuration(source, name)["per_class"][defect][column]) == bare
        return

    if kind == "per-class-detected-or-zero":
        # A class a configuration detected none of still has a row; a class it never met has none.
        name, defect = argument.split()
        classes = configuration(source, name)["per_class"]
        assert str(classes.get(defect, {"detected": 0})["detected"]) == bare
        return

    if kind == "precision":
        assert formatted(float(configuration(source, argument)["precision"]), bare) == bare
        return

    if kind == "grounding":
        name, field = argument.split()
        assert formatted(float(configuration(source, name)["grounding"][field]), bare) == bare
        return

    if kind == "collateral-total":
        names = CONFIGS if argument == "all" else (argument,)
        assert str(sum(len(configuration(source, one)["collateral"]) for one in names)) == bare
        return

    if kind == "collateral":
        name, verdict = argument.split()
        assert str(len(collateral(source, name, verdict))) == bare
        return

    if kind == "collateral-pairings":
        name, verdict = argument.split()
        pairs = {(f["variant"], f["class"]) for f in collateral(source, name, verdict)}
        assert str(len(pairs)) == bare
        return

    if kind == "reports":
        assert str(configuration(source, argument)["runs"]) == bare
        return

    if kind == "ledger-cells":
        assert str(len(cells(source, argument))) == bare
        return

    if kind == "ledger-sum":
        name, field = argument.split()
        assert formatted(sum(float(cell[field]) for cell in cells(source, name)), bare) == bare
        return

    if kind == "ledger-median-seconds":
        assert (
            formatted(median_seconds([float(c["seconds"]) for c in cells(source, argument)]), bare)
            == bare
        )
        return

    if kind == "front-matter":
        head = source.read_text(encoding="utf-8").split("---", 2)[1]
        match = re.search(rf"^{re.escape(unticked(argument))}:\s*(.+)$", head, re.MULTILINE)
        assert match is not None, f"{source} has no front-matter key {argument}"
        assert match.group(1).strip().strip('"') == bare
        return

    if kind == "verifier-false-verified":
        perturbation, field = argument.split()
        assert str(json_at(source, f"false_verified.{perturbation}.{field}")) == bare
        return

    raise AssertionError(f"docs/PROVENANCE.md names a check this test cannot run: {check!r}")


# ------------------------------------------------------------------------------------ the tables


def test_the_measurements_table_is_not_empty_and_has_five_columns() -> None:
    assert len(MEASUREMENTS) >= 40
    assert {len(row) for row in MEASUREMENTS} == {5}


@pytest.mark.parametrize("row", MEASUREMENTS, ids=lambda row: unticked(row[0]))
def test_every_measurement_is_what_its_source_file_holds(row: list[str]) -> None:
    number, _, source, check, _ = row
    run_check(unticked(number), REPO_ROOT / unticked(source), check)


@pytest.mark.parametrize("row", MEASUREMENTS, ids=lambda row: unticked(row[0]))
def test_every_measurement_is_printed_by_every_document_the_row_names(row: list[str]) -> None:
    number, documents, *_ = row
    for name in documents.split(","):
        document = REPO_ROOT / unticked(name)
        assert document.is_file(), f"docs/PROVENANCE.md names a document that is gone: {name}"
        assert unticked(number) in prose(document), f"{number} is not printed in {name}"


@pytest.mark.parametrize("row", MEASUREMENTS, ids=lambda row: unticked(row[0]))
def test_every_source_file_a_row_names_is_committed(row: list[str]) -> None:
    """ "A committed run produced it" is the rule; an untracked file is not one."""
    source = unticked(row[2])
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", source],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if "not a git repository" in completed.stderr:  # pragma: no cover - checkout without git
        return
    assert completed.returncode == 0, f"{source} is named as provenance but is not committed"


def test_no_measurement_row_is_a_duplicate_of_another() -> None:
    """One string may hold two rows only when two different measurements print the same digits."""
    duplicated = [
        key for key, n in Counter((r[0], r[2], r[3]) for r in MEASUREMENTS).items() if n > 1
    ]
    assert not duplicated, f"identical rows: {duplicated}"


# -------------------------------------------------------------------------------------- the sweep


def accounted_for() -> list[str]:
    """Every literal string the two tables let a numeral hide inside, longest first."""
    literals = [unticked(row[0]) for row in MEASUREMENTS]
    literals += [
        unticked(row[0]) for row in NOT_MEASUREMENTS if not unticked(row[0]).startswith("re:")
    ]
    return sorted(literals, key=len, reverse=True)


def patterns() -> list[str]:
    return [
        unticked(row[0]).removeprefix("re:")
        for row in NOT_MEASUREMENTS
        if unticked(row[0]).startswith("re:")
    ]


def unfenced(name: str) -> str:
    """A document without its fenced blocks: those are quoted commands, checked separately."""
    kept, fenced = [], False
    for line in (REPO_ROOT / name).read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return "\n".join(kept).replace("**", "")


SWEPT: Final = ["README.md"]


@pytest.mark.parametrize("name", SWEPT)
def test_every_numeral_in_a_swept_document_is_accounted_for_by_one_of_the_two_tables(
    name: str,
) -> None:
    """The sweep. A number added to the README fails until a row names the file behind it."""
    remaining = unfenced(name)
    for pattern in patterns():
        remaining = re.sub(pattern, " ", remaining)
    for literal in accounted_for():
        remaining = remaining.replace(literal, " ")
    stray = sorted({match.group(0) for match in NUMERAL.finditer(remaining)})
    assert not stray, f"{name} prints numerals docs/PROVENANCE.md does not account for: {stray}"


# ---------------------------------------------------------------------------- coverage of `docs/`


def test_every_document_that_prints_a_number_is_either_indexed_or_declared_unswept() -> None:
    """No document under `docs/` may appear without landing in one of the three lists."""
    for row in GUARDS + UNSWEPT:
        document = unticked(row[0])
        assert (REPO_ROOT / document).is_file(), document
    for row in GUARDS:
        test = unticked(row[1])
        assert (REPO_ROOT / test).is_file(), test

    listed = {unticked(row[0]) for row in GUARDS} | {unticked(row[0]) for row in UNSWEPT}
    present = {"README.md", "CHANGELOG.md"} | {
        str(path.relative_to(REPO_ROOT)) for path in (REPO_ROOT / "docs").rglob("*.md")
    }
    assert present == listed, present ^ listed


def test_no_document_is_both_guarded_and_declared_unswept() -> None:
    both = {unticked(row[0]) for row in GUARDS} & {unticked(row[0]) for row in UNSWEPT}
    assert not both, both


# --------------------------------------------------- the claims the README makes about other files


def test_the_readme_quotes_the_excerpt_verbatim_from_the_committed_report() -> None:
    """§10 asks for "one real report excerpt"; the README says verbatim, so it must be verbatim."""
    report = (REPO_ROOT / "eval" / "results" / "first-live" / "credit" / "report.md").read_text(
        encoding="utf-8"
    )
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("## What a report looks like", 1)[1].split("\n---", 1)[0]

    quoted = [line[2:] for line in section.splitlines() if line.startswith("> ")]
    assert quoted, "the excerpt block is gone"
    # The README rewraps the report's lines and fences each citation in backticks to keep the
    # markdown readable; neither changes a character of the sentence or of any number in it.
    rejoined = " ".join(quoted).replace("`", "")
    for sentence in re.split(r"(?<=\.)\s+(?=[A-Z])", rejoined):
        flattened = re.sub(r"\s+", " ", sentence).strip()
        assert flattened in re.sub(r"\s+", " ", report), flattened


def test_the_readme_names_the_commit_and_the_run_the_study_numbers_come_from() -> None:
    manifest = load(PUBLISHED / "MANIFEST.json")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert manifest["commit"][:7] in readme
    assert Path(manifest["source_results_dir"]).name in readme
    assert manifest["model"] in readme

    completed = subprocess.run(
        ["git", "cat-file", "-t", manifest["commit"]],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:  # pragma: no cover - shallow checkout
        return
    assert completed.stdout.strip() == "commit"


def test_the_readme_lists_exactly_the_misses_the_scorer_recorded() -> None:
    summary = load(PUBLISHED / "summary.json")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("### The misses, by variant", 1)[1].split("\n###", 1)[0]
    listed = {
        line.strip("- `").strip("`") for line in section.splitlines() if line.startswith("- `")
    }
    assert listed == set(summary["configurations"]["plain_llm"]["missed"])
    for name in CONFIGS:
        if name != "plain_llm":
            assert not summary["configurations"][name]["missed"], name


def test_the_readme_detection_table_matches_the_scorer_class_for_class() -> None:
    summary = load(PUBLISHED / "summary.json")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("| defect class | seeded n |", 1)[1].split("\n\n", 1)[0]

    seen = 0
    for line in section.splitlines():
        cells_of = r"\|\s*`(\w+)`[^|]*" + r"\|\s*(\d+)\s*" * 4 + r"\|"
        match = re.match(cells_of, line)
        if not match:
            continue
        defect, seeded, rules, plain, full = match.groups()
        for name, printed in (("rules_only", rules), ("plain_llm", plain), ("full_agent", full)):
            entry = summary["configurations"][name]["per_class"][defect]
            assert str(entry["seeded"]) == seeded, (defect, name)
            assert str(entry["detected"]) == printed, (defect, name)
        seen += 1
    assert seen == len(summary["configurations"]["full_agent"]["per_class"]), seen


def test_the_readme_control_table_matches_the_scorers_false_alarms() -> None:
    summary = load(PUBLISHED / "summary.json")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("### False alarms on the four controls", 1)[1].split("\n###", 1)[0]

    counted: dict[str, Counter[str]] = {name: Counter() for name in CONFIGS}
    for name in CONFIGS:
        for alarm in summary["configurations"][name]["false_alarms"]:
            counted[name][alarm["variant"]] += 1

    controls = set()
    for line in section.splitlines():
        match = re.match(r"\|\s*`(control_\w+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", line)
        if not match:
            continue
        control, rules, plain, full = match.groups()
        controls.add(control)
        for name, printed in (("rules_only", rules), ("plain_llm", plain), ("full_agent", full)):
            assert str(counted[name][control]) == printed, (control, name)
    assert len(controls) == 4, controls


def test_the_readme_does_not_repeat_amendment_ones_wrong_collateral_count_as_a_fact() -> None:
    """93 may appear only inside the paragraph that says it is wrong (D-198)."""
    readme = CITATION.sub(" ", prose(REPO_ROOT / "README.md"))
    carrying = [line for line in readme.splitlines() if "93" in line]
    assert carrying, "the correction is gone"
    for line in carrying:
        assert line.startswith("> "), f"93 outside the correction blockquote: {line}"
    quoted = [line[2:] for line in readme.splitlines() if line.startswith("> ")]
    correction = re.sub(r"\s+", " ", " ".join(quoted))
    assert "does not come from the published scoring" in correction
    assert "collateral_unjudged: 46" in correction


def test_study_md_amendment_three_corrects_amendment_one_and_agrees_with_the_scorer() -> None:
    summary = load(PUBLISHED / "summary.json")
    unjudged = collateral(PUBLISHED / "summary.json", "all", "unjudged")
    pairings = {(f["variant"], f["class"]) for f in unjudged}
    study = prose(REPO_ROOT / "docs" / "STUDY.md")

    assert "### Amendment 3 — 2026-09-20" in study
    amendment = study.split("### Amendment 3", 1)[1]
    assert str(len(unjudged)) in amendment
    assert str(len(pairings)) in amendment
    assert "Amendment 1 is left as written" in amendment

    # Amendment 1 is left as written, so its wrong figure must still be there to be corrected.
    assert "93 collateral findings" in study.split("### Amendment 3", 1)[0]
    assert summary["configurations"]["plain_llm"]["collateral_unjudged"] == len(unjudged)


def test_the_readme_quotes_the_probatio_status_the_run_log_records() -> None:
    """7 failed / 33 passed is an observation, so it is sourced to the run log that observed it."""
    readme = prose(REPO_ROOT / "README.md")
    progress = prose(REPO_ROOT / "PROGRESS.md")
    assert "7 failed / 33 passed" in readme
    assert "7 failed, 33 passed" in readme
    assert "7 failed, 33 passed" in progress
    assert "D-188" in readme


def test_the_readme_claims_no_component_the_repository_does_not_ship() -> None:
    """The roadmap says the MCP server is not built; nothing above it may imply otherwise."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert not (REPO_ROOT / "src" / "quaestor" / "mcp_server.py").exists()
    assert "The MCP server" in readme.split("## Roadmap", 1)[1]
    assert "quaestor mcp" not in readme.split("## Roadmap", 1)[0]


def test_the_quick_start_command_is_one_the_cli_accepts() -> None:
    """Every flag the quick start shows is a flag `quaestor validate --help` names."""
    from quaestor.cli import build_parser

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("## Quick start", 1)[1].split("\n---", 1)[0]
    flags = set(re.findall(r"(?<![\w-])--[a-z][a-z-]+", section))

    parser = build_parser()
    known: set[str] = set()
    for command in parser._subparsers._group_actions[0].choices.values():  # type: ignore[union-attr]
        for action in command._actions:
            known.update(action.option_strings)
    assert flags <= known | {"--help"}, flags - known


def test_the_prior_art_note_exists_carries_the_date_and_every_claim_has_a_url() -> None:
    """§12 rejects a comparison not verified on a stated date; the note is what states it."""
    note = (REPO_ROOT / "notes" / "prior-art.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "2026-09-20" in note and "2026-09-20" in readme
    assert "notes/prior-art.md" in readme
    for vendor in ("ValidMind", "deepchecks"):
        assert vendor in note and vendor in readme
    for url in ("https://validmind.com/", "https://github.com/deepchecks/deepchecks"):
        assert url in note
    # Each vendor section must carry at least one fetched URL per claim heading.
    for heading in re.findall(r"^### \d\.\d .+$", note, re.MULTILINE):
        body = note.split(heading, 1)[1].split("\n### ", 1)[0]
        assert "http" in body or "not checked" in body, heading


def test_the_readme_never_claims_compliance() -> None:
    """`CLAUDE.md`: SR 11-7-shaped, never compliant or certified."""
    readme = prose(REPO_ROOT / "README.md")
    for line in readme.splitlines():
        lowered = line.lower()
        for word in ("compliant", "certified"):
            if word in lowered:
                assert "not " + word in lowered, line
    assert "SR 11-7 as revised by SR 26-2" in readme, "D-055's required wording is gone"


def release_section() -> str:
    """The `0.1.0` entry only: the historical entries below it are not swept (see the document)."""
    from quaestor import __version__

    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    body = changelog.split(f"## [{__version__}]", 1)[1].split("\n## ", 1)[0]
    kept, fenced = [], False
    for line in body.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return "\n".join(kept).replace("**", "")


def test_the_changelog_names_the_version_the_package_carries() -> None:
    from quaestor import __version__

    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{__version__}]" in changelog, __version__
    assert "0.1.0.dev0" not in changelog
    assert "## [Unreleased]" in changelog


def test_the_version_the_package_carries_is_the_one_the_distribution_builds() -> None:
    """`pyproject.toml` takes the version from `__init__.py`, so there is one place to change."""
    from quaestor import __version__

    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in pyproject
    assert 'path = "src/quaestor/__init__.py"' in pyproject
    assert re.search(
        rf'^__version__ = "{re.escape(__version__)}"$',
        (REPO_ROOT / "src" / "quaestor" / "__init__.py").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert not __version__.endswith(".dev0")


def test_every_numeral_in_the_release_section_is_accounted_for_too() -> None:
    """The release entry states the headline, so its figures are swept like the README's."""
    remaining = release_section()
    for pattern in patterns():
        remaining = re.sub(pattern, " ", remaining)
    for literal in accounted_for():
        remaining = remaining.replace(literal, " ")
    stray = sorted({match.group(0) for match in NUMERAL.finditer(remaining)})
    assert not stray, f"the 0.1.0 entry prints numerals with no row: {stray}"
