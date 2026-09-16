"""Phase 10: the taxonomy, the seeded-defect generator and what each recipe actually produces.

`02-SPEC.md` section 5 and `04-SEEDED-DEFECT-STUDY.md` section 2. Every variant is built from the
clean subject, loaded through `load_package`, run through `run_model` in the sandbox and put
through a `rules_only` validation, and the assertions are the taxonomy's own `expected_signal`
column read as an acceptance test: the artifact the recipe was supposed to move, the bound it was
supposed to cross, and `04` section 4's detection criterion -- a finding of the seeded class at
severity at least medium in `findings.json`.

The whole suite of eighteen validations runs once, in a session fixture, and every test below
reads from it. Nothing here calls a model: `rules_only` emits no `llm_call` at all, and the one
test that drafts a report uses the offline provider.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from conftest import REPO_ROOT, load_module
from quaestor.cli import EXIT_FAILED_RUN, EXIT_OK, EXIT_USAGE
from quaestor.cli import main as cli_main
from quaestor.configs import SCREENED_CLASSES, synthetic_default_n
from quaestor.findings import PRE_RUN_TOOL, DefectClass, Severity, severity_rank
from quaestor.llm.offline import OfflineLLM
from quaestor.package import load_package
from quaestor.pipeline import ValidationRun, validate
from quaestor.tools import default_registry

sys.path.insert(0, str(REPO_ROOT / "eval"))
seed_module = load_module("quaestor_eval_seed_under_test", REPO_ROOT / "eval" / "seed.py")

TAXONOMY_FILE = REPO_ROOT / "eval" / "taxonomy.yaml"
CHECKLIST_FILE = REPO_ROOT / "docs" / "CHECKLIST.md"
SUBJECTS = REPO_ROOT / "subjects"

SEEDED_VARIANTS = 14
CONTROL_VARIANTS = 4
"""`04` section 2's variant plan: nine classes over two subjects, plus two controls each."""

POISON = "kestrel-99913-marmalade"
"""A value that appears nowhere in this repository, planted in one variant's `SEED.yaml`."""


Signal = tuple[str, str, float]
"""One row of the acceptance test: an artifact's logical name, a comparison and a bound."""

SIGNALS: dict[str, tuple[Signal, ...]] = {
    "credit__L1__after_outcome_declared": (("leakage.timing.n_flagged", ">=", 1.0),),
    "credit__L1__after_outcome_hidden": (
        ("leakage.target_corr.max_single_feature_auc", ">", 0.90),
    ),
    "msr__L1__eom_balance": (("leakage.target_corr.max_single_feature_auc", ">", 0.90),),
    "credit__L2__contamination": (("leakage.overlap.features", ">", 0.005),),
    "msr__L2__contamination": (("leakage.overlap.features", ">", 0.005),),
    "credit__R1__regime_flip": (("stability.bill_trend_6m.sign_flip", "==", 1.0),),
    "credit__C1__smote_uncalibrated": (("calibration.mean_rel_gap.test", ">", 0.25),),
    "msr__C1__oversampled_hazard": (("calibration.mean_rel_gap.test", ">", 0.25),),
    "credit__S1__segment_shift": (("psi.limit_bal", ">", 0.25),),
    "msr__S1__vintage_shift": (("psi.burnout", ">", 0.25),),
    "credit__M1__vif_reintroduced": (
        ("vif.max", ">", 10.0),
        ("condition_number", ">", 30.0),
    ),
    "credit__D1__test_only_missingness": (("profile.test.missing.max", ">", 0.10),),
    "credit__T1__false_claim": (("threshold.package.auc.test.min", ">", 0.0),),
    "msr__X1__projection_sign": (("scenario.convexity", ">", 0.0),),
}
"""The `expected_signal` column, as artifacts and bounds. `T1`'s bound is read from the variant."""

