"""The ``LLM`` protocol and the ``Completion`` it returns.

Spec section 3.5. The protocol is a :class:`typing.Protocol`, not a base class, so an adapter
satisfies it without importing anything from Quaestor -- and, deliberately, it is structurally
identical to Probatio's ``Provider``. That is not a coincidence to be tidied away later: it is the
mechanism by which the Phase 11 test layer records cassettes of Quaestor's own calls, because
Probatio's ``provider`` fixture is then already a valid :class:`LLM`.

:class:`Completion` is blunt about what it does not know. ``cost_usd`` is ``None`` when nobody
priced the call, never ``0.0`` as a stand-in, because a zero that means "unknown" turns a cost
ceiling into a check that always passes.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["LLM", "Completion"]


class Completion(BaseModel):
    """One model response, plus what it cost and how long it took.

    Attributes:
        text: The response text.
        model: The model that produced it, as the provider reports or was asked for it.
        tokens_in: Prompt tokens, or ``None`` when the provider does not report them.
        tokens_out: Completion tokens, or ``None`` when the provider does not report them.
        cost_usd: Cost in US dollars, or ``None`` when the call was not priced. Notional for
            :class:`~quaestor.llm.claude_cli.ClaudeCLILLM`; see its docstring.
        latency_ms: Wall-clock duration of the call in milliseconds.
        raw: The provider's own payload, carried for the record and for the trace.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str
    model: str
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    latency_ms: float = 0.0
    raw: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class LLM(Protocol):
    """Anything that can turn a prompt into a :class:`Completion`.

    Attributes:
        name: A short, stable identifier written into traces and cassettes, such as
            ``claude-cli``.
    """

    name: str

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Complete one user-turn prompt.

        Args:
            prompt: The user-turn text. Multi-turn is out of scope for v0.1; a caller that keeps
                a history flattens it into the prompt.
            system: The system prompt, when the caller has one.
            **params: Provider parameters, such as ``model``. An adapter that cannot honour a
                parameter says so rather than pretending.

        Returns:
            The completion.
        """
        ...
