"""The spec 3.3 contract check, one malformation at a time.

`read_contract` is the gate between somebody else's code and every tool Quaestor has, so what
matters is not only that it rejects a bad file but that its message names the file and the field.
Each test below writes one valid output directory, breaks exactly one thing, and asserts on the
message a validator would have to act on.

The contract's own transformation is here too: `features.json` is a list on disk and an object in
the store, because a list has no `#n` to cite (DECISIONS D-026).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from quaestor import SandboxError, load_package
from quaestor.artifacts import ArtifactKind
from quaestor.package import PackageSpec
from quaestor.sandbox import features_artifact, read_contract, required_files

REPO_ROOT = Path(__file__).resolve().parent.parent
CREDIT_DEFAULT = REPO_ROOT / "subjects" / "credit_default"
HAZARD = REPO_ROOT / "tests" / "fixtures" / "hazard_package"

ROWS = ((1, 0, 0.10), (2, 1, 0.90), (3, 0, 0.25), (4, 1, 0.75))


@pytest.fixture
def spec() -> PackageSpec:
    """The credit subject's own `package.yaml`: two splits, twelve declared features."""
    return load_package(CREDIT_DEFAULT).spec


def write_valid(out_dir: Path, spec: PackageSpec) -> Path:
    """Write a minimal but valid contract for `spec`, with two rows per split."""
    out_dir.mkdir(parents=True, exist_ok=True)
    splits: dict[str, Any] = {}
    names = spec.splits.names()
    identifier = spec.data.id_column
    feature = spec.feature_names[0]
    time_column = spec.data.time_column
    for position, split in enumerate(names):
        rows = ROWS[2 * position % len(ROWS) :][:2]
        header = [identifier, *([time_column] if time_column else []), "y_true", "y_score"]
        lines = [",".join(header)]
        for row in rows:
            values = [str(row[0]), *(["1"] if time_column else []), str(row[1]), str(row[2])]
            lines.append(",".join(values))
        (out_dir / f"predictions_{split}.csv").write_text("\n".join(lines) + "\n")
        (out_dir / f"data_{split}.csv").write_text(
            f"{identifier},{feature},{spec.data.target}\n"
            + "".join(f"{row[0]},{row[2]},{row[1]}\n" for row in rows)
        )
        text = "\n".join(str(row[0]) for row in rows)
        splits[split] = {
            "n": len(rows),
            "event_rate": sum(row[1] for row in rows) / len(rows),
            "rows_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
    write_json(out_dir / "splits.json", splits)
    write_json(
        out_dir / "features.json",
        [
            {"name": item.name, "dtype": "float64", "timing": item.timing.value}
            for item in spec.features
        ],
    )
    write_json(out_dir / "metrics.json", {split: {"auc": 0.75} for split in names})
    summary: dict[str, Any] = {
        "coefficients": [{"feature": feature, "value": 1.25}],
        "removed": [{"feature": spec.feature_names[-1], "vif": 42.0}],
    }
    if spec.data.time_column is not None:
        summary["baseline_hazard"] = [{"month": 1, "hazard": 0.01}]
    write_json(out_dir / "model_summary.json", summary)
    if spec.scenarios is not None:
        write_json(
            out_dir / "projection.json",
            {
                "value_by_shock": {str(shock): 1.0 for shock in spec.scenarios.rate_shocks_bp},
                "balance_by_month": [{"month": 1, "balance": 100.0}],
            },
        )
    return out_dir


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def edit_json(path: Path, mutate: Any) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    write_json(path, payload)


# --- what is required ---------------------------------------------------------------------------


def test_a_classifier_requires_four_json_files_and_two_csvs_per_split(spec: PackageSpec) -> None:
    assert required_files(spec) == [
        "splits.json",
        "features.json",
        "metrics.json",
        "model_summary.json",
        "predictions_train.csv",
        "data_train.csv",
        "predictions_test.csv",
        "data_test.csv",
    ]


def test_a_hazard_package_requires_its_four_splits_and_a_projection() -> None:
    names = required_files(load_package(HAZARD).spec)
    assert "projection.json" in names
    assert "predictions_out_of_time.csv" in names
    assert "data_vintage_holdout.csv" in names
    assert len(names) == 13


def test_a_valid_contract_reads_back_with_its_kinds_and_logical_names(
    tmp_path: Path, spec: PackageSpec
) -> None:
    contract = read_contract(spec, write_valid(tmp_path, spec))
    kinds = {item.name: item.kind for item in contract}
    assert kinds["splits.json"] is ArtifactKind.json
    assert kinds["predictions_test.csv"] is ArtifactKind.table
    assert {item.logical_name for item in contract} == {
        "run.splits",
        "run.features",
        "run.metrics",
        "run.model_summary",
        "run.predictions_train",
        "run.data_train",
        "run.predictions_test",
        "run.data_test",
    }
    payload = {item.name: item.payload for item in contract}
    assert payload["predictions_test.csv"][0]["y_score"] == "0.25"
    assert payload["features.json"]["n"] == 12


def test_a_valid_hazard_contract_reads_back(tmp_path: Path) -> None:
    hazard = load_package(HAZARD).spec
    contract = read_contract(hazard, write_valid(tmp_path, hazard))
    assert "run.projection" in {item.logical_name for item in contract}


# --- the features artifact (DECISIONS D-026) -----------------------------------------------------


def test_the_features_artifact_carries_the_count_and_a_key_per_timing() -> None:
    artifact = features_artifact(
        [
            {"name": "a", "dtype": "float64", "timing": "at_origination"},
            {"name": "b", "dtype": "float64", "timing": "before_period_start"},
            {"name": "c", "dtype": "float64", "timing": "before_period_start"},
        ]
    )
    assert artifact == {
        "n": 3,
        "at_origination": 1,
        "before_period_start": 2,
        "during_period": 0,
        "after_outcome": 0,
        "items": [
            {"name": "a", "dtype": "float64", "timing": "at_origination"},
            {"name": "b", "dtype": "float64", "timing": "before_period_start"},
            {"name": "c", "dtype": "float64", "timing": "before_period_start"},
        ],
    }


# --- one malformation at a time ------------------------------------------------------------------


def test_a_missing_file_names_itself_and_lists_the_contract(
    tmp_path: Path, spec: PackageSpec
) -> None:
    out = write_valid(tmp_path, spec)
    (out / "metrics.json").unlink()
    with pytest.raises(SandboxError, match="did not write metrics.json") as raised:
        read_contract(spec, out)
    assert "splits.json" in str(raised.value)


def test_a_json_file_that_is_not_json_names_itself(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "model_summary.json").write_text("{")
    with pytest.raises(SandboxError, match=r"model_summary\.json.*not JSON"):
        read_contract(spec, out)


def test_a_json_file_that_is_not_utf8_names_itself(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "metrics.json").write_bytes(b"\xff\xfe{}")
    with pytest.raises(SandboxError, match="not UTF-8"):
        read_contract(spec, out)


def test_splits_json_must_be_an_object(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    write_json(out / "splits.json", [1, 2])
    with pytest.raises(SandboxError, match="the file is a list, not an object"):
        read_contract(spec, out)


def test_splits_json_must_cover_every_declared_split(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "splits.json", lambda payload: payload.pop("test"))
    with pytest.raises(SandboxError, match="no entry for the declared split 'test'"):
        read_contract(spec, out)


@pytest.mark.parametrize("key", ["n", "event_rate", "rows_hash"])
def test_a_split_entry_needs_all_three_fields(tmp_path: Path, spec: PackageSpec, key: str) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "splits.json", lambda payload: payload["train"].pop(key))
    with pytest.raises(SandboxError, match=f"'train' has no '{key}'"):
        read_contract(spec, out)


def test_a_split_entry_that_is_not_an_object_names_itself(
    tmp_path: Path, spec: PackageSpec
) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "splits.json", lambda payload: payload.__setitem__("train", 3))
    with pytest.raises(SandboxError, match="'train' is a int, not an object"):
        read_contract(spec, out)


