"""``AnthropicLLM``: the Anthropic SDK, behind the same protocol as everything else.

Anthropic is the only live provider Quaestor ships, in two forms: this one, which needs an API key
and the optional ``anthropic`` extra, and :class:`~quaestor.llm.claude_cli.ClaudeCLILLM`, which
needs neither. There is no OpenAI adapter and there will not be one; the point of the project is
not provider breadth.

The SDK is imported inside the constructor, not at module import, so that ``import quaestor`` works
without the extra installed and the test suite never has the SDK on its import path by accident.
The client is injectable for the same reason: the tests pass a stub object with one ``messages``
attribute and assert on what was sent, which needs no network, no key and no SDK.
"""

from __future__ import annotations

import time
from typing import Any, Final

from ..errors import LLMProviderError
from .base import Completion

__all__ = ["DEFAULT_MAX_TOKENS", "DEFAULT_MODEL", "AnthropicLLM"]

DEFAULT_MODEL: Final = "claude-sonnet-4-5"
"""The model used when the caller names none. Overridden per call or per construction."""

DEFAULT_MAX_TOKENS: Final = 4096
"""Enough for one drafted section; the Messages API requires the parameter."""

_INSTALL_FIX: Final = "pip install 'quaestor-mrm[anthropic]'"


class AnthropicLLM:
    """One Anthropic Messages call per :meth:`complete`.

    Attributes:
        name: ``"anthropic"``.
        model: The default model.
        client: The SDK client, or whatever was injected in its place.
    """

    name: str = "anthropic"

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        client: Any = None,
        api_key: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> None:
        """Build or accept a client.

        Args:
            model: The default model, used for calls whose params name none.
            client: An SDK client to use as given. When ``None``, one is constructed, which is
                the only code path that imports the ``anthropic`` package.
            api_key: Passed to the constructed client; when ``None`` the SDK reads
                ``ANTHROPIC_API_KEY`` from the environment itself. Never read from a file, never
                logged, never written to a trace.
            max_tokens: The completion cap sent with every call.

        Raises:
            LLMProviderError: The ``anthropic`` extra is not installed and no client was given.
        """
        self.model = model
        self.max_tokens = max_tokens
        if client is not None:
            self.client = client
            return
        try:
            import anthropic
        except ImportError as exc:
            raise LLMProviderError(
                "the anthropic SDK is not installed, so AnthropicLLM cannot build a client; "
                "pass client=... or use --llm claude-cli, which needs no key",
                fix=_INSTALL_FIX,
            ) from exc
        self.client = anthropic.Anthropic(api_key=api_key)

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Send one user-turn message and map the response onto a :class:`Completion`.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when the caller has one.
            **params: ``model`` and ``max_tokens`` override this adapter's defaults; anything
                else is passed to the SDK unchanged, so a caller can set ``temperature``.

        Returns:
            The completion. ``cost_usd`` is ``None``: the Messages API does not price a call, and
            a zero would make a cost ceiling unenforceable.

        Raises:
            LLMProviderError: The SDK raised, or the response carried no text block.
        """
        request: dict[str, Any] = {
            "model": params.pop("model", None) or self.model,
            "max_tokens": params.pop("max_tokens", None) or self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system is not None:
            request["system"] = system
        request.update(params)
        started = time.perf_counter()
        try:
            response = self.client.messages.create(**request)
        except Exception as exc:  # noqa: BLE001 - the SDK's error tree is not ours to enumerate
            raise LLMProviderError(
                f"the Anthropic API call failed: {type(exc).__name__}: {exc}"
            ) from exc
        latency_ms = (time.perf_counter() - started) * 1000.0
        return _completion(response, model=str(request["model"]), latency_ms=latency_ms)


def _completion(response: Any, *, model: str, latency_ms: float) -> Completion:
    """Map an SDK response onto a completion, insisting that it carried text."""
    blocks = getattr(response, "content", None) or []
    texts = [str(block.text) for block in blocks if getattr(block, "type", None) == "text"]
    if not texts:
        raise LLMProviderError(
            "the Anthropic response carried no text block, so there is no answer to use"
        )
    usage = getattr(response, "usage", None)
    return Completion(
        text="".join(texts),
        model=str(getattr(response, "model", model) or model),
        tokens_in=_int_or_none(getattr(usage, "input_tokens", None)),
        tokens_out=_int_or_none(getattr(usage, "output_tokens", None)),
        cost_usd=None,
        latency_ms=latency_ms,
        raw={"stop_reason": getattr(response, "stop_reason", None)},
    )


def _int_or_none(value: Any) -> int | None:
    """Coerce a reported token count to ``int``, or to ``None`` when it is absent."""
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else None
