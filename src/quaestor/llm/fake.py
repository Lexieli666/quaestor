"""``FakeLLM`` and ``ScriptedLLM``: the only two providers the test suite may use.

``CLAUDE.md`` forbids a live model in anything ``pytest`` runs, so every test of the drafter, the
extractor, the planner and the repair loop reaches one of these. A fake has to be predictable
enough to assert on and interesting enough to be worth asserting on, which is why the lookup has
three layers: an exact key over the whole call, a prompt substring for the common "answer this
question with that", and a default that may be a callable so a fake extractor can answer by
inspecting the prompt it was handed.

Nothing here is random and nothing reads the clock: the same construction answers the same prompt
with the same text, cost and latency in every process. That is what makes an end-to-end report
under ``--llm fake`` byte-comparable between runs.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..errors import LLMProviderError
from ..hashing import stable_hash
from .base import Completion

__all__ = ["DEFAULT_MODEL", "FakeCall", "FakeLLM", "ScriptedLLM"]

DEFAULT_MODEL: Final = "fake-1"
"""The model name a fake reports when the caller does not choose one."""


class FakeCall(BaseModel):
    """One call a fake received, recorded so a test can assert on what the pipeline sent.

    Attributes:
        prompt: The user-turn text.
        system: The system prompt, or ``None``.
        params: The parameters the caller passed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    prompt: str
    system: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class FakeLLM:
    """An offline provider that answers from a table.

    A prompt is answered by the first of these that produces something:

    1. ``responses[call_key(prompt, system, params)]`` -- an exact match on the whole call.
    2. ``responses[k]`` for the first ``k``, in insertion order, that is a substring of the
       prompt. Insertion order is the author's declared priority.
    3. ``default``, called with the prompt if it is callable.
    4. ``f"FAKE({stable_hash(prompt)})"``, a fallback that is stable, obviously synthetic and
       different for every prompt, so a table that misses shows up as a failed assertion rather
       than as a plausible answer.

    Attributes:
        name: ``"fake"``, which is what the report's front matter records as its model.
        calls: Every call received, in order.
    """

    name: str = "fake"

    def __init__(
        self,
        responses: Mapping[str, str] | None = None,
        default: str | Callable[[str], str] | None = None,
        *,
        cost_usd: float | None = None,
        latency_ms: float = 0.0,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """Configure the table and the fixed cost, latency and model name of every answer.

        Args:
            responses: Answers keyed by call key or by prompt substring, checked in that order.
            default: The answer when nothing matches, or a callable applied to the prompt.
            cost_usd: The cost reported for every call. ``None`` means "unknown", exactly as a
                real unpriced model would report.
            latency_ms: The latency reported for every call.
            model: The model name reported on every completion.
        """
        self.responses: dict[str, str] = dict(responses or {})
        self.default = default
        self.cost_usd = cost_usd
        self.latency_ms = latency_ms
        self.model = model
        self.calls: list[FakeCall] = []

    @property
    def call_count(self) -> int:
        """How many calls this provider has received."""
        return len(self.calls)

    @staticmethod
    def call_key(prompt: str, system: str | None, params: Mapping[str, Any]) -> str:
        """Return the exact-match key for one call, for use as a ``responses`` key.

        Args:
            prompt: The user-turn text.
            system: The system prompt, or ``None``.
            params: The call's parameters.

        Returns:
            The :func:`~quaestor.hashing.stable_hash` of the whole call.
        """
        return stable_hash({"prompt": prompt, "params": dict(params), "system": system})

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Answer a prompt from the table and record the call.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when the caller has one.
            **params: The caller's parameters; recorded, and part of the exact-match key.

        Returns:
            The completion, with this provider's fixed cost, latency and model name.
        """
        self.calls.append(FakeCall(prompt=prompt, system=system, params=dict(params)))
        text, source = self._respond(prompt, system, params)
        return Completion(
            text=text,
            model=self.model,
            cost_usd=self.cost_usd,
            latency_ms=self.latency_ms,
            raw={"provider": self.name, "matched": source},
        )

    def _respond(
        self, prompt: str, system: str | None, params: Mapping[str, Any]
    ) -> tuple[str, str]:
        """Resolve a prompt to its answer and the name of the layer that produced it."""
        key = self.call_key(prompt, system, params)
        if key in self.responses:
            return self.responses[key], "call_key"
        for needle, answer in self.responses.items():
            if needle in prompt:
                return answer, "substring"
        if callable(self.default):
            return self.default(prompt), "default"
        if self.default is not None:
            return self.default, "default"
        return f"FAKE({stable_hash(prompt)})", "fallback"


class ScriptedLLM(FakeLLM):
    """A fake that reads a fixed sequence of answers in order, cycling when it runs out.

    This is how the re-ask path is tested offline: a script whose first entry is unparsable JSON
    and whose second is valid proves that :func:`~quaestor.llm.structured.structured` re-asks
    exactly once and then succeeds, with no randomness anywhere.

    Attributes:
        name: ``"scripted"``.
        script: The answers, in order.
    """

    name: str = "scripted"

    def __init__(
        self,
        script: Sequence[str],
        *,
        cost_usd: float | None = None,
        latency_ms: float = 0.0,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """Configure the sequence and the fixed cost, latency and model name of every answer.

        Args:
            script: The answers, in the order they are returned. Cycles once exhausted.
            cost_usd: The cost reported for every call.
            latency_ms: The latency reported for every call.
            model: The model name reported on every completion.

        Raises:
            LLMProviderError: The script is empty, so there is nothing to return.
        """
        super().__init__(None, None, cost_usd=cost_usd, latency_ms=latency_ms, model=model)
        if not script:
            raise LLMProviderError("a ScriptedLLM needs at least one scripted answer")
        self.script: list[str] = list(script)

    def _respond(
        self, prompt: str, system: str | None, params: Mapping[str, Any]
    ) -> tuple[str, str]:
        """Return the answer for this call's position in the script."""
        return self.script[(self.call_count - 1) % len(self.script)], "script"