CONTROL_EXPECTATIONS: dict[str, set[tuple[str, str]]] = {
    "control_credit_clean": {("E1", "low")},
    "control_credit_perturbed": {("E1", "low")},
    "control_msr_clean": set(),
    "control_msr_perturbed": set(),
}
"""D-017 and D-047, and the rule that a harmless perturbation changes neither of them."""


def _compare(value: float, operator: str, bound: float) -> bool:
    """Apply one of the three comparisons a signal row may state."""
    if operator == ">":
        return value > bound
    if operator == ">=":
        return value >= bound
    return value == bound


@pytest.fixture(scope="session")
def taxonomy() -> Any:
    """`eval/taxonomy.yaml`, loaded."""
    return seed_module.load_taxonomy(TAXONOMY_FILE)


@pytest.fixture(scope="session")
def variants(tmp_path_factory: pytest.TempPathFactory, taxonomy: Any) -> dict[str, Path]:
    """Every variant the taxonomy declares, built once into a temporary tree."""
    root = tmp_path_factory.mktemp("variants")
    results = seed_module.build_all(
        taxonomy,
        root,
        subjects_dir=SUBJECTS,
        synthetic_n=seed_module.synthetic_sizes(taxonomy, None),
    )
    return {result.spec.id: result.root for result in results if result.built}


@pytest.fixture(scope="session")
def runs(
    tmp_path_factory: pytest.TempPathFactory, variants: dict[str, Path]
) -> dict[str, ValidationRun]:
    """One `rules_only` validation per variant, at each subject's documented panel size."""
    out = tmp_path_factory.mktemp("runs")
    completed: dict[str, ValidationRun] = {}
    for name, root in variants.items():
        package = load_package(root)
        completed[name] = validate(
            package,
            llm=OfflineLLM(),
            config="rules_only",
            synthetic=synthetic_default_n(package.name),
            out=out / name,
        )
    return completed


def _classes(run: ValidationRun) -> set[tuple[str, str]]:
    """The finding set of a run, as class and severity pairs."""
    return {(f.defect_class.value, f.severity.value) for f in run.findings.findings}


# --- the taxonomy itself -------------------------------------------------------------------------


def test_the_taxonomy_is_the_variant_plan_04_asks_for(taxonomy: Any) -> None:
    seeded = [spec for spec in taxonomy.specs if spec.defect_class is not None]
    controls = [spec for spec in taxonomy.specs if spec.is_control]
    assert len(seeded) == SEEDED_VARIANTS
    assert len(controls) == CONTROL_VARIANTS
    assert taxonomy.variants == SEEDED_VARIANTS + CONTROL_VARIANTS
    assert {spec.defect_class for spec in seeded} == {
        "L1",
        "L2",
        "R1",
        "C1",
        "S1",
        "M1",
        "D1",
        "T1",
        "X1",
    }
    assert {spec.subject for spec in taxonomy.specs} == set(taxonomy.subjects)


def test_every_seeded_row_carries_a_class_a_signal_and_a_sentence(taxonomy: Any) -> None:
    for spec in taxonomy.specs:
        if spec.is_control:
            continue
        assert DefectClass(spec.defect_class)
        assert spec.expected_signal and spec.met_where
        assert spec.id in SIGNALS, f"{spec.id} has no acceptance test in this module"


def test_no_recipe_is_named_that_the_generator_does_not_implement(taxonomy: Any) -> None:
    assert {spec.recipe for spec in taxonomy.specs} <= set(seed_module.RECIPES)
    assert set(seed_module.RECIPES) == {spec.recipe for spec in taxonomy.specs}


