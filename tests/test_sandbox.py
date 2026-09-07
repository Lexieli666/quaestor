"""`run_model` and the spec 3.3 contract check: spec section 3.6's acceptance list.

The fixture subject below is a single small program whose behaviour is chosen by a flag written
into its package's `entrypoint`, which is how a test gets a subject that sleeps past its cap, one
that exits non-zero, one that writes a file nobody asked for and one that forgets a required file
without four near-identical fixture directories drifting apart.

Nothing here touches the network, and the only real subject exercised is the synthetic
`credit_default` panel: `tests/test_subject_credit_default.py` owns the assertions about what that
panel *is*, and this module owns the assertions about how it is run.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest
import yaml

from quaestor import ArtifactStore, SandboxError, load_package, run_model
from quaestor.sandbox import MemoryCap, build_argv, required_files
from quaestor.trace import EventType, TraceReader, TraceWriter

CREDIT_DEFAULT = Path(__file__).resolve().parent.parent / "subjects" / "credit_default"

FIXTURE_SUBJECT = '''
"""A fixture subject. Its behaviour is chosen by --behaviour, from the package's entrypoint."""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True)
parser.add_argument("--synthetic", type=int)
parser.add_argument("--data")
parser.add_argument("--seed", type=int)
parser.add_argument("--behaviour", default="ok")
args = parser.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

if args.behaviour == "sleep":
    time.sleep(120)
if args.behaviour == "fail":
    print("fitting the champion")
    sys.stderr.write("Traceback: the design matrix is singular\\n")
    raise SystemExit(3)
if args.behaviour == "environment":
    print(json.dumps(dict(sorted(os.environ.items()))))
if args.behaviour == "cwd":
    print(json.dumps(sorted(entry.name for entry in Path.cwd().iterdir())))
if args.behaviour == "pollute":
    (Path.cwd() / "code" / "scratch.txt").write_text("the subject wrote into its own copy")
if args.behaviour == "loud":
    print("x" * 200_000)

rows = [(1, 0, 0.1), (2, 1, 0.9), (3, 0, 0.3), (4, 1, 0.7)]
for split, part in (("train", rows[:2]), ("test", rows[2:])):
    identifiers = sorted(str(row[0]) for row in part)
    (out / f"splits_{split}.tmp").write_text("")
    (out / f"predictions_{split}.csv").write_text(
        "client_id,y_true,y_score\\n"
        + "".join(f"{row[0]},{row[1]},{row[2]}\\n" for row in part)
    )
    (out / f"data_{split}.csv").write_text(
        "client_id,x1,default\\n" + "".join(f"{row[0]},{row[2]},{row[1]}\\n" for row in part)
    )
    (out / f"splits_{split}.tmp").unlink()