@pytest.mark.parametrize("value", [-1, 2.5, True])
def test_a_split_row_count_must_be_a_non_negative_integer(
    tmp_path: Path, spec: PackageSpec, value: object
) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "splits.json", lambda payload: payload["train"].__setitem__("n", value))
    with pytest.raises(SandboxError, match="train.n is"):
        read_contract(spec, out)


def test_a_split_event_rate_must_be_a_rate(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "splits.json", lambda payload: payload["train"].__setitem__("event_rate", 1.4))
    with pytest.raises(SandboxError, match=r"train\.event_rate is 1.4, which is not a rate"):
        read_contract(spec, out)


def test_a_split_event_rate_must_be_a_number(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(
        out / "splits.json", lambda payload: payload["train"].__setitem__("event_rate", "high")
    )
    with pytest.raises(SandboxError, match=r"train\.event_rate is 'high', not a number"):
        read_contract(spec, out)


def test_a_rows_hash_must_be_a_full_sha256(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "splits.json", lambda payload: payload["train"].__setitem__("rows_hash", "abc"))
    with pytest.raises(SandboxError, match="64-character SHA-256"):
        read_contract(spec, out)


def test_features_json_must_be_a_non_empty_list(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    write_json(out / "features.json", [])
    with pytest.raises(SandboxError, match="it declares no features"):
        read_contract(spec, out)
    write_json(out / "features.json", {"limit_bal": "float64"})
    with pytest.raises(SandboxError, match="not a list of features"):
        read_contract(spec, out)


@pytest.mark.parametrize("key", ["name", "dtype", "timing"])
def test_a_feature_entry_needs_all_three_fields(
    tmp_path: Path, spec: PackageSpec, key: str
) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "features.json", lambda payload: payload[0].pop(key))
    with pytest.raises(SandboxError, match=f"element 0 has no '{key}'"):
        read_contract(spec, out)


def test_a_feature_timing_must_be_one_of_the_four(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "features.json", lambda payload: payload[0].__setitem__("timing", "later"))
    with pytest.raises(SandboxError, match="declares timing 'later'"):
        read_contract(spec, out)


def test_a_feature_the_package_does_not_declare_is_malformed(
    tmp_path: Path, spec: PackageSpec
) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "features.json", lambda payload: payload[0].__setitem__("name", "surprise"))
    with pytest.raises(SandboxError, match=r"names the features \['surprise'\]"):
        read_contract(spec, out)


