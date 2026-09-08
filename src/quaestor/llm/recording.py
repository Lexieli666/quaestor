"""``RecordingLLM`` and ``ReplayLLM``: keeping every call a live validation made.

The runbook's Phase 9 runs both real subjects through ``--llm claude-cli`` and reads the two
reports end to end. A model call that produced a published report and was then thrown away is a
result that cannot be re-examined, so ``quaestor validate --record-cassettes DIR`` wraps whatever
provider was chosen and writes one JSON file per call: the request, the completion, and the
provenance of the provider that answered. ``--llm replay --cassettes DIR`` reads them back, and a
call that is not on tape raises rather than being answered by something else.

The file for a call is named by ``stable_hash`` of ``(system, prompt, params)`` -- the same key
:meth:`quaestor.llm.FakeLLM.call_key` uses -- so the store is a mapping from request to answer.
Two consequences follow and are deliberate. Re-running a validation over the same artifacts asks
the same questions and hits the same tapes, which is what makes a recorded run reproducible. And
a run that asks the *identical* question twice has one tape for both: the file records how many
times it was asked (``calls``), and a non-deterministic provider's second answer overwrites the
first (DECISIONS D-079).

This is **not** Phase 11's cassette format. Probatio's cases record their own tapes through
Probatio's provider fixture, under ``tests/probatio/cassettes/``, and those are a test suite's
fixtures: they are replayed by ``pytest`` in CI and they pin what the SUT is given. These are the
record of one validation run, written beside its report, and nothing in the test suite replays
them by default. The two stores answer different questions and neither reads the other's files.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from ..errors import LLMProviderError
from ..hashing import stable_hash
from .base import LLM, Completion

__all__ = ["CASSETTE_SUFFIX", "CASSETTE_VERSION", "RecordingLLM", "ReplayLLM", "cassette_key"]

CASSETTE_SUFFIX: Final = ".json"
"""One file per call, named ``<key><suffix>``."""

CASSETTE_VERSION: Final = 1
"""The ``schema_version`` every cassette carries, so a format change is legible."""

_UNRECORDED: Final = "replay"
"""The provider name a replay reports when the directory holds no tape to take one from."""


def cassette_key(prompt: str, system: str | None, params: Mapping[str, Any]) -> str:
    """Return the file name stem for one call.

    Args:
        prompt: The user-turn text.
        system: The system prompt, or ``None``.
        params: The parameters the caller passed to the provider.

    Returns:
        The :func:`~quaestor.hashing.stable_hash` of the whole request, which is what the call's
        file is named after. The parameters are rendered the same way they are recorded, so that
        a parameter no JSON encoder can take -- which a provider is free to accept -- names a
        tape rather than raising in the middle of a run.
    """
    return stable_hash({"prompt": prompt, "params": _plain(params), "system": system})


class RecordingLLM:
    """A provider that answers through another one and writes every call to a directory.

    Attributes:
        name: The wrapped provider's name, so that a recorded run's report and trace say what
            answered them rather than saying that a recorder did.
        inner: The provider that does the work.
        dir: Where the cassettes are written; created if it does not exist.
    """

    def __init__(self, inner: LLM, dir: Path | str) -> None:
        """Wrap a provider and choose where its calls are kept.

        Args:
            inner: The provider that answers, satisfying the
                :class:`~quaestor.llm.base.LLM` protocol.
            dir: The cassette directory.
        """
        self.inner = inner
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.name: str = str(getattr(inner, "name", "unknown"))

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Answer through the wrapped provider and write the call to its cassette.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when the caller has one.
            **params: Passed straight through, and part of the cassette's key.

        Returns:
            Exactly what the wrapped provider returned, unchanged.
        """
        completion = self.inner.complete(prompt, system=system, **params)
        key = cassette_key(prompt, system, params)
        path = self.dir / f"{key}{CASSETTE_SUFFIX}"
        calls = 1
        if path.exists():
            previous = _read(path)
            calls = int(previous.get("calls", 1)) + 1
        payload = {
            "schema_version": CASSETTE_VERSION,
            "key": key,
            "provider": self.name,
            "calls": calls,
            "request": {"prompt": prompt, "system": system, "params": _plain(params)},
            "completion": completion.model_dump(mode="json"),
        }
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return completion


class ReplayLLM:
    """A provider that answers only from a directory of recorded calls.

    Attributes:
        name: The name of the provider the tapes were recorded from, when they agree on one, so
            that a replayed run renders the report the recorded run rendered. ``"replay"`` when
            the directory is empty or its tapes disagree.
        dir: Where the cassettes are.
        served: The keys served so far, in order, so a test can assert what was replayed.
    """

    def __init__(self, dir: Path | str) -> None:
        """Read the directory's index.

        Args:
            dir: The cassette directory.

        Raises:
            LLMProviderError: The directory does not exist; a replay with nothing to replay is a
                mistake worth failing on rather than a run with no answers.
        """
        self.dir = Path(dir)
        if not self.dir.is_dir():
            raise LLMProviderError(
                f"no cassette directory at {self.dir}",
                fix=f"quaestor validate PKG --llm claude-cli --record-cassettes {self.dir}",
            )
        self.served: list[str] = []
        providers = {
            str(_read(path).get("provider", ""))
            for path in sorted(self.dir.glob(f"*{CASSETTE_SUFFIX}"))
        }
        self.name: str = providers.pop() if len(providers) == 1 else _UNRECORDED

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Answer one call from its cassette.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when the caller has one.
            **params: The parameters, which are part of the key: a call made with a different
                model is a different call and is not on this tape.

        Returns:
            The completion as it was recorded.

        Raises:
            LLMProviderError: This call is not on tape. The message names the missing key and the
                first line of the prompt, because a replay that fails is nearly always a pipeline
                that changed a prompt since the recording.
        """
        key = cassette_key(prompt, system, params)
        path = self.dir / f"{key}{CASSETTE_SUFFIX}"
        if not path.exists():
            opening = prompt.strip().splitlines()[0][:120] if prompt.strip() else "<empty>"
            raise LLMProviderError(
                f"no recorded call {key} in {self.dir}; the prompt began {opening!r}",
                fix=f"quaestor validate PKG --llm claude-cli --record-cassettes {self.dir}",
            )
        self.served.append(key)
        payload = _read(path)
        completion = payload.get("completion")
        if not isinstance(completion, dict):
            raise LLMProviderError(f"the cassette {path} holds no completion object")
        return Completion.model_validate(completion)


def _read(path: Path) -> dict[str, Any]:
    """Read one cassette, naming the file when it is not a JSON object."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LLMProviderError(f"the cassette {path} could not be read: {exc}") from exc
    if not isinstance(payload, dict):
        raise LLMProviderError(f"the cassette {path} is not a JSON object")
    return payload


def _plain(params: Mapping[str, Any]) -> dict[str, Any]:
    """Render a call's parameters for the record, keeping anything unserialisable as its repr."""
    plain: dict[str, Any] = {}
    for name, value in params.items():
        try:
            json.dumps(value)
        except TypeError:
            plain[name] = repr(value)
        else:
            plain[name] = value
    return plain