def test_the_checklist_names_only_real_tools_and_the_taxonomy_s_classes() -> None:
    """The two columns of `docs/CHECKLIST.md` section 1 this phase was allowed to correct."""
    text = CHECKLIST_FILE.read_text(encoding="utf-8")
    registry = set(default_registry().names())
    rows = [line for line in text.splitlines() if line.startswith("| ") and line.count("|") == 5]
    named_tools: set[str] = set()
    named_classes: set[str] = set()
    for row in rows[2:]:
        _, _, tools, classes = (cell.strip() for cell in row.strip("|").split("|"))
        named_tools |= {word.strip("`") for word in tools.split(",") if word.strip() != "—"}
        named_classes |= {word.strip() for word in classes.split(",") if word.strip() != "—"}
    named_tools = {name.split(" ")[0].strip("`") for name in named_tools}
    named_tools -= {""}
    named_classes -= {""}
    assert named_tools <= registry, sorted(named_tools - registry)
    assert named_classes <= {member.value for member in DefectClass}


# --- what each recipe produces --------------------------------------------------------------------


@pytest.mark.parametrize("variant", sorted(SIGNALS))
def test_each_recipe_produces_its_expected_signal(
    variant: str, runs: dict[str, ValidationRun], variants: dict[str, Path]
) -> None:
    """The `expected_signal` column, read as an acceptance test over the store."""
    run = runs[variant]
    assert "run.stdout" in run.store, "the variant did not run through the sandbox"
    for name, operator, bound in SIGNALS[variant]:
        assert name in run.store, f"{variant}: {name} is not in the store"
        value = float(run.store.value(name))
        if variant == "credit__T1__false_claim":
            bound = float(run.store.value("metrics.test.auc"))
        assert _compare(value, operator, bound), (
            f"{variant}: {name} is {value}, not {operator} {bound}"
        )


@pytest.mark.parametrize("variant", sorted(SIGNALS))
def test_each_seeded_class_is_detected_at_severity_at_least_medium(
    variant: str, runs: dict[str, ValidationRun], taxonomy: Any
) -> None:
    """`04` section 4's detection criterion, on the configuration that calls no model."""
    spec = next(row for row in taxonomy.specs if row.id == variant)
    run = runs[variant]
    matching = [
        finding
        for finding in run.findings.findings
        if finding.defect_class.value == spec.defect_class
    ]
    assert matching, f"{variant}: no {spec.defect_class} finding in {_classes(run)}"
    assert any(
        severity_rank(finding.severity) <= severity_rank(Severity.medium) for finding in matching
    )
    for finding in matching:
        tools = set(finding.tool.split("+"))
        assert tools <= set(SCREENED_CLASSES) | {PRE_RUN_TOOL}
        screening = tools & set(SCREENED_CLASSES)
        assert screening
        assert all(finding.defect_class in SCREENED_CLASSES[tool] for tool in screening)


# --- the controls ---------------------------------------------------------------------------------


@pytest.mark.parametrize("variant", sorted(CONTROL_EXPECTATIONS))
def test_a_control_raises_exactly_what_the_unperturbed_subject_raises(
    variant: str, runs: dict[str, ValidationRun]
) -> None:
    """D-017 and D-047: `{E1 low}` and `{}`, and the perturbation changes neither."""
    assert _classes(runs[variant]) == CONTROL_EXPECTATIONS[variant]


def test_every_control_carries_the_baseline_d161_measured(taxonomy: Any) -> None:
    """D-161: a control's baseline is measured per data mode, and a seeded row has none."""
    by_id = {spec.id: spec for spec in taxonomy.specs}

    credit_clean = by_id["control_credit_clean"].baseline
    assert credit_clean == {
        "synthetic": [{"class": "E1", "severity": "low"}],  # D-017
        "real": [],  # eval/results/first-live/credit/
    }

    msr_clean = by_id["control_msr_clean"].baseline
    assert msr_clean is not None
    assert msr_clean["synthetic"] == []  # D-047
    assert msr_clean["real"] == [
        {
            "class": "C1",
            "severity": "medium",
            "splits": ["out_of_time", "vintage_holdout"],
            "evidence": [
                "calibration_slope.out_of_time",
                "calibration.mean_rel_gap.out_of_time",
                "calibration.mean_rel_gap.vintage_holdout",
            ],
        }
    ]

    # The perturbed pair is a Phase 12 pre-flight item and says so by carrying nothing.
    assert by_id["control_credit_perturbed"].baseline is None
    assert by_id["control_msr_perturbed"].baseline is None

    # A baseline answers a question about a control, so no seeded row has one.
    for spec in taxonomy.specs:
        if not spec.is_control:
            assert spec.baseline is None, spec.id


