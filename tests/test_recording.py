"""Phase 9: the recording layer, and the round trip that proves a run can be replayed.

The runbook's Phase 9 makes the first two live validations and commits their reports. A model call
that produced a published report and was then thrown away cannot be re-examined, so
`--record-cassettes DIR` keeps every one of them and `--llm replay --cassettes DIR` runs the
pipeline again from the tape.

The end-to-end test below records a run under `--llm fake` and replays it, and asserts the two
reports are byte-identical apart from the three things that are not properties of the model: the
`generated` timestamp and the two wall-clock rows of Appendix C. Everything else -- every claim,
every artifact hash, both grounding figures, the run id -- is the same file twice.

Nothing here calls a live model. The recorder is exercised over `OfflineLLM` and over small fakes.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from quaestor import TraceReader
from quaestor.cli import EXIT_FAILED_RUN, EXIT_OK, main
from quaestor.errors import LLMProviderError
from quaestor.llm import Completion, FakeLLM, OfflineLLM, RecordingLLM, ReplayLLM
from quaestor.llm.recording import CASSETTE_VERSION, cassette_key
from quaestor.trace import EventType

REPO_ROOT = Path(__file__).resolve().parents[1]
CREDIT = REPO_ROOT / "subjects" / "credit_default"
SMALL = 600
"""Rows enough for every check to have something to read, small enough to run twice in a test."""

_VARIABLE = re.compile(
    r"^(generated: .*|run_id: .*|\| run id \| .*|\| wall-clock \(s\) \| .*"
    r"|\| subject run \(s\) \| .*)$",
    re.MULTILINE,
)
"""The five lines of a report that are a property of the occasion rather than of the model.

