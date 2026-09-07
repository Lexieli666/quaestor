"""The loader is the first thing a validator meets, so its error messages are the feature.

Spec section 3.2's acceptance list is the spine of this module: malformed YAML names the field, a
manifest hash mismatch raises `PackageError` naming the file, both shipped packages load, and a
package with an `after_outcome` feature yields a pre-run finding candidate. Both shipped
subjects load here -- `credit_default` and, from Phase 4, `msr_prepayment` -- along with the
hazard fixture, which is the package that still exercises the loader when a subject's own
`package.yaml` changes.

The `SEED.yaml` test is the one that protects the study: a variant package carries the answer key
beside `package.yaml`, and a pipeline that could read it would be measuring nothing.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from quaestor import DefectClass, PackageError, load_package
from quaestor.package import ConvexityExpectation, FeatureTiming, ModelType, PackageSpec

REPO_ROOT = Path(__file__).resolve().parent.parent
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"
HAZARD = REPO_ROOT / "tests" / "fixtures" / "hazard_package"


def copy_package(source: Path, tmp_path: Path) -> Path:
    destination = tmp_path / source.name
    shutil.copytree(source, destination)
    return destination


def edit(package_dir: Path, mutate: object) -> Path:
    """Rewrite a copied `package.yaml` through a callable that mutates the parsed mapping."""
    path = package_dir / "package.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert callable(mutate)
    mutate(raw)
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    return package_dir


# --- the two shipped packages -------------------------------------------------------------------


def test_the_credit_default_package_loads() -> None:
    package = load_package(CREDIT)
    assert package.spec.name == "credit_default"
    assert package.spec.model_type is ModelType.binary_classification
    assert package.spec.version == "1.0"
    assert len(package.spec.features) == 12
    assert package.code_dir == CREDIT / "code"


def test_the_credit_default_package_carries_the_notes_of_d017() -> None:
    package = load_package(CREDIT)
    notes = {f.name: f.note for f in package.spec.features}
    assert "near-collinear" in (notes["bill_last"] or "")
    assert notes["pay_ratio_mean_6m"] is None


def test_the_credit_default_package_declares_no_hazard_fields() -> None:
    spec = load_package(CREDIT).spec
    assert spec.scenarios is None
    assert spec.regime.column is None
    assert spec.splits.names() == ["train", "test"]


def test_the_hazard_fixture_loads_with_every_hazard_field() -> None:
    spec = load_package(HAZARD).spec
    assert spec.model_type is ModelType.discrete_time_hazard
    assert spec.data.time_column == "as_of_month"
    assert spec.regime.column == "rate_regime"
    assert spec.scenarios is not None
    assert spec.scenarios.rate_shocks_bp == [-300, -200, -100, 0, 100, 200, 300]
    assert spec.scenarios.horizon_months == 180
    assert spec.scenarios.servicing_fee_bp == pytest.approx(25.0)
    assert spec.scenarios.discount_rate_annual == pytest.approx(0.08)
    assert spec.scenarios.convexity_expectation is ConvexityExpectation.negative
    assert spec.splits.names() == ["train", "test", "out_of_time", "vintage_holdout"]
    assert spec.claims[0].value == pytest.approx(0.68)


def test_the_msr_prepayment_package_loads_with_the_scenarios_of_d037() -> None:
    spec = load_package(MSR).spec
    assert spec.name == "msr_prepayment"
    assert spec.model_type is ModelType.discrete_time_hazard
    assert spec.data.time_column == "period"
    assert spec.data.id_column == "loan_id"
    assert spec.regime.column == "rate_regime"
    assert spec.splits.names() == ["train", "test", "out_of_time", "vintage_holdout"]
    assert len(spec.features) == 12
    assert spec.scenarios is not None
    assert spec.scenarios.rate_shocks_bp == [-300, -200, -100, 0, 100, 200, 300]
    assert spec.scenarios.horizon_months == 180
    assert spec.scenarios.servicing_fee_bp == pytest.approx(25.0)
    assert spec.scenarios.discount_rate_annual == pytest.approx(0.08)
    assert spec.scenarios.convexity_expectation is ConvexityExpectation.negative
    assert spec.claims == []


def test_the_three_scenario_additions_are_required_not_defaulted(tmp_path: Path) -> None:
    # D-037: a threshold rule that supplies its own declaration is not a developer declaration,
    # so `X1` and the servicing valuation both fail loudly rather than inventing a number.
    for field in ("servicing_fee_bp", "discount_rate_annual", "convexity_expectation"):

        def mutate(raw: dict[str, object], field: str = field) -> None:
            scenarios = raw["scenarios"]
            assert isinstance(scenarios, dict)
            del scenarios[field]

        package_dir = edit(copy_package(MSR, tmp_path / field), mutate)
        with pytest.raises(PackageError, match=f"scenarios.{field}"):
            load_package(package_dir)


def test_a_scenario_block_without_the_base_case_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        scenarios = raw["scenarios"]
        assert isinstance(scenarios, dict)
        scenarios["rate_shocks_bp"] = [-100, 100]

    package_dir = edit(copy_package(MSR, tmp_path), mutate)
    with pytest.raises(PackageError, match="does not include 0"):
        load_package(package_dir)


def test_an_unknown_convexity_expectation_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        scenarios = raw["scenarios"]
        assert isinstance(scenarios, dict)
        scenarios["convexity_expectation"] = "sideways"

    package_dir = edit(copy_package(MSR, tmp_path), mutate)
    with pytest.raises(PackageError, match="convexity_expectation"):
        load_package(package_dir)


def test_a_package_can_be_addressed_by_its_yaml_file() -> None:
    assert load_package(CREDIT / "package.yaml").spec.name == "credit_default"


# --- SEED.yaml is invisible ----------------------------------------------------------------------


def test_load_package_ignores_a_seed_file_beside_package_yaml(tmp_path: Path) -> None:
    # Spec section 5: the evaluator reads SEED.yaml; the pipeline being measured must not.
    package_dir = copy_package(CREDIT, tmp_path)
    (package_dir / "SEED.yaml").write_text(
        "seeded:\n  class: L1\n  recipe: poison_leak_9f3c\n  params: {answer: POISONED}\n",
        encoding="utf-8",
    )
    package = load_package(package_dir)
    assert "POISONED" not in package.model_dump_json()
    assert "poison_leak_9f3c" not in package.model_dump_json()


# --- validation errors name the field and the file -----------------------------------------------


def test_malformed_yaml_names_the_file(tmp_path: Path) -> None:
    package_dir = copy_package(CREDIT, tmp_path)
    (package_dir / "package.yaml").write_text("name: [unclosed\n", encoding="utf-8")
    with pytest.raises(PackageError, match=r"package\.yaml is not valid YAML"):
        load_package(package_dir)


def test_an_unknown_field_names_the_field_and_the_file(tmp_path: Path) -> None:
    package_dir = edit(copy_package(CREDIT, tmp_path), lambda raw: raw.update(champion="logit"))
    with pytest.raises(PackageError, match=r"package\.yaml is not a valid package: champion:"):
        load_package(package_dir)


def test_a_misspelt_split_is_rejected_rather_than_ignored(tmp_path: Path) -> None:
    # The failure this forbids: a report that silently never looks at the holdout.
    def mutate(raw: dict[str, object]) -> None:
        splits = raw["splits"]
        assert isinstance(splits, dict)
        splits["vintage_holdouts"] = {"rule": "origination year 2012"}

    package_dir = edit(copy_package(HAZARD, tmp_path), mutate)
    with pytest.raises(PackageError, match="splits.vintage_holdouts"):
        load_package(package_dir)


def test_a_bad_enum_value_names_the_field(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        features = raw["features"]
        assert isinstance(features, list)
        features[2]["timing"] = "whenever"

    package_dir = edit(copy_package(CREDIT, tmp_path), mutate)
    with pytest.raises(PackageError, match="features.2.timing"):
        load_package(package_dir)


def test_an_unquoted_version_is_rejected(tmp_path: Path) -> None:
    # YAML reads 1.10 as a float, and 1.10 != 1.1 for a version string.
    package_dir = edit(copy_package(CREDIT, tmp_path), lambda raw: raw.update(version=1.10))
    with pytest.raises(PackageError, match="version:"):
        load_package(package_dir)


def test_a_hazard_package_without_a_time_column_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        data = raw["data"]
        assert isinstance(data, dict)
        data["time_column"] = None

    package_dir = edit(copy_package(HAZARD, tmp_path), mutate)
    with pytest.raises(PackageError, match="must declare data.time_column"):
        load_package(package_dir)


def test_scenarios_on_a_classifier_are_rejected(tmp_path: Path) -> None:
    package_dir = edit(
        copy_package(CREDIT, tmp_path),
        lambda raw: raw.update(
            scenarios={
                "rate_shocks_bp": [0],
                "horizon_months": 12,
                "servicing_fee_bp": 25,
                "discount_rate_annual": 0.08,
                "convexity_expectation": "negative",
            }
        ),
    )
    with pytest.raises(PackageError, match="discrete_time_hazard package only"):
        load_package(package_dir)


def test_a_duplicated_feature_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        features = raw["features"]
        assert isinstance(features, list)
        features.append({"name": "limit_bal", "timing": "at_origination"})

    package_dir = edit(copy_package(CREDIT, tmp_path), mutate)
    with pytest.raises(PackageError, match=r"declares \['limit_bal'\] more than once"):
        load_package(package_dir)


def test_the_target_declared_as_a_feature_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        features = raw["features"]
        assert isinstance(features, list)
        features.append({"name": "default_next_month", "timing": "at_origination"})

    package_dir = edit(copy_package(CREDIT, tmp_path), mutate)
    with pytest.raises(PackageError, match="total leakage"):
        load_package(package_dir)


def test_a_threshold_with_no_bound_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        thresholds = raw["thresholds"]
        assert isinstance(thresholds, list)
        thresholds.append({"metric": "ks", "split": "test"})

    package_dir = edit(copy_package(CREDIT, tmp_path), mutate)
    with pytest.raises(PackageError, match="declares neither min nor max"):
        load_package(package_dir)


def test_a_threshold_with_min_above_max_is_rejected(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        thresholds = raw["thresholds"]
        assert isinstance(thresholds, list)
        thresholds.append({"metric": "ks", "split": "test", "min": 0.9, "max": 0.1})

    package_dir = edit(copy_package(CREDIT, tmp_path), mutate)
    with pytest.raises(PackageError, match="above max"):
        load_package(package_dir)


def test_a_package_with_no_features_is_rejected(tmp_path: Path) -> None:
    package_dir = edit(copy_package(CREDIT, tmp_path), lambda raw: raw.update(features=[]))
    with pytest.raises(PackageError, match="features:"):
        load_package(package_dir)


def test_an_explicit_null_regime_block_reads_as_undeclared(tmp_path: Path) -> None:
    package_dir = edit(copy_package(CREDIT, tmp_path), lambda raw: raw.update(regime=None))
    assert load_package(package_dir).spec.regime.column is None


def test_a_null_required_block_still_names_its_field(tmp_path: Path) -> None:
    package_dir = edit(copy_package(CREDIT, tmp_path), lambda raw: raw.update(splits=None))
    with pytest.raises(PackageError, match="splits:"):
        load_package(package_dir)


# --- what is not a package -----------------------------------------------------------------------


def test_a_directory_without_package_yaml_says_so(tmp_path: Path) -> None:
    with pytest.raises(PackageError, match="it has no package.yaml"):
        load_package(tmp_path)


def test_a_path_that_does_not_exist_says_so(tmp_path: Path) -> None:
    with pytest.raises(PackageError, match="there is no model package at"):
        load_package(tmp_path / "nowhere")


def test_an_empty_package_yaml_says_so(tmp_path: Path) -> None:
    package_dir = copy_package(CREDIT, tmp_path)
    (package_dir / "package.yaml").write_text("", encoding="utf-8")
    with pytest.raises(PackageError, match="is empty"):
        load_package(package_dir)


def test_a_package_yaml_that_is_not_a_mapping_says_so(tmp_path: Path) -> None:
    package_dir = copy_package(CREDIT, tmp_path)
    (package_dir / "package.yaml").write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(PackageError, match="not a mapping of package fields"):
        load_package(package_dir)


def test_a_package_without_code_is_rejected(tmp_path: Path) -> None:
    package_dir = copy_package(CREDIT, tmp_path)
    shutil.rmtree(package_dir / "code")
    with pytest.raises(PackageError, match="has no code/ directory"):
        load_package(package_dir)


# --- the manifest ---------------------------------------------------------------------------------


def manifest_package(tmp_path: Path, digest: str) -> Path:
    def mutate(raw: dict[str, object]) -> None:
        data = raw["data"]
        assert isinstance(data, dict)
        data["manifest"] = {"train.csv": digest}

    return edit(copy_package(CREDIT, tmp_path), mutate)


def test_a_matching_manifest_verifies(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "train.csv").write_bytes(b"id,y\n1,0\n")
    digest = hashlib.sha256(b"id,y\n1,0\n").hexdigest()
    package = load_package(manifest_package(tmp_path, digest), data_dir=data_dir)
    assert package.data_dir == data_dir


def test_a_manifest_mismatch_names_the_file(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "train.csv").write_bytes(b"id,y\n1,1\n")
    digest = hashlib.sha256(b"id,y\n1,0\n").hexdigest()
    with pytest.raises(PackageError, match=r"train\.csv") as caught:
        load_package(manifest_package(tmp_path, digest), data_dir=data_dir)
    assert "shasum" in str(caught.value)


def test_a_manifest_naming_a_missing_file_says_so(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with pytest.raises(PackageError, match="which is not in"):
        load_package(manifest_package(tmp_path, "0" * 64), data_dir=data_dir)


def test_a_manifest_is_not_verified_without_a_data_dir(tmp_path: Path) -> None:
    # This is synthetic mode: there is no data directory, and Appendix D says the manifest was
    # not checked (DECISIONS D-022).
    package = load_package(manifest_package(tmp_path, "0" * 64))
    assert package.data_dir is None


def test_a_data_dir_that_is_not_a_directory_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(PackageError, match="is not a directory"):
        load_package(manifest_package(tmp_path, "0" * 64), data_dir=tmp_path / "absent")


def test_a_data_dir_without_a_manifest_verifies_nothing(tmp_path: Path) -> None:
    # The hazard fixture declares `manifest: null`, so there is nothing to verify and `data_dir`
    # stays unset. `credit_default` used to serve here and cannot any more: it declares the two
    # digests of its committed real sample.
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    assert load_package(HAZARD, data_dir=data_dir).data_dir is None


# --- the pre-run L1 candidate ---------------------------------------------------------------------


def test_a_clean_package_yields_no_pre_run_candidate() -> None:
    assert load_package(CREDIT).pre_run_candidates() == []


def test_an_after_outcome_feature_yields_a_pre_run_l1_candidate(tmp_path: Path) -> None:
    def mutate(raw: dict[str, object]) -> None:
        features = raw["features"]
        assert isinstance(features, list)
        features.append({"name": "collections_flag", "timing": "after_outcome"})

    package = load_package(edit(copy_package(CREDIT, tmp_path), mutate))
    (candidate,) = package.pre_run_candidates()
    assert candidate.defect_class is DefectClass.L1
    assert candidate.is_pre_run
    assert candidate.evidence == []
    assert "collections_flag" in candidate.detail
    assert "credit_default" in candidate.detail


def test_features_with_timing_selects_in_declaration_order() -> None:
    spec = load_package(CREDIT).spec
    assert [f.name for f in spec.features_with_timing(FeatureTiming.at_origination)] == [
        "limit_bal",
        "age",
    ]
    assert spec.feature_names[0] == "limit_bal"


def test_docs_dir_is_none_when_the_package_has_none(tmp_path: Path) -> None:
    package = load_package(copy_package(CREDIT, tmp_path))
    assert package.docs_dir is None
    (package.root / "docs").mkdir()
    assert load_package(package.root).docs_dir == package.root / "docs"


def test_package_spec_forbids_extra_fields_everywhere() -> None:
    # One assertion for the property the whole schema rests on.
    for model in (PackageSpec,):
        assert model.model_config["extra"] == "forbid"


def test_the_package_exposes_its_declared_name() -> None:
    assert load_package(CREDIT).name == "credit_default"


def test_the_null_block_validator_hands_on_anything_that_is_not_a_mapping() -> None:
    # It only tidies null blocks; the loader never reaches it with a non-mapping, but a direct
    # model_validate can, and pydantic's own message is better than one invented here.
    with pytest.raises(ValidationError, match="valid dictionary"):
        PackageSpec.model_validate(42)