def test_metrics_must_cover_every_declared_split_with_numbers(
    tmp_path: Path, spec: PackageSpec
) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "metrics.json", lambda payload: payload.pop("test"))
    with pytest.raises(SandboxError, match="no metrics for the declared split 'test'"):
        read_contract(spec, out)


def test_an_empty_metrics_block_is_malformed(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "metrics.json", lambda payload: payload.__setitem__("test", {}))
    with pytest.raises(SandboxError, match="'test' carries no metrics"):
        read_contract(spec, out)


def test_a_metric_that_is_not_a_number_names_itself(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "metrics.json", lambda payload: payload["test"].__setitem__("auc", "high"))
    with pytest.raises(SandboxError, match=r"test\.auc is 'high', not a number"):
        read_contract(spec, out)


def test_model_summary_must_carry_coefficients(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "model_summary.json", lambda payload: payload.pop("coefficients"))
    with pytest.raises(SandboxError, match="no 'coefficients'"):
        read_contract(spec, out)


def test_coefficients_must_be_a_list_of_named_numbers(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(
        out / "model_summary.json",
        lambda payload: payload.__setitem__("coefficients", {"limit_bal": 1.0}),
    )
    with pytest.raises(SandboxError, match="'coefficients' is a dict, not a list"):
        read_contract(spec, out)


def test_a_coefficient_needs_a_feature_and_a_value(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "model_summary.json", lambda payload: payload["coefficients"][0].pop("value"))
    with pytest.raises(SandboxError, match=r"coefficients\[0\] has no 'value'"):
        read_contract(spec, out)
    edit_json(
        out / "model_summary.json",
        lambda payload: payload["coefficients"].__setitem__(0, {"value": 1.0}),
    )
    with pytest.raises(SandboxError, match=r"coefficients\[0\] has no 'feature'"):
        read_contract(spec, out)


def test_a_removed_feature_needs_its_vif(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "model_summary.json", lambda payload: payload["removed"][0].pop("vif"))
    with pytest.raises(SandboxError, match=r"removed\[0\] has no 'vif'"):
        read_contract(spec, out)


def test_a_null_removed_list_is_allowed(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    edit_json(out / "model_summary.json", lambda payload: payload.__setitem__("removed", None))
    assert read_contract(spec, out)


def test_a_hazard_model_summary_must_carry_a_baseline_hazard(tmp_path: Path) -> None:
    hazard = load_package(HAZARD).spec
    out = write_valid(tmp_path, hazard)
    edit_json(out / "model_summary.json", lambda payload: payload.pop("baseline_hazard"))
    with pytest.raises(SandboxError, match="baseline_hazard"):
        read_contract(hazard, out)


def test_a_projection_needs_both_of_its_blocks(tmp_path: Path) -> None:
    hazard = load_package(HAZARD).spec
    out = write_valid(tmp_path, hazard)
    edit_json(out / "projection.json", lambda payload: payload.pop("balance_by_month"))
    with pytest.raises(SandboxError, match="no 'balance_by_month'"):
        read_contract(hazard, out)


def test_a_projection_must_cover_every_declared_shock(tmp_path: Path) -> None:
    hazard = load_package(HAZARD).spec
    out = write_valid(tmp_path, hazard)
    edit_json(out / "projection.json", lambda payload: payload["value_by_shock"].pop("-300"))
    with pytest.raises(SandboxError, match=r"no entry for the declared shocks \[-300\]"):
        read_contract(hazard, out)


def test_a_csv_with_no_rows_is_malformed(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("client_id,y_true,y_score\n")
    with pytest.raises(SandboxError, match="header but no rows"):
        read_contract(spec, out)


def test_an_empty_csv_is_malformed(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "data_test.csv").write_text("")
    with pytest.raises(SandboxError, match="no header row"):
        read_contract(spec, out)


def test_a_ragged_csv_names_its_line(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("client_id,y_true,y_score\n3,0\n")
    with pytest.raises(SandboxError, match="line 2 has fewer fields"):
        read_contract(spec, out)


def test_a_csv_that_is_not_utf8_names_itself(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "data_test.csv").write_bytes(b"client_id,limit_bal\n1,\xff\n")
    with pytest.raises(SandboxError, match="not UTF-8"):
        read_contract(spec, out)


def test_predictions_need_an_identifier_column(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("who,y_true,y_score\n3,0,0.2\n")
    with pytest.raises(SandboxError, match="no identifier column"):
        read_contract(spec, out)


def test_the_spec_33_spelling_of_the_identifier_is_accepted(
    tmp_path: Path, spec: PackageSpec
) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("id,y_true,y_score\n3,0,0.2\n")
    assert read_contract(spec, out)


def test_predictions_need_a_score_column(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("client_id,y_true\n3,0\n")
    with pytest.raises(SandboxError, match="no 'y_score' column"):
        read_contract(spec, out)


def test_a_hazard_prediction_file_needs_its_period_column(tmp_path: Path) -> None:
    hazard = load_package(HAZARD).spec
    out = write_valid(tmp_path, hazard)
    (out / "predictions_test.csv").write_text("loan_id,y_true,y_score\n3,0,0.2\n")
    with pytest.raises(SandboxError, match="data.time_column 'as_of_month'"):
        read_contract(hazard, out)


def test_a_score_outside_the_unit_interval_is_malformed(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("client_id,y_true,y_score\n3,0,1.4\n")
    with pytest.raises(SandboxError, match="y_score 1.4, which is not a probability"):
        read_contract(spec, out)


def test_a_score_that_is_not_a_number_names_its_line(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("client_id,y_true,y_score\n3,0,high\n")
    with pytest.raises(SandboxError, match="line 2 has y_score 'high'"):
        read_contract(spec, out)


def test_an_outcome_that_is_not_binary_is_malformed(tmp_path: Path, spec: PackageSpec) -> None:
    out = write_valid(tmp_path, spec)
    (out / "predictions_test.csv").write_text("client_id,y_true,y_score\n3,2,0.4\n")
    with pytest.raises(SandboxError, match="y_true '2', not 0 or 1"):
        read_contract(spec, out)


def test_a_data_file_needs_an_identifier_and_a_declared_feature(
    tmp_path: Path, spec: PackageSpec
) -> None:
    out = write_valid(tmp_path, spec)
    (out / "data_test.csv").write_text("client_id,something_else\n3,0.4\n")
    with pytest.raises(SandboxError, match="none of the declared features"):
        read_contract(spec, out)
    (out / "data_test.csv").write_text("who,limit_bal\n3,0.4\n")
    with pytest.raises(SandboxError, match="no identifier column"):
        read_contract(spec, out)