splits = {}
for split, part in (("train", rows[:2]), ("test", rows[2:])):
    text = "\\n".join(str(row[0]) for row in sorted(part))
    splits[split] = {
        "n": len(part),
        "event_rate": sum(row[1] for row in part) / len(part),
        "rows_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
(out / "splits.json").write_text(json.dumps(splits))
(out / "features.json").write_text(
    json.dumps([{"name": "x1", "dtype": "float64", "timing": "at_origination"}])
)
(out / "metrics.json").write_text(json.dumps({"train": {"auc": 1.0}, "test": {"auc": 1.0}}))
(out / "model_summary.json").write_text(
    json.dumps({"coefficients": [{"feature": "x1", "value": 2.5}], "removed": []})
)
print(f"fixture subject: behaviour={args.behaviour} synthetic={args.synthetic} seed={args.seed}")

if args.behaviour == "extra":
    (out / "notes.txt").write_text("a figure the contract does not name")
    (out / "figures").mkdir(exist_ok=True)
    (out / "figures" / "roc.bin").write_bytes(b"\\x89PNG not really")
if args.behaviour == "omit_predictions":
    (out / "predictions_test.csv").unlink()
if args.behaviour == "malformed_splits":
    (out / "splits.json").write_text("{not json at all")
'''

FIXTURE_PACKAGE = {
    "name": "fixture_subject",
    "version": "0.1",
    "model_type": "binary_classification",
    "entrypoint": "python -m code.run",
    "data": {
        "source": "fixture only; no data, real or synthetic, is read",
        "manifest": None,
        "target": "default",
        "event_definition": "1 when the fixture says so",
        "time_column": None,
        "id_column": "client_id",
    },
    "splits": {
        "train": {"rule": "the first two rows"},
        "test": {"rule": "the last two rows"},
        "out_of_time": None,
        "vintage_holdout": None,
    },
    "features": [{"name": "x1", "timing": "at_origination"}],
    "regime": {"column": None},
    "thresholds": [],
    "claims": [],
    "scenarios": None,
    "runtime": {"max_seconds": 60, "max_memory_mb": 4096},
}


def make_fixture_subject(
    root: Path, *, behaviour: str = "ok", max_seconds: int = 60, memory_mb: int = 4096
) -> Path:
    """Write a fixture package whose subject behaves as asked, and return its directory."""
    package = root / f"fixture_{behaviour}"
    (package / "code").mkdir(parents=True)
    (package / "code" / "__init__.py").write_text('"""A fixture subject."""\n')
    (package / "code" / "run.py").write_text(FIXTURE_SUBJECT)
    spec = json.loads(json.dumps(FIXTURE_PACKAGE))
    spec["entrypoint"] = f"python -m code.run --behaviour {behaviour}"
    spec["runtime"] = {"max_seconds": max_seconds, "max_memory_mb": memory_mb}
    (package / "package.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))
    return package


# --- the argument vector -------------------------------------------------------------------------


def test_the_entrypoints_python_becomes_this_interpreter(tmp_path: Path) -> None:
    argv = build_argv("python -m code.run", tmp_path / "out", data_dir=None, synthetic=500, seed=7)
    assert argv == [
        sys.executable,
        "-m",
        "code.run",
        "--out",
        str((tmp_path / "out").resolve()),
        "--synthetic",
        "500",
        "--seed",
        "7",
    ]


def test_a_data_run_passes_the_data_directory_and_omits_an_unset_seed(tmp_path: Path) -> None:
    argv = build_argv(
        "python3 -m code.run", tmp_path / "out", data_dir=tmp_path, synthetic=None, seed=None
    )
    assert argv[:3] == [sys.executable, "-m", "code.run"]
    assert "--synthetic" not in argv
    assert "--seed" not in argv
    assert argv[-2:] == ["--data", str(tmp_path.resolve())]


def test_a_non_python_entrypoint_is_left_alone(tmp_path: Path) -> None:
    argv = build_argv("./fit.sh", tmp_path, data_dir=None, synthetic=1, seed=None)
    assert argv[0] == "./fit.sh"


def test_an_empty_entrypoint_is_a_sandbox_error(tmp_path: Path) -> None:
    with pytest.raises(SandboxError, match="empty entrypoint"):
        build_argv("   ", tmp_path, data_dir=None, synthetic=1, seed=None)


# --- the memory cap policy (DECISIONS D-028) -----------------------------------------------------


def test_linux_enforces_the_address_space_cap() -> None:
    assert memory_cap_policy_for("linux") is MemoryCap.enforced


@pytest.mark.parametrize("platform", ["darwin", "win32", "freebsd13"])
def test_every_other_platform_records_the_cap_as_unenforced(platform: str) -> None:
    assert memory_cap_policy_for(platform) is MemoryCap.unenforced


def memory_cap_policy_for(platform: str) -> MemoryCap:
    from quaestor.sandbox import memory_cap_policy

    return memory_cap_policy(platform)


def test_the_limiter_is_a_callable_whatever_the_policy_says() -> None:
    from quaestor.sandbox.runner import _limiter

    # Built here rather than through a run, because the child it applies the limit in is a fork
    # that no coverage of this process can see, and on macOS the policy never builds one at all.
    assert callable(_limiter(4096))


def test_the_running_platforms_policy_is_one_of_the_two() -> None:
    from quaestor.sandbox import memory_cap_policy

    assert memory_cap_policy() in (MemoryCap.enforced, MemoryCap.unenforced)


# --- how the subprocess is run -------------------------------------------------------------------


PASSED_ENVIRONMENT = frozenset({"PATH", "PYTHONPATH", "HOME", "QUAESTOR_NO_NETWORK"})
"""The four variables `run_model` sets. Nothing else of the caller's reaches the subject."""

PLATFORM_INJECTED = frozenset({"__CF_USER_TEXT_ENCODING", "LC_CTYPE"})
"""What macOS's own libc adds to every spawned process, whatever environment it was given.

Neither carries a path or a secret, and neither is inherited from the caller: they appear in a
child spawned from an empty environment too, which is why the assertion below excludes them
rather than pretending the scrub failed.
"""


def test_the_environment_is_scrubbed_to_four_variables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-this-must-not-reach-a-subject")
    monkeypatch.setenv("QUAESTOR_LEAK_CANARY", "the caller's environment leaked")
    package = load_package(make_fixture_subject(tmp_path, behaviour="environment"))
    result = run_model(package, None, tmp_path / "out", synthetic=4)
    environment = json.loads(result.stdout.splitlines()[0])
    assert set(environment) - PLATFORM_INJECTED <= PASSED_ENVIRONMENT
    assert "ANTHROPIC_API_KEY" not in environment
    assert "QUAESTOR_LEAK_CANARY" not in environment
    assert environment["QUAESTOR_NO_NETWORK"] == "1"
    assert environment["HOME"] != str(Path.home())
    assert environment["HOME"] not in (str(tmp_path), str(package.root))


def test_the_working_directory_holds_a_copy_of_code_and_a_private_home(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="cwd"))
    result = run_model(package, None, tmp_path / "out", synthetic=4)
    assert json.loads(result.stdout.splitlines()[0]) == ["code", "home"]


def test_the_subject_cannot_reach_the_packages_own_code_directory(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="pollute"))
    run_model(package, None, tmp_path / "out", synthetic=4)
    assert not (package.code_dir / "scratch.txt").exists()
    assert sorted(path.name for path in package.code_dir.iterdir()) == ["__init__.py", "run.py"]


def test_a_subject_that_sleeps_past_its_cap_is_killed_and_reported(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="sleep", max_seconds=2))
    started = time.monotonic()
    with pytest.raises(SandboxError, match="outran its wall-clock cap of 2 s") as raised:
        run_model(package, None, tmp_path / "out", synthetic=4)
    assert time.monotonic() - started < 60.0
    assert "run.stdout" in str(raised.value)

    store = ArtifactStore(tmp_path / "out" / "artifacts")
    status = store.load("run.status")
    assert status["timed_out"] is True
    assert status["returncode"] == -9
    assert store.value("run.duration_s") >= 2.0
    assert not (tmp_path / "out" / "splits.json").exists()


def test_a_subject_that_exits_non_zero_is_reported_with_its_stderr(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="fail"))
    with pytest.raises(SandboxError, match="exited 3") as raised:
        run_model(package, None, tmp_path / "out", synthetic=4)
    assert "design matrix is singular" in str(raised.value)

    store = ArtifactStore(tmp_path / "out" / "artifacts")
    assert store.load("run.stdout").strip() == "fitting the champion"
    assert store.load("run.status")["timed_out"] is False


def test_an_extra_file_is_stored_and_flagged_unexpected_output(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="extra"))
    result = run_model(package, None, tmp_path / "out", synthetic=4)
    assert result.unexpected_output == ["figures/roc.bin", "notes.txt"]

    store = ArtifactStore(result.store_root)
    described = store.load("run.unexpected.notes.txt")
    assert described["file"] == "notes.txt"
    assert described["text"] == "a figure the contract does not name"
    assert len(described["sha256"]) == 64
    binary = store.load("run.unexpected.figures.roc.bin")
    assert binary["text"] is None
    assert binary["bytes"] == 15


def test_a_missing_contract_file_names_itself(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="omit_predictions"))
    with pytest.raises(SandboxError, match="did not write predictions_test.csv"):
        run_model(package, None, tmp_path / "out", synthetic=4)


def test_a_malformed_contract_file_names_itself(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="malformed_splits"))
    with pytest.raises(SandboxError, match=r"splits\.json does not satisfy") as raised:
        run_model(package, None, tmp_path / "out", synthetic=4)
    assert "not JSON" in str(raised.value)


def test_a_loud_subjects_output_is_truncated_with_a_marker(tmp_path: Path) -> None:
    from quaestor.sandbox.runner import MAX_CAPTURE_BYTES

    package = load_package(make_fixture_subject(tmp_path, behaviour="loud"))
    result = run_model(package, None, tmp_path / "out", synthetic=4)
    assert "truncated by quaestor.sandbox" in result.stdout
    assert len(result.stdout.encode("utf-8")) < MAX_CAPTURE_BYTES + 200


def test_the_result_records_the_run_and_its_caps(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="ok", max_seconds=45))
    result = run_model(package, None, tmp_path / "out", synthetic=4, seed=13)
    assert result.package == "fixture_subject"
    assert result.data_mode == "synthetic"
    assert result.synthetic == 4
    assert result.seed == 13
    assert result.returncode == 0
    assert result.timed_out is False
    assert result.max_seconds == 45
    assert result.memory_cap_mb == 4096
    assert "seed=13" in result.stdout
    assert result.duration_s > 0.0
    assert result.store_root == tmp_path / "out" / "artifacts"


def test_a_caller_can_pass_its_own_store(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path))
    store = ArtifactStore(tmp_path / "elsewhere")
    result = run_model(package, None, tmp_path / "out", synthetic=4, store=store)
    assert result.store_root == store.root
    assert "run.splits" in store
    assert not (tmp_path / "out" / "artifacts").exists()
    assert result.unexpected_output == []


def test_a_previous_runs_store_inside_the_output_directory_is_not_unexpected(
    tmp_path: Path,
) -> None:
    package = load_package(make_fixture_subject(tmp_path))
    out = tmp_path / "out"
    ArtifactStore(out / "artifacts").put("run.leftover", 1.0, "scalar")
    result = run_model(package, None, out, synthetic=4)
    assert result.unexpected_output == []


def test_the_run_emits_one_traced_tool_call_with_its_memory_cap(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path))
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="sandbox-test")
    result = run_model(package, None, tmp_path / "out", synthetic=4, trace=trace)
    events = TraceReader(tmp_path / "trace.jsonl").events(EventType.tool_call)
    assert len(events) == 1
    payload = events[0].payload
    assert payload["tool"] == "run_model"
    assert payload["ok"] is True
    assert payload["timed_out"] is False
    assert payload["memory_cap"] == result.memory_cap.value
    assert payload["unexpected_output"] == []
    assert sorted(payload["artifacts"]) == sorted(item.hash for item in result.artifacts)


def test_a_failed_run_is_traced_too(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path, behaviour="fail"))
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="sandbox-test")
    with pytest.raises(SandboxError):
        run_model(package, None, tmp_path / "out", synthetic=4, trace=trace)
    events = TraceReader(tmp_path / "trace.jsonl").events(EventType.tool_call)
    assert [event.payload["ok"] for event in events] == [False]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({}, "not neither"),
        ({"synthetic": 4, "data_dir": "somewhere"}, "not both"),
    ],
)
def test_exactly_one_data_mode_is_required(
    tmp_path: Path, kwargs: dict[str, object], message: str
) -> None:
    package = load_package(make_fixture_subject(tmp_path))
    with pytest.raises(SandboxError, match=message):
        run_model(
            package,
            kwargs.get("data_dir"),  # type: ignore[arg-type]
            tmp_path / "out",
            synthetic=kwargs.get("synthetic"),  # type: ignore[arg-type]
        )


def test_an_output_directory_is_required(tmp_path: Path) -> None:
    package = load_package(make_fixture_subject(tmp_path))
    with pytest.raises(SandboxError, match="needs an output directory"):
        run_model(package, None, None, synthetic=4)


def test_a_package_whose_code_directory_vanished_is_a_sandbox_error(tmp_path: Path) -> None:
    root = make_fixture_subject(tmp_path)
    package = load_package(root)
    for path in sorted(package.code_dir.iterdir()):
        path.unlink()
    package.code_dir.rmdir()
    with pytest.raises(SandboxError, match="has no code/ directory"):
        run_model(package, None, tmp_path / "out", synthetic=4)


# --- the credit_default subject through the sandbox ----------------------------------------------


def test_the_synthetic_credit_subject_runs_end_to_end_under_sixty_seconds(
    tmp_path: Path,
) -> None:
    package = load_package(CREDIT_DEFAULT)
    started = time.monotonic()
    result = run_model(package, None, tmp_path / "run", synthetic=5000)
    elapsed = time.monotonic() - started
    assert elapsed < 60.0, f"the synthetic credit subject took {elapsed:.1f} s"
    assert result.returncode == 0
    assert result.duration_s < 60.0
    assert sorted(result.files) == sorted(required_files(package.spec))
    assert {"run.splits", "run.features", "run.metrics", "run.model_summary"} <= {
        artifact.name for artifact in result.artifacts
    }
