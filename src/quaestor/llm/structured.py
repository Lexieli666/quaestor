"""``structured``: ask a model for JSON, validate it, re-ask once, then give up loudly.

Spec section 3.5. Every place Quaestor needs a model to produce a shape rather than prose -- the
section drafter, the claim extractor, the planner's action loop -- goes through this function, so
that "the model returned something unusable" has exactly one meaning, one retry policy and one
trace signature across the whole pipeline.

The retry is deliberately one, and the second failure is fatal. A loop that keeps re-asking hides
a prompt that does not work behind a cost line, and the study counts re-asks as a quality signal:
a configuration that needs three of them per section is worse than one that needs none, and that
only shows up if re-asks are rare enough to be counted rather than amortised.

**Rejected alternative:** the Claude Code CLI's ``--json-schema`` flag, which would let the CLI
adapter enforce the schema server-side. :class:`~quaestor.llm.anthropic.AnthropicLLM` cannot offer
the same thing through the Messages API without tool-use scaffolding, so using it would mean two
providers with two different failure modes and a re-ask count that means different things in the
two halves of the study. Validation stays here, in provider-agnostic code, and every provider
fails identically. See ``docs/DESIGN.md``, Phase 2.
"""

from __future__ import annotations

import json
import re
from typing import Any, Final, TypeVar

from pydantic import BaseModel, ValidationError

from ..errors import LLMOutputError
from ..trace import TraceWriter
from .base import LLM, Completion

__all__ = [
    "JSON_INSTRUCTION",
    "PROVENANCE_PREFIX",
    "REASK_PURPOSE",
    "strip_fence",
    "structured",
]

ModelT = TypeVar("ModelT", bound=BaseModel)

JSON_INSTRUCTION: Final = (
    "Answer with one JSON object and nothing else: no prose before or after it, no explanation, "
    "no markdown fence. It must validate against this JSON schema:\n{schema}"
)
"""Appended to every prompt. The schema is generated from the pydantic model, never restated."""

REASK_PURPOSE: Final = "reask"
"""The ``llm_call`` purpose that marks a retry, so the study can count them."""

PROVENANCE_PREFIX: Final = "quaestor_"
"""Keys an adapter puts on ``Completion.raw`` under this prefix are copied onto the trace event.

An adapter knows things about its own call that no caller can see -- which flags the Claude CLI was
invoked with, which parameters it could not honour -- and a published run has to be able to state
them. Namespacing them keeps :func:`structured` provider-agnostic: it copies a prefix, it does not
know what ``quaestor_bare`` means.
"""

_FENCE_RE: Final = re.compile(
    r"^\s*```(?:[A-Za-z0-9_+-]*)\s*\n(?P<body>.*?)\n?\s*```\s*$", re.DOTALL
)
"""One fenced block wrapping the whole answer. Exactly one is stripped, and only at the ends."""


def strip_fence(text: str) -> str:
    """Remove one markdown code fence wrapping the whole answer.

    A model told to answer with JSON and nothing else will still occasionally wrap it in a fence.
    Exactly one wrapper is removed, and only when it encloses the entire answer: stripping every
    fence anywhere would silently concatenate a model's two candidate answers into one.

    Args:
        text: The model's answer.

    Returns:
        The answer with one enclosing fence removed, stripped of surrounding whitespace.
    """
    match = _FENCE_RE.match(text)
    return match.group("body").strip() if match else text.strip()


def structured(
    llm: LLM,
    prompt: str,
    schema: type[ModelT],
    *,
    system: str | None = None,
    max_attempts: int = 2,
    trace: TraceWriter | None = None,
    purpose: str = "structured",
    **params: Any,
) -> ModelT:
    """Ask a model for a JSON object of one shape and return it validated.

    Args:
        llm: Any provider satisfying the :class:`~quaestor.llm.base.LLM` protocol.
        prompt: The task. The strict-JSON instruction and the schema are appended to it.
        schema: The pydantic model the answer must validate against.
        system: The system prompt, when the caller has one.
        max_attempts: How many calls may be made in total. The default of 2 is one ask and one
            re-ask; ``1`` disables the retry.
        trace: The run's trace writer. Every call is an ``llm_call`` event; a retry carries
            ``purpose`` :data:`REASK_PURPOSE`.
        purpose: The ``llm_call`` purpose recorded for the first attempt -- ``"draft"``,
            ``"extract"``, ``"plan"``.
        **params: Passed to the provider, such as ``model``.

    Returns:
        The validated model instance.

    Raises:
        LLMOutputError: The last attempt did not parse or did not validate. The exception carries
            the raw text of that attempt, so the failure is diagnosable without a second call.
        ValueError: ``max_attempts`` is below 1.
    """
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be at least 1, not {max_attempts}")
    instruction = JSON_INSTRUCTION.format(schema=json.dumps(schema.model_json_schema()))
    ask = f"{prompt}\n\n{instruction}"
    problem = ""
    completion: Completion | None = None
    for attempt in range(1, max_attempts + 1):
        completion = llm.complete(ask, system=system, **params)
        if trace is not None:
            trace.llm_call(
                purpose=purpose if attempt == 1 else REASK_PURPOSE,
                model=completion.model,
                tokens_in=completion.tokens_in,
                tokens_out=completion.tokens_out,
                cost_usd=completion.cost_usd,
                latency_ms=completion.latency_ms,
                schema=schema.__name__,
                attempt=attempt,
                **_provenance(completion),
            )
        parsed, problem = _validate(completion.text, schema)
        if parsed is not None:
            return parsed
        ask = (
            f"{prompt}\n\n{instruction}\n\nYour previous answer was rejected:\n{problem}\n"
            f"Answer again with one JSON object that validates, and nothing else."
        )
    raw = completion.text if completion is not None else ""
    raise LLMOutputError(
        f"the model did not return a valid {schema.__name__} in {max_attempts} attempt(s): "
        f"{problem}",
        raw=raw,
    )


def _provenance(completion: Completion) -> dict[str, Any]:
    """Return the adapter's own ``quaestor_``-prefixed keys, for the ``llm_call`` trace event."""
    return {
        key: value for key, value in completion.raw.items() if key.startswith(PROVENANCE_PREFIX)
    }


def _validate(text: str, schema: type[ModelT]) -> tuple[ModelT | None, str]:
    """Parse and validate one answer, returning either the model or why it was rejected."""
    body = strip_fence(text)
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        return None, f"it is not JSON ({exc}); it began {body[:200]!r}"
    try:
        return schema.model_validate(payload), ""
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or '<root>'}: {error['msg']}"
            for error in exc.errors()
        )
        return None, f"it does not validate against {schema.__name__}: {problems}"