def test_the_baseline_reaches_the_scorer_and_not_the_variant(tmp_path: Path, taxonomy: Any) -> None:
    """`SEED.yaml` is unchanged by D-161: the baseline is the scorer's input, not the variant's."""
    spec = next(row for row in taxonomy.specs if row.id == "control_msr_clean")
    assert spec.baseline is not None
    target = tmp_path / spec.id
    seed_module.seed(SUBJECTS / spec.subject, spec, target, taxonomy=taxonomy)
    payload = yaml.safe_load((target / seed_module.SEED_FILE).read_text(encoding="utf-8"))
    assert "baseline" not in payload
    assert "calibration_slope.out_of_time" not in (target / seed_module.SEED_FILE).read_text(
        encoding="utf-8"
    )


def test_the_clean_control_is_a_byte_copy_of_the_subject(variants: dict[str, Path]) -> None:
    for control, subject in (
        ("control_credit_clean", "credit_default"),
        ("control_msr_clean", "msr_prepayment"),
    ):
        root = variants[control]
        for path in sorted((SUBJECTS / subject).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            copy = root / path.relative_to(SUBJECTS / subject)
            assert copy.read_bytes() == path.read_bytes(), copy


def test_the_perturbed_control_renames_the_columns_and_moves_no_number(
    runs: dict[str, ValidationRun],
) -> None:
    clean = runs["control_credit_clean"]
    perturbed = runs["control_credit_perturbed"]
    assert "psi.f_limit_bal" in perturbed.store
    assert "psi.limit_bal" in clean.store
    for name in ("metrics.test.auc", "vif.max", "condition_number", "psi.max"):
        assert perturbed.store.value(name) == pytest.approx(clean.store.value(name), abs=1e-9)


# --- idempotence and provenance ------------------------------------------------------------------


def test_applying_a_recipe_twice_writes_the_same_bytes(tmp_path: Path, taxonomy: Any) -> None:
    spec = next(row for row in taxonomy.specs if row.id == "credit__M1__vif_reintroduced")
    first = tmp_path / "first"
    second = tmp_path / "second"
    for target in (first, second):
        seed_module.seed(SUBJECTS / spec.subject, spec, target, taxonomy=taxonomy)
    assert seed_module.directory_digest(first) == seed_module.directory_digest(second)
    seed_module.seed(SUBJECTS / spec.subject, spec, first, taxonomy=taxonomy)
    assert seed_module.directory_digest(first) == seed_module.directory_digest(second)


def test_a_recipe_whose_anchor_moved_is_an_error_rather_than_a_no_op(
    tmp_path: Path, taxonomy: Any
) -> None:
    spec = next(row for row in taxonomy.specs if row.id == "credit__M1__vif_reintroduced")
    target = tmp_path / "variant"
    seed_module.seed(SUBJECTS / spec.subject, spec, target, taxonomy=taxonomy)
    variant = seed_module.Variant(target)
    with pytest.raises(ValueError, match="anchor appears 0 time"):
        variant.replace("code/run.py", "a line no subject has", "x", note="never")


def test_seed_yaml_records_the_recipe_and_package_yaml_does_not(
    variants: dict[str, Path], taxonomy: Any
) -> None:
    root = variants["credit__L2__contamination"]
    payload = yaml.safe_load((root / seed_module.SEED_FILE).read_text(encoding="utf-8"))
    assert payload["seeded"]["class"] == "L2"
    assert payload["seeded"]["recipe"] == "duplicate_test_into_train"
    assert payload["seeded"]["params"]["fresh_ids"] is True
    assert payload["taxonomy"]["sha256"] == taxonomy.digest()
    assert payload["applied"], "SEED.yaml records what the recipe did"
    package = yaml.safe_load((root / "package.yaml").read_text(encoding="utf-8"))
    assert "seeded" not in package


def test_load_package_does_not_open_the_answer_key(
    variants: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[str] = []
    original = Path.read_text

    def spy(self: Path, *args: Any, **kwargs: Any) -> str:
        opened.append(self.name)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", spy)
    load_package(variants["credit__T1__false_claim"])
    assert "package.yaml" in opened
    assert seed_module.SEED_FILE not in opened


def test_a_value_planted_in_seed_yaml_reaches_nothing_the_pipeline_writes(
    tmp_path: Path, variants: dict[str, Path]
) -> None:
    """The poison test of spec section 5, over a whole `--llm fake` validation."""
    root = variants["credit__L1__after_outcome_hidden"]
    key = root / seed_module.SEED_FILE
    key.write_text(key.read_text(encoding="utf-8") + f"poison: {POISON}\n", encoding="utf-8")
    package = load_package(root)
    out = tmp_path / "run"
    run = validate(
        package,
        llm=OfflineLLM(),
        config="full_agent",
        synthetic=synthetic_default_n(package.name),
        out=out,
    )
    assert POISON in key.read_text(encoding="utf-8")
    assert POISON not in run.report_path.read_text(encoding="utf-8")
    assert POISON not in (out / "trace.jsonl").read_text(encoding="utf-8")
    assert POISON not in json.dumps(run.claims.model_dump(mode="json"))
    assert POISON not in json.dumps(run.findings.model_dump(mode="json"))
    for name in run.store.names():
        assert POISON not in json.dumps(run.store.load(name), default=str)


# --- the command line ----------------------------------------------------------------------------


def test_study_build_writes_every_variant_and_study_run_is_still_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "variants"
    assert (
        cli_main(["study", "build", "--taxonomy", str(TAXONOMY_FILE), "--out", str(out)]) == EXIT_OK
    )
    printed = capsys.readouterr().out
    assert f"{SEEDED_VARIANTS + CONTROL_VARIANTS} variant(s) under" in printed
    assert (out / "credit__T1__false_claim" / seed_module.SEED_FILE).is_file()
    with pytest.raises(SystemExit) as exit_code:
        cli_main(["study", "run"])
    assert exit_code.value.code == EXIT_USAGE


def test_study_build_without_a_generator_beside_the_taxonomy_says_so(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    elsewhere = tmp_path / "eval" / "taxonomy.yaml"
    elsewhere.parent.mkdir(parents=True)
    elsewhere.write_text(TAXONOMY_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    code = cli_main(["study", "build", "--taxonomy", str(elsewhere), "--out", str(tmp_path / "v")])
    assert code == EXIT_USAGE
    assert "seed.py" in capsys.readouterr().err


def test_study_build_names_a_taxonomy_that_is_not_there(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli_main(
        ["study", "build", "--taxonomy", str(tmp_path / "nope.yaml"), "--out", str(tmp_path / "v")]
    )
    assert code == EXIT_USAGE
    assert "no taxonomy at" in capsys.readouterr().err


def test_study_build_names_a_subjects_directory_that_is_not_there(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli_main(
        [
            "study",
            "build",
            "--taxonomy",
            str(TAXONOMY_FILE),
            "--subjects",
            str(tmp_path / "nowhere"),
            "--out",
            str(tmp_path / "v"),
        ]
    )
    assert code == EXIT_USAGE
    assert "no subjects directory at" in capsys.readouterr().err


def test_a_taxonomy_that_names_an_unknown_recipe_is_a_failed_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    checkout = tmp_path / "checkout"
    (checkout / "eval").mkdir(parents=True)
    (checkout / "eval" / "seed.py").write_text(
        (REPO_ROOT / "eval" / "seed.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    broken = checkout / "eval" / "taxonomy.yaml"
    broken.write_text(
        TAXONOMY_FILE.read_text(encoding="utf-8").replace(
            "recipe: train_on_segment", "recipe: no_such_recipe"
        ),
        encoding="utf-8",
    )
    code = cli_main(
        [
            "study",
            "build",
            "--taxonomy",
            str(broken),
            "--subjects",
            str(SUBJECTS),
            "--out",
            str(tmp_path / "v"),
        ]
    )
    assert code == EXIT_FAILED_RUN
    assert "no_such_recipe" in capsys.readouterr().err


def test_the_generator_runs_as_a_script_and_takes_a_panel_size(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "variants"
    code = seed_module.main(
        [
            "--taxonomy",
            str(TAXONOMY_FILE),
            "--subjects",
            str(SUBJECTS),
            "--out",
            str(out),
            "--synthetic",
            "600",
        ]
    )
    assert code == 0
    assert "18 variant(s) built" in capsys.readouterr().out
    payload = yaml.safe_load(
        (out / "control_msr_clean" / seed_module.SEED_FILE).read_text(encoding="utf-8")
    )
    assert payload["synthetic_n"] == 600
    assert payload["seeded"]["class"] is None


def _checkout_with(tmp_path: Path, taxonomy_text: str) -> Path:
    """A directory holding the generator and one taxonomy, as `study build` expects to find them."""
    evaluation = tmp_path / "checkout" / "eval"
    evaluation.mkdir(parents=True)
    (evaluation / "seed.py").write_text(
        (REPO_ROOT / "eval" / "seed.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    path = evaluation / "taxonomy.yaml"
    path.write_text(taxonomy_text, encoding="utf-8")
    return path


def test_a_dropped_row_is_recorded_and_not_built(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`04` section 2: a recipe that cannot produce its signal is dropped, never tuned until it
    fires. Nothing in the committed taxonomy is dropped today; this is the path if one ever is."""
    reason = "the signal lands on a comparison this pipeline reports and does not test"
    path = _checkout_with(
        tmp_path,
        TAXONOMY_FILE.read_text(encoding="utf-8").replace(
            "    recipe: train_pre_test_post",
            f"    recipe: train_pre_test_post\n    status: dropped\n    dropped_reason: {reason}",
        ),
    )
    out = tmp_path / "variants"
    code = cli_main(
        ["study", "build", "--taxonomy", str(path), "--subjects", str(SUBJECTS), "--out", str(out)]
    )
    assert code == EXIT_OK
    printed = capsys.readouterr().out
    assert f"msr__S1__vintage_shift: dropped ({reason})" in printed
    assert f"{SEEDED_VARIANTS + CONTROL_VARIANTS - 1} variant(s) under" in printed
    assert "1 dropped" in printed
    assert not (out / "msr__S1__vintage_shift").exists()

    taxonomy = seed_module.load_taxonomy(path)
    dropped = next(spec for spec in taxonomy.dropped)
    assert [spec.id for spec in taxonomy.buildable] == [
        spec.id for spec in taxonomy.specs if spec.id != dropped.id
    ]
    with pytest.raises(ValueError, match="status: dropped"):
        seed_module.seed(SUBJECTS / dropped.subject, dropped, tmp_path / "never")


def test_a_dropped_row_without_a_reason_is_refused(tmp_path: Path) -> None:
    path = _checkout_with(
        tmp_path,
        TAXONOMY_FILE.read_text(encoding="utf-8").replace(
            "    recipe: train_pre_test_post",
            "    recipe: train_pre_test_post\n    status: dropped",
        ),
    )
    with pytest.raises(ValueError, match="dropped with no dropped_reason"):
        seed_module.load_taxonomy(path)
