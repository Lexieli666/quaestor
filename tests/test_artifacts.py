"""The store is where "every number carries a citation" stops being a slogan.

Spec section 3.4's acceptance list: identical payload gives an identical hash across processes, a
citation to a missing hash is detected, and `value()` on a table raises with the table's columns
listed. The cross-process test spawns a real interpreter, because the property being asserted is
exactly the one that a same-process test cannot see.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from quaestor import ArtifactError, ArtifactStore
from quaestor.artifacts import INDEX_FILE, Artifact, ArtifactKind, canonical_bytes

DECILES = [
    {"decile": 1, "count": 150, "event_rate": 0.493, "lift": 2.24},
    {"decile": 2, "count": 150, "event_rate": 0.347, "lift": 1.58},
]
MODEL_SUMMARY = {
    "coefficients": [
        {"feature": "delinq_last", "value": 0.612},
        {"feature": "utilisation", "value": 0.487},
    ],
    "removed": [{"feature": "bill_last", "vif": 41.7}],
    "intercept": -1.2649,
}


def store(tmp_path: Path) -> ArtifactStore:
    return ArtifactStore(tmp_path / "artifacts")


# --- put, get, index ------------------------------------------------------------------------------


def test_put_returns_an_artifact_with_a_sixteen_character_hash(tmp_path: Path) -> None:
    artifact = store(tmp_path).put("metrics.test.auc", 0.7412, ArtifactKind.scalar, "test AUC")
    assert len(artifact.hash) == 16
    assert artifact.name == "metrics.test.auc"
    assert artifact.kind is ArtifactKind.scalar
    assert artifact.summary == "test AUC"
    assert artifact.path.is_file()


def test_the_citation_an_artifact_renders_quotes_eight_characters(tmp_path: Path) -> None:
    artifact = store(tmp_path).put("metrics.test.auc", 0.7412, "scalar")
    assert artifact.citation() == f"[[art:{artifact.hash[:8]}:metrics.test.auc]]"
    assert artifact.citation("1.lift") == f"[[art:{artifact.hash[:8]}:metrics.test.auc#1.lift]]"
    assert artifact.short_hash == artifact.hash[:8]


def test_the_index_maps_names_to_hashes_and_scalar_values(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar", "test AUC")
    target.put("deciles.test", DECILES, "table", "decile table")
    index = json.loads((tmp_path / "artifacts" / INDEX_FILE).read_text(encoding="utf-8"))
    assert index["schema_version"] == 1
    assert index["artifacts"]["metrics.test.auc"]["value"] == pytest.approx(0.7412)
    assert index["artifacts"]["deciles.test"]["value"] is None
    assert index["artifacts"]["deciles.test"]["kind"] == "table"


def test_the_index_is_written_in_sorted_order(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("psi.utilisation", 0.021, "scalar")
    target.put("metrics.test.auc", 0.7412, "scalar")
    index = json.loads((tmp_path / "artifacts" / INDEX_FILE).read_text(encoding="utf-8"))
    assert list(index["artifacts"]) == ["metrics.test.auc", "psi.utilisation"]


def test_a_store_reopens_its_index(tmp_path: Path) -> None:
    store(tmp_path).put("metrics.test.auc", 0.7412, "scalar")
    reopened = store(tmp_path)
    assert reopened.value("metrics.test.auc") == pytest.approx(0.7412)
    assert len(reopened) == 1
    assert "metrics.test.auc" in reopened


def test_an_unreadable_index_says_so(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    root.mkdir()
    (root / INDEX_FILE).write_text("{not json", encoding="utf-8")
    with pytest.raises(ArtifactError, match="not a readable artifact index"):
        ArtifactStore(root)


def test_get_resolves_a_short_hash(tmp_path: Path) -> None:
    target = store(tmp_path)
    artifact = target.put("metrics.test.auc", 0.7412, "scalar")
    assert target.get(artifact.short_hash) == artifact
    assert target.get(artifact.hash) == artifact


def test_get_rejects_a_hash_shorter_than_a_citation_quotes(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar")
    with pytest.raises(ArtifactError, match="shorter than the 8 characters"):
        target.get("4bb1")


def test_get_on_a_missing_hash_says_so(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="no artifact in"):
        store(tmp_path).get("deadbeef")


def test_entry_on_a_missing_name_suggests_nearby_names(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar")
    with pytest.raises(ArtifactError, match=r"names beginning 'metrics\.test'") as caught:
        target.entry("metrics.test.aucc")
    assert "metrics.test.auc" in str(caught.value)


def test_names_are_sorted(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("psi.max", 0.021, "scalar")
    target.put("metrics.test.auc", 0.7412, "scalar")
    assert target.names() == ["metrics.test.auc", "psi.max"]


# --- naming rules ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "metrics.test.auc",
        "threshold.E1.delta_auc",
        "scenario.value_change.-300",
        "condition_number",
        "rule.calibration_first_event_rate",
    ],
)
def test_the_logical_names_of_the_golden_report_are_accepted(tmp_path: Path, name: str) -> None:
    assert store(tmp_path).put(name, 1.0, "scalar").name == name


@pytest.mark.parametrize("name", ["Metrics.test.auc", "metrics..auc", "", "metrics test", "1.auc"])
def test_a_malformed_logical_name_is_rejected(tmp_path: Path, name: str) -> None:
    with pytest.raises(ArtifactError, match="not a logical artifact name"):
        store(tmp_path).put(name, 1.0, "scalar")


# --- canonical bytes and cross-process stability --------------------------------------------------


def test_identical_payloads_hash_identically(tmp_path: Path) -> None:
    first = ArtifactStore(tmp_path / "a").put("metrics.test.auc", 0.7412, "scalar")
    second = ArtifactStore(tmp_path / "b").put("metrics.test.auc", 0.7412, "scalar")
    assert first.hash == second.hash


def test_the_name_is_part_of_the_address(tmp_path: Path) -> None:
    # Two splits with the same event rate are two artifacts, so a finding's evidence can say
    # which split it rested on (DECISIONS D-023).
    target = store(tmp_path)
    train = target.put("metrics.train.event_rate", 0.22, "scalar")
    test = target.put("metrics.test.event_rate", 0.22, "scalar")
    assert train.hash != test.hash


def test_a_different_value_gives_a_different_hash(tmp_path: Path) -> None:
    target = store(tmp_path)
    first = target.put("metrics.test.auc", 0.7412, "scalar")
    second = ArtifactStore(tmp_path / "other").put("metrics.test.auc", 0.7413, "scalar")
    assert first.hash != second.hash


def test_json_key_order_does_not_change_the_hash(tmp_path: Path) -> None:
    first = ArtifactStore(tmp_path / "a").put("run.metrics", {"a": 1, "b": 2}, "json")
    second = ArtifactStore(tmp_path / "b").put("run.metrics", {"b": 2, "a": 1}, "json")
    assert first.hash == second.hash


def test_floats_are_rounded_to_ten_significant_digits(tmp_path: Path) -> None:
    # 1/3 and its ten-significant-digit rounding are one artifact: identical results must hash
    # identically even when one of them came back through a CSV.
    first = ArtifactStore(tmp_path / "a").put("psi.utilisation", 1 / 3, "scalar")
    second = ArtifactStore(tmp_path / "b").put("psi.utilisation", 0.3333333333, "scalar")
    assert first.hash == second.hash
    assert first.path.read_text(encoding="utf-8") == "0.3333333333\n"


def test_the_hash_is_stable_across_processes(tmp_path: Path) -> None:
    script = (
        "import sys;"
        "from quaestor.artifacts import ArtifactStore;"
        "print(ArtifactStore(sys.argv[1]).put('deciles.test', "
        f"{DECILES!r}, 'table').hash)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path / "child")],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    here = ArtifactStore(tmp_path / "here").put("deciles.test", DECILES, "table")
    assert completed.stdout.strip() == here.hash


def test_a_table_is_written_as_canonical_csv() -> None:
    assert canonical_bytes(ArtifactKind.table, DECILES).decode("utf-8") == (
        "decile,count,event_rate,lift\n1,150,0.493,2.24\n2,150,0.347,1.58\n"
    )


def test_a_json_artifact_is_written_with_sorted_keys() -> None:
    assert canonical_bytes(ArtifactKind.json, {"b": 1.5, "a": [1, 2]}).decode("utf-8") == (
        '{"a":[1,2],"b":1.5}\n'
    )


def test_a_figure_is_written_verbatim(tmp_path: Path) -> None:
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    artifact = store(tmp_path).put("figure.calibration", png, "figure")
    assert artifact.path.suffix == ".png"
    assert artifact.path.read_bytes() == png
    assert store(tmp_path).load("figure.calibration") == png


# --- payloads that have no canonical form ---------------------------------------------------------


def test_a_scalar_must_be_a_number(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="holds a number, not str"):
        store(tmp_path).put("metrics.test.auc", "0.7412", "scalar")


def test_a_boolean_is_not_a_scalar(tmp_path: Path) -> None:
    # True is an int in Python; a scalar artifact of 1 that came from a flag is not a measurement.
    with pytest.raises(ArtifactError, match="holds a number, not bool"):
        store(tmp_path).put("leakage.clean", True, "scalar")


def test_nan_has_no_canonical_form(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="has no canonical form"):
        store(tmp_path).put("metrics.test.auc", float("nan"), "scalar")


def test_infinity_has_no_canonical_form(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="has no canonical form"):
        store(tmp_path).put("vif.utilisation", float("inf"), "scalar")


def test_a_table_needs_rows(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="needs at least one row"):
        store(tmp_path).put("deciles.test", [], "table")


def test_a_table_needs_columns(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="needs at least one column"):
        store(tmp_path).put("deciles.test", [{}], "table")


def test_a_ragged_table_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="row 2 of the table"):
        store(tmp_path).put("deciles.test", [{"a": 1, "b": 2}, {"a": 3}], "table")


def test_a_table_payload_must_be_rows(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="sequence of row mappings"):
        store(tmp_path).put("deciles.test", {"decile": [1, 2]}, "table")


def test_a_figure_payload_must_be_bytes(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="holds PNG bytes"):
        store(tmp_path).put("figure.calibration", "not bytes", "figure")


def test_a_json_payload_must_be_json(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="cannot hold object"):
        store(tmp_path).put("run.metrics", {"when": object()}, "json")


def test_a_table_cell_that_is_none_is_written_empty(tmp_path: Path) -> None:
    artifact = store(tmp_path).put("t.x", [{"k": "a", "v": None, "flag": True}], "table")
    assert artifact.path.read_text(encoding="utf-8") == "k,v,flag\na,,true\n"


# --- idempotence and replacement ------------------------------------------------------------------


def test_storing_the_same_payload_twice_is_idempotent(tmp_path: Path) -> None:
    target = store(tmp_path)
    first = target.put("metrics.test.auc", 0.7412, "scalar", "test AUC")
    second = target.put("metrics.test.auc", 0.7412, "scalar", "test AUC")
    assert first == second
    assert len(target) == 1


def test_replacing_a_name_with_a_different_payload_is_refused(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar")
    with pytest.raises(ArtifactError, match="cannot be replaced"):
        target.put("metrics.test.auc", 0.7413, "scalar")


# --- value(), load() and columns() ----------------------------------------------------------------


def test_value_returns_a_scalar(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar")
    assert target.value("metrics.test.auc") == pytest.approx(0.7412)


def test_value_on_a_table_lists_its_columns(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("deciles.test", DECILES, "table")
    with pytest.raises(ArtifactError, match=r"columns \['decile', 'count', 'event_rate', 'lift'\]"):
        target.value("deciles.test")


def test_value_on_a_json_artifact_shows_the_path_syntax(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("run.model_summary", MODEL_SUMMARY, "json")
    with pytest.raises(ArtifactError, match=r"#<dotted\.path>"):
        target.value("run.model_summary")


def test_value_on_a_figure_says_there_is_nothing_to_cite(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("figure.calibration", b"\x89PNG", "figure")
    with pytest.raises(ArtifactError, match="is a figure and has no value"):
        target.value("figure.calibration")


def test_value_on_a_hand_edited_index_says_so(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar")
    index_path = tmp_path / "artifacts" / INDEX_FILE
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["artifacts"]["metrics.test.auc"]["value"] = None
    index_path.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(ArtifactError, match="edited by hand"):
        ArtifactStore(tmp_path / "artifacts").value("metrics.test.auc")


def test_load_returns_table_rows(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("deciles.test", DECILES, "table")
    rows = target.load("deciles.test")
    assert rows[0]["lift"] == "2.24"


def test_load_returns_a_json_object(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("run.model_summary", MODEL_SUMMARY, "json")
    assert target.load("run.model_summary")["intercept"] == pytest.approx(-1.2649)


def test_load_says_so_when_the_payload_is_missing(tmp_path: Path) -> None:
    target = store(tmp_path)
    artifact = target.put("metrics.test.auc", 0.7412, "scalar")
    artifact.path.unlink()
    with pytest.raises(ArtifactError, match="the store at .* and its index disagree"):
        target.load("metrics.test.auc")


def test_columns_names_the_row_key_first(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("deciles.test", DECILES, "table")
    assert target.columns("deciles.test")[0] == "decile"


def test_columns_on_a_non_table_is_refused(tmp_path: Path) -> None:
    target = store(tmp_path)
    target.put("metrics.test.auc", 0.7412, "scalar")
    with pytest.raises(ArtifactError, match="is a scalar, not a table"):
        target.columns("metrics.test.auc")


def test_artifact_is_frozen(tmp_path: Path) -> None:
    artifact = store(tmp_path).put("metrics.test.auc", 0.7412, "scalar")
    with pytest.raises(ValueError, match="frozen"):
        artifact.hash = "0" * 16


def test_artifact_round_trips_through_the_store(tmp_path: Path) -> None:
    target = store(tmp_path)
    stored = target.put("metrics.test.auc", 0.7412, "scalar", "test AUC")
    assert target.artifact("metrics.test.auc") == stored
    assert isinstance(stored, Artifact)


def test_a_prefix_shared_by_two_artifacts_is_refused(tmp_path: Path) -> None:
    # The real case: two hashes really do share their first eight characters. Simulated by hand
    # on the index, because finding a natural collision would take 2**32 puts.
    target = store(tmp_path)
    first = target.put("metrics.test.auc", 0.7412, "scalar")
    index_path = tmp_path / "artifacts" / INDEX_FILE
    index = json.loads(index_path.read_text(encoding="utf-8"))
    twin = dict(index["artifacts"]["metrics.test.auc"])
    twin["hash"] = first.hash[:8] + "f" * 8
    index["artifacts"]["metrics.train.auc"] = twin
    index_path.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(ArtifactError, match="quote more of it"):
        ArtifactStore(tmp_path / "artifacts").get(first.hash[:8])
