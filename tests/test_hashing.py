"""`stable_hash` is the identity of everything Quaestor persists, so its stability is the test.

The subprocess test is the one that matters. Python salts `hash()` per process for strings, and
the whole point of `stable_hash` is that it does not: an artifact computed on a laptop and cited in
a report replayed on a CI runner has to be the same artifact.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

from quaestor.hashing import MAX_LENGTH, canonical_json, sha256_file, stable_hash

PAYLOAD = {
    "metric": "auc",
    "split": "test",
    "value": 0.7412,
    "features": ["utilisation", "delinq_last"],
    "nested": {"b": 2, "a": 1},
}


def test_canonical_json_sorts_keys_and_drops_whitespace() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_canonical_json_is_insensitive_to_key_order() -> None:
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_canonical_json_escapes_to_ascii() -> None:
    assert canonical_json({"note": "München"}) == '{"note":"M\\u00fcnchen"}'


def test_canonical_json_orders_sets_by_their_own_canonical_form() -> None:
    assert canonical_json({3, 1, 2}) == canonical_json({2, 3, 1})


def test_canonical_json_reduces_pydantic_models() -> None:
    class Row(BaseModel):
        name: str
        value: float

    assert canonical_json(Row(name="auc", value=0.5)) == '{"name":"auc","value":0.5}'


def test_canonical_json_accepts_paths() -> None:
    assert canonical_json(Path("a/b")) == '"a/b"'


def test_canonical_json_rejects_nan() -> None:
    with pytest.raises(ValueError, match="Out of range"):
        canonical_json({"value": math.nan})


def test_canonical_json_rejects_a_type_with_no_canonical_form() -> None:
    with pytest.raises(TypeError, match="cannot canonicalise"):
        canonical_json({"when": object()})


def test_stable_hash_length_defaults_to_sixteen() -> None:
    assert len(stable_hash(PAYLOAD)) == 16


@pytest.mark.parametrize("length", [1, 8, MAX_LENGTH])
def test_stable_hash_honours_length(length: int) -> None:
    assert len(stable_hash(PAYLOAD, length=length)) == length


def test_stable_hash_prefixes_are_consistent() -> None:
    assert stable_hash(PAYLOAD, length=8) == stable_hash(PAYLOAD, length=MAX_LENGTH)[:8]


@pytest.mark.parametrize("length", [0, -1, MAX_LENGTH + 1])
def test_stable_hash_rejects_an_impossible_length(length: int) -> None:
    with pytest.raises(ValueError, match="length must be between"):
        stable_hash(PAYLOAD, length=length)


def test_stable_hash_distinguishes_different_payloads() -> None:
    assert stable_hash({"value": 0.7412}) != stable_hash({"value": 0.7413})


def test_stable_hash_is_stable_across_processes() -> None:
    # The reason this module exists. `hash("auc")` differs between two interpreters; this must not.
    script = (
        "import json,sys;"
        "from quaestor.hashing import stable_hash;"
        "print(stable_hash(json.loads(sys.argv[1])))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, json.dumps(PAYLOAD)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == stable_hash(PAYLOAD)


def test_stable_hash_is_stable_across_processes_for_a_string_keyed_payload() -> None:
    # Strings are the case Python's own `hash` salts, so they are the case worth proving twice.
    script = (
        "from quaestor.hashing import stable_hash;"
        "print(stable_hash({'logical_name': 'metrics.test.auc'}))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=60, check=False
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == stable_hash({"logical_name": "metrics.test.auc"})


def test_sha256_file_is_a_plain_file_digest(tmp_path: Path) -> None:
    # A manifest digest is compared against a value somebody produced with `shasum -a 256`, so
    # this is deliberately the file's own digest and not a stable_hash of its contents.
    target = tmp_path / "train.csv"
    target.write_bytes(b"id,y\n1,0\n")
    assert sha256_file(target) == hashlib.sha256(b"id,y\n1,0\n").hexdigest()


def test_sha256_file_reads_a_file_larger_than_one_chunk(tmp_path: Path) -> None:
    target = tmp_path / "big.csv"
    target.write_bytes(b"x" * 5000)
    assert sha256_file(target, chunk_bytes=1024) == hashlib.sha256(b"x" * 5000).hexdigest()


def test_canonical_json_decodes_bytes() -> None:
    assert canonical_json(b"utf-8 text") == '"utf-8 text"'