The two ``run_id`` lines joined this list in the Phase 9 follow-up 3: a run id now carries the
second it started at (D-093), so two runs never share one and the replay cannot be expected to
reproduce the recording's. What the identifier stands for is still asserted -- both lines are
present, and every event of each run carries its own run's id -- and what the round trip is for,
that every claim, hash and grounding figure comes back the same, is unchanged.
"""


def quaestor(*argv: str) -> subprocess.CompletedProcess[str]:
    """Run the installed console script, as `tests/test_cli.py` does."""
    executable = shutil.which("quaestor")
    assert executable is not None, "the `quaestor` console script is not on PATH; pip install -e ."
    return subprocess.run(
        [executable, *argv], capture_output=True, text=True, timeout=600, check=False
    )


def stable(report: str) -> str:
    """Blank the timestamp and the two duration rows, which no two runs share."""
    return _VARIABLE.sub("<varies>", report)


# --- the recorder ----------------------------------------------------------------------------


def test_one_call_becomes_one_file_named_by_its_request(tmp_path: Path) -> None:
    inner = FakeLLM(default="the answer")
    recorder = RecordingLLM(inner, tmp_path / "tapes")
    completion = recorder.complete("a question", system="be brief", model="m")
    key = cassette_key("a question", "be brief", {"model": "m"})
    payload = json.loads((tmp_path / "tapes" / f"{key}.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == CASSETTE_VERSION
    assert payload["key"] == key
    assert payload["provider"] == "fake"
    assert payload["calls"] == 1
    assert payload["request"] == {
        "prompt": "a question",
        "system": "be brief",
        "params": {"model": "m"},
    }
    assert payload["completion"]["text"] == completion.text == "the answer"


def test_the_recorder_reports_the_wrapped_providers_name(tmp_path: Path) -> None:
    # So that a recorded run's front matter and trace say `fake`, not `recording`: recording a run
    # must not change what the run is.
    assert RecordingLLM(OfflineLLM(), tmp_path).name == "fake"
    assert RecordingLLM(object(), tmp_path).name == "unknown"


def test_the_same_request_twice_keeps_one_tape_and_counts_the_calls(tmp_path: Path) -> None:
    # The store is keyed by request, so a repeated question has one answer on file. The count is
    # recorded rather than hidden, because for a non-deterministic provider it is a caveat (D-079).
    recorder = RecordingLLM(FakeLLM(default="same"), tmp_path)
    recorder.complete("twice")
    recorder.complete("twice")
    tapes = sorted(tmp_path.glob("*.json"))
    assert len(tapes) == 1
    assert json.loads(tapes[0].read_text(encoding="utf-8"))["calls"] == 2


def test_a_parameter_no_json_encoder_takes_is_recorded_as_its_repr(tmp_path: Path) -> None:
    # A provider is free to accept a parameter that is not JSON, and a recorder that raised on one
    # would fail a live run in the middle. The key is computed the same way the record is written.
    recorder = RecordingLLM(FakeLLM(default="ok"), tmp_path)
    recorder.complete("p", settings=Path("/etc/quaestor"))
    payload = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    assert payload["request"]["params"]["settings"] == repr(Path("/etc/quaestor"))
    assert ReplayLLM(tmp_path).complete("p", settings=Path("/etc/quaestor")).text == "ok"


def test_the_directory_is_created_if_it_is_not_there(tmp_path: Path) -> None:
    RecordingLLM(FakeLLM(default="ok"), tmp_path / "deep" / "deeper")
    assert (tmp_path / "deep" / "deeper").is_dir()


# --- the replay ------------------------------------------------------------------------------


def test_a_recorded_call_is_replayed_exactly(tmp_path: Path) -> None:
    inner = FakeLLM(default="the answer", cost_usd=0.25, latency_ms=12.5, model="m-1")
    RecordingLLM(inner, tmp_path).complete("a question", system="s")
    replay = ReplayLLM(tmp_path)
    completion = replay.complete("a question", system="s")
    assert completion == Completion(
        text="the answer",
        model="m-1",
        cost_usd=0.25,
        latency_ms=12.5,
        raw={"provider": "fake", "matched": "default"},
    )
    assert replay.served == [cassette_key("a question", "s", {})]


def test_the_replay_answers_as_the_provider_that_was_recorded(tmp_path: Path) -> None:
    RecordingLLM(OfflineLLM(), tmp_path).complete("anything")
    assert ReplayLLM(tmp_path).name == "fake"


def test_a_replay_of_tapes_from_two_providers_names_neither(tmp_path: Path) -> None:
    RecordingLLM(FakeLLM(default="a"), tmp_path).complete("one")
    RecordingLLM(OfflineLLM(model="other"), tmp_path).complete("two")
    tapes = sorted(tmp_path.glob("*.json"))
    payload = json.loads(tapes[0].read_text(encoding="utf-8"))
    payload["provider"] = "claude-cli"
    tapes[0].write_text(json.dumps(payload), encoding="utf-8")
    assert ReplayLLM(tmp_path).name == "replay"


def test_a_call_that_is_not_on_tape_fails_loudly(tmp_path: Path) -> None:
    RecordingLLM(FakeLLM(default="ok"), tmp_path).complete("the recorded question")
    replay = ReplayLLM(tmp_path)
    with pytest.raises(LLMProviderError) as raised:
        replay.complete("a question nobody recorded\nand a second line")
    message = str(raised.value)
    assert cassette_key("a question nobody recorded\nand a second line", None, {}) in message
    assert "a question nobody recorded" in message
    assert "--record-cassettes" in message


def test_a_call_whose_parameters_differ_is_a_different_call(tmp_path: Path) -> None:
    # A tape recorded from one model does not answer for another; the study depends on it.
    RecordingLLM(FakeLLM(default="ok"), tmp_path).complete("p", model="a")
    with pytest.raises(LLMProviderError, match="no recorded call"):
        ReplayLLM(tmp_path).complete("p", model="b")


def test_a_replay_of_a_directory_that_is_not_there_says_how_to_record_one(tmp_path: Path) -> None:
    with pytest.raises(LLMProviderError, match="no cassette directory"):
        ReplayLLM(tmp_path / "never-recorded")


@pytest.mark.parametrize(
    ("content", "needle"),
    [("not json", "could not be read"), ('["a list"]', "is not a JSON object")],
    ids=["unparsable", "not-an-object"],
)
def test_a_cassette_that_is_not_a_record_of_a_call_names_its_file(
    content: str, needle: str, tmp_path: Path
) -> None:
    (tmp_path / "deadbeefdeadbeef.json").write_text(content, encoding="utf-8")
    with pytest.raises(LLMProviderError, match=needle):
        ReplayLLM(tmp_path)


def test_a_cassette_holding_no_completion_is_refused(tmp_path: Path) -> None:
    key = cassette_key("p", None, {})
    (tmp_path / f"{key}.json").write_text(json.dumps({"provider": "fake"}), encoding="utf-8")
    with pytest.raises(LLMProviderError, match="holds no completion object"):
        ReplayLLM(tmp_path).complete("p")


# --- the round trip, through the command line ------------------------------------------------


@pytest.fixture(scope="module")
def round_trip(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, Path]:
    """Record one validation and replay it, returning the two run directories and the tapes."""
    root = tmp_path_factory.mktemp("roundtrip")
    recorded, replayed, tapes = root / "recorded", root / "replayed", root / "tapes"
    assert (
        main(
            [
                "validate",
                str(CREDIT),
                "--synthetic",
                str(SMALL),
                "--llm",
                "fake",
                "--out",
                str(recorded),
                "--record-cassettes",
                str(tapes),
            ]
        )
        == EXIT_OK
    )
    assert (
        main(
            [
                "validate",
                str(CREDIT),
                "--synthetic",
                str(SMALL),
                "--llm",
                "replay",
                "--cassettes",
                str(tapes),
                "--out",
                str(replayed),
            ]
        )
        == EXIT_OK
    )
    return recorded, replayed, tapes


def test_a_replayed_run_writes_the_report_the_recorded_run_wrote(
    round_trip: tuple[Path, Path, Path],
) -> None:
    recorded, replayed, _ = round_trip
    first = stable((recorded / "report.md").read_text(encoding="utf-8"))
    second = stable((replayed / "report.md").read_text(encoding="utf-8"))
    assert first == second
    assert "run_id:" in (recorded / "report.md").read_text(encoding="utf-8")
    assert _run_ids(recorded) != _run_ids(replayed), (
        "two runs shared a run id; D-093 stamps the second the run started into it"
    )


def _run_ids(out: Path) -> str:
    """The run id every file of one run carries, read off its trace."""
    events = TraceReader(out / "trace.jsonl").events()
    ids = {event.run_id for event in events}
    assert len(ids) == 1, f"{out} wrote more than one run id: {sorted(ids)}"
    return ids.pop()


def test_the_replayed_run_writes_the_same_claims_and_findings(
    round_trip: tuple[Path, Path, Path],
) -> None:
    recorded, replayed, _ = round_trip
    for name in ("claims.json", "findings.json"):
        first = json.loads((recorded / name).read_text(encoding="utf-8"))
        second = json.loads((replayed / name).read_text(encoding="utf-8"))
        assert _without_run_id(first) == _without_run_id(second), name


def _without_run_id(document: dict[str, object]) -> dict[str, object]:
    """One document without its ``run_id``, which is now a property of the occasion (D-093)."""
    return {key: value for key, value in document.items() if key != "run_id"}


def test_every_model_call_of_the_recorded_run_is_on_tape(
    round_trip: tuple[Path, Path, Path],
) -> None:
    recorded, _, tapes = round_trip
    events = TraceReader(recorded / "trace.jsonl").events()
    calls = [event for event in events if event.type == EventType.llm_call]
    assert calls, "the recorded run made no model call, so nothing was under test"
    keys = {json.loads(path.read_text(encoding="utf-8"))["key"] for path in tapes.glob("*.json")}
    assert len(keys) == len(list(tapes.glob("*.json")))
    assert len(keys) <= len(calls)


def test_a_replay_missing_one_call_fails_the_run_rather_than_inventing_an_answer(
    round_trip: tuple[Path, Path, Path], tmp_path: Path
) -> None:
    _, _, tapes = round_trip
    incomplete = tmp_path / "incomplete"
    shutil.copytree(tapes, incomplete)
    removed = sorted(incomplete.glob("*.json"))[0]
    key = removed.stem
    removed.unlink()
    completed = quaestor(
        "validate",
        str(CREDIT),
        "--synthetic",
        str(SMALL),
        "--llm",
        "replay",
        "--cassettes",
        str(incomplete),
        "--out",
        str(tmp_path / "r"),
    )
    assert completed.returncode == EXIT_FAILED_RUN
    assert key in completed.stderr
    assert "no recorded call" in completed.stderr
    assert not (tmp_path / "r" / "report.md").exists()


def test_the_same_failure_in_process_returns_the_exit_code_rather_than_raising(
    round_trip: tuple[Path, Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, tapes = round_trip
    incomplete = tmp_path / "incomplete"
    shutil.copytree(tapes, incomplete)
    sorted(incomplete.glob("*.json"))[0].unlink()
    code = main(
        [
            "validate",
            str(CREDIT),
            "--synthetic",
            str(SMALL),
            "--llm",
            "replay",
            "--cassettes",
            str(incomplete),
            "--out",
            str(tmp_path / "r"),
        ]
    )
    assert code == EXIT_FAILED_RUN
    assert "no recorded call" in capsys.readouterr().err
