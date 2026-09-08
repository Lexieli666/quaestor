"""``ClaudeCLILLM``: the Claude Code CLI as a subprocess, for a developer on a subscription.

This adapter is why Quaestor can be run live at all without an API key: a developer with the CLI
installed and signed in runs ``quaestor validate --llm claude-cli``, and the Phase 12 study runs
the same way. It is never reached by the test suite, which monkeypatches :func:`subprocess.run`
and reads the captured payload committed at ``tests/fixtures/claude_cli_payload.json``.

The contract needed from the CLI is one non-interactive turn, machine-readable, with no project
context, no MCP servers and no tools. Every flag is a constructor argument, because these flags
belong to a version of somebody else's program: when one changes, a user overrides one argument
instead of waiting for a Quaestor release. The exact flag list and the reason for each is
DECISIONS D-025.

**Authentication.** The default vector deliberately does *not* pass ``--bare``. ``--bare`` restricts
Anthropic authentication to ``ANTHROPIC_API_KEY`` or an ``apiKeyHelper`` and never reads OAuth or
the keychain, so it cannot run on a subscription login -- which is the only login this project has,
since ``CLAUDE.md`` forbids an API key anywhere. Project context is excluded instead by running each
call in an empty temporary working directory, and MCP servers by ``--strict-mcp-config``. An
operator who does have a key may opt in with ``bare_flag="--bare"``; what it additionally suppresses
(hooks, plugins, auto-memory, user-level ``CLAUDE.md``) is named as a limitation in
``docs/DESIGN.md``, Phase 2. Whether it was passed is recorded on every ``llm_call`` trace event as
``quaestor_bare``, so a published run says which of the two it was.

**Long prompts.** The prompt is the positional argument after ``-p`` until it exceeds
:data:`STDIN_THRESHOLD_BYTES`, at which point it is written to the subprocess's stdin instead and
no positional argument is emitted -- which is how ``claude -p`` reads a prompt when it is given
none. The operating system caps the length of a single argument well below the total it allows,
so a large prompt otherwise fails before the CLI runs at all (DECISIONS D-078).

**Cost caveat.** ``total_cost_usd`` in the payload is the *notional* API price of the turn as the
CLI computes it. A developer running this on a Claude subscription is not billed that money. It is
reported because it is the only cost signal available and it makes ``--max-cost`` enforceable, not
because it is an invoice. Every document that prints it calls it notional.

**Model attribution.** The payload's ``modelUsage`` can name more than one model, because the CLI
bills side work to a small model alongside the model that answered. Picking the busiest of them
would be a guess written into every trace, so the model is what the caller asked for, and the whole
payload -- ``modelUsage`` included -- is carried on :attr:`Completion.raw`.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from collections.abc import Sequence
from typing import Any, Final

from ..errors import LLMProviderError
from .base import Completion

__all__ = ["DEFAULT_TIMEOUT_S", "STDIN_THRESHOLD_BYTES", "UNKNOWN_MODEL", "ClaudeCLILLM"]

DEFAULT_TIMEOUT_S: Final = 300.0
"""A section draft with no tools is quick; five minutes is a hung-process ceiling, not a budget."""

UNKNOWN_MODEL: Final = "claude-cli"
"""Reported as the model when neither the caller nor the payload names exactly one."""

_STDERR_LIMIT: Final = 2000
"""How much of the CLI's stderr an error message quotes before truncating it."""

STDIN_THRESHOLD_BYTES: Final = 64 * 1024
"""Above this many UTF-8 bytes the prompt is written to the CLI's stdin instead of to ``argv``.

A single argument on macOS is capped well below the total ``ARG_MAX``, so a long enough positional
prompt fails with ``OSError: [Errno 7] Argument list too long`` before the CLI is even reached --
and a ``plain_llm`` prompt, which carries four contract files at once, is the call that reaches
that size first. Under ``-p`` with no positional prompt the CLI reads the prompt from stdin, so
the same call is made the other way round. 64 KiB is a conservative fraction of the smallest limit
either supported platform imposes; it is not a tuned number (DECISIONS D-078)."""


class ClaudeCLILLM:
    """Runs ``claude -p`` once per call and parses its JSON result.

    Attributes:
        name: ``"claude-cli"``, which is what the report's front matter and the trace record.
    """

    name: str = "claude-cli"

    def __init__(
        self,
        *,
        model: str | None = None,
        executable: str = "claude",
        timeout_s: float = DEFAULT_TIMEOUT_S,
        print_flag: str = "-p",
        bare_flag: str | None = None,
        output_format_flag: str = "--output-format",
        output_format: str = "json",
        session_persistence_flag: str = "--no-session-persistence",
        strict_mcp_config_flag: str | None = "--strict-mcp-config",
        model_flag: str = "--model",
        system_prompt_flag: str = "--system-prompt",
        tools_flag: str = "--tools",
        tools: str = "",
        extra_args: Sequence[str] = (),
        stdin_threshold_bytes: int = STDIN_THRESHOLD_BYTES,
    ) -> None:
        """Configure the executable, the timeout and every flag name used to invoke it.

        Args:
            model: The default model, used for calls whose params name none.
            executable: The CLI to run; a path works as well as a name on ``PATH``.
            timeout_s: Seconds before the subprocess is killed and the call fails.
            print_flag: Non-interactive mode. The prompt is the positional argument after it.
            bare_flag: ``None`` by default, so ``--bare`` is *not* passed and the call uses the
                operator's ordinary login. Pass ``"--bare"`` to opt in, which additionally
                suppresses hooks, plugins, auto-memory and user-level ``CLAUDE.md`` -- and which
                requires ``ANTHROPIC_API_KEY`` or an ``apiKeyHelper``, because ``--bare`` never
                reads OAuth or the keychain (DECISIONS D-025).
            output_format_flag: Selects the output format.
            output_format: The format value; the parser here expects ``json``.
            session_persistence_flag: Stops the run being written to the session store.
            strict_mcp_config_flag: Restricts MCP servers to those given by ``--mcp-config``, of
                which this adapter passes none, so no MCP server is loaded. ``None`` drops it.
            model_flag: Passes the model through.
            system_prompt_flag: Passes the system prompt through.
            tools_flag: Selects the available built-in tools.
            tools: The empty string disables all tools. With no tools the CLI cannot take a second
                turn, which is how "one turn" is obtained on a version with no ``--max-turns``.
            extra_args: Further arguments, inserted before the tools flag.
            stdin_threshold_bytes: Prompts larger than this many UTF-8 bytes are written to the
                subprocess's stdin instead of being passed as the positional argument, because a
                single argument that long is refused by the operating system (D-078).
        """
        self.model = model
        self.executable = executable
        self.timeout_s = timeout_s
        self.print_flag = print_flag
        self.bare_flag = bare_flag
        self.output_format_flag = output_format_flag
        self.output_format = output_format
        self.session_persistence_flag = session_persistence_flag
        self.strict_mcp_config_flag = strict_mcp_config_flag
        self.model_flag = model_flag
        self.system_prompt_flag = system_prompt_flag
        self.tools_flag = tools_flag
        self.tools = tools
        self.extra_args = list(extra_args)
        self.stdin_threshold_bytes = stdin_threshold_bytes

    def on_stdin(self, prompt: str) -> bool:
        """Say whether this prompt goes on stdin rather than into the argument vector.

        Args:
            prompt: The user-turn text.

        Returns:
            ``True`` when the prompt is larger than :data:`STDIN_THRESHOLD_BYTES` encoded as
            UTF-8. A single argument that long is refused by the operating system before the CLI
            runs, and ``-p`` with no positional prompt reads it from stdin instead (D-078).
        """
        return len(prompt.encode("utf-8")) > self.stdin_threshold_bytes

    def argv(
        self, prompt: str, *, system: str | None = None, model: str | None = None
    ) -> list[str]:
        """Build the command line for one call.

        The tools flag is variadic on this CLI version, so it is placed last: anything after it
        would be read as another tool name rather than as the next flag.

        Args:
            prompt: The user-turn text, passed as the positional prompt argument -- unless
                :meth:`on_stdin` says it is too long, in which case no positional argument is
                emitted at all and the caller writes the prompt to the subprocess's stdin.
            system: The system prompt, when the caller has one.
            model: The model to pass through, when one is configured.

        Returns:
            The full argument vector, executable first.
        """
        argv = [self.executable, self.print_flag]
        if not self.on_stdin(prompt):
            argv.append(prompt)
        if self.bare_flag:
            argv.append(self.bare_flag)
        argv += [self.output_format_flag, self.output_format, self.session_persistence_flag]
        if self.strict_mcp_config_flag:
            argv.append(self.strict_mcp_config_flag)
        if model:
            argv += [self.model_flag, model]
        if system is not None:
            argv += [self.system_prompt_flag, system]
        argv += self.extra_args
        argv += [self.tools_flag, self.tools]
        return argv

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Run one turn and map the CLI's JSON result onto a :class:`Completion`.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when the caller has one.
            **params: ``model`` overrides the constructor's; the rest are recorded on ``raw`` as
                ignored, because this CLI version exposes no flag for them.

        Returns:
            The completion, with the CLI's notional cost and its API latency.

        Raises:
            LLMProviderError: The executable is missing, the call timed out, it exited non-zero,
                its stdout was not the expected JSON, or the payload reports an error.
        """
        ignored = dict(params)
        model = ignored.pop("model", None) or self.model
        argv = self.argv(prompt, system=system, model=model)
        started = time.perf_counter()
        completed = self._run(argv, prompt if self.on_stdin(prompt) else None)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        payload = self._payload(argv, completed)
        return self._completion(payload, model=model, elapsed_ms=elapsed_ms, ignored=ignored)

    def _run(
        self, argv: Sequence[str], stdin: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        """Run the CLI in an empty temporary directory, so no project context is discovered.

        Args:
            argv: The argument vector, which carries the prompt unless it was too long for one.
            stdin: The prompt, when it goes that way instead; ``None`` otherwise.

        Returns:
            The completed process.

        Raises:
            LLMProviderError: The executable is missing or the call timed out.
        """
        with tempfile.TemporaryDirectory(prefix="quaestor-claude-cli-") as empty:
            try:
                return subprocess.run(
                    list(argv),
                    cwd=empty,
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_s,
                    check=False,
                )
            except FileNotFoundError as exc:
                raise LLMProviderError(
                    f"the Claude CLI executable {self.executable!r} was not found on PATH",
                    fix="npm install -g @anthropic-ai/claude-code",
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise LLMProviderError(
                    f"the Claude CLI did not answer within {self.timeout_s:g}s; "
                    f"stderr: {_tail(exc.stderr)}"
                ) from exc

    def _payload(
        self, argv: Sequence[str], completed: subprocess.CompletedProcess[str]
    ) -> dict[str, Any]:
        """Parse the CLI's stdout, quoting stderr on every failure so the cause is visible."""
        stderr = _tail(completed.stderr)
        if completed.returncode != 0:
            raise LLMProviderError(
                f"the Claude CLI exited {completed.returncode} for "
                f"{' '.join(argv[:2])!r}; stderr: {stderr}"
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(
                f"the Claude CLI wrote no parsable {self.output_format} on stdout: {exc}; "
                f"stdout began {completed.stdout[:200]!r}; stderr: {stderr}"
            ) from exc
        if not isinstance(payload, dict):
            raise LLMProviderError(
                f"the Claude CLI wrote a {type(payload).__name__}, not a JSON object; "
                f"stderr: {stderr}"
            )
        if payload.get("is_error") or payload.get("subtype", "success") != "success":
            raise LLMProviderError(
                f"the Claude CLI reported an error: subtype={payload.get('subtype')!r}, "
                f"api_error_status={payload.get('api_error_status')!r}, "
                f"result={str(payload.get('result'))[:200]!r}; stderr: {stderr}"
            )
        return payload

    def _completion(
        self,
        payload: dict[str, Any],
        *,
        model: str | None,
        elapsed_ms: float,
        ignored: dict[str, Any],
    ) -> Completion:
        """Map a successful payload onto a completion."""
        result = payload.get("result")
        if not isinstance(result, str):
            raise LLMProviderError(
                "the Claude CLI payload has no 'result' string, so there is no answer to use"
            )
        usage = payload.get("usage")
        usage = usage if isinstance(usage, dict) else {}
        raw: dict[str, Any] = dict(payload)
        # `quaestor_`-prefixed keys are this adapter's own provenance, copied onto the `llm_call`
        # trace event by `structured()`. A published run must be able to say whether it ran with
        # the operator's ordinary login or under `--bare` (DECISIONS D-025).
        raw["quaestor_bare"] = self.bare_flag is not None
        if ignored:
            raw["quaestor_ignored_params"] = sorted(ignored)
        return Completion(
            text=result,
            model=model or _model_of(payload),
            tokens_in=_input_tokens(usage),
            tokens_out=_int_or_none(usage.get("output_tokens")),
            cost_usd=_float_or_none(payload.get("total_cost_usd")),
            latency_ms=_float_or_none(payload.get("duration_api_ms")) or elapsed_ms,
            raw=raw,
        )


_INPUT_TOKEN_FIELDS: Final = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)
"""Every field of the CLI's ``usage`` object that counts as a token the request sent.

``input_tokens`` alone is what was neither written to nor read from the prompt cache, which for a
CLI run that caches the system prompt is a handful of tokens: the third live validation recorded
**38 tokens in for 19 calls** while its cassettes show 176,851 across the three fields. A cost
table built on that number says a report was drafted from nothing (DECISIONS D-093).
"""


def _input_tokens(usage: dict[str, Any]) -> int | None:
    """Return every input token the request was billed for, cached ones included.

    Args:
        usage: The CLI payload's ``usage`` object.

    Returns:
        The sum of the three input-token fields, or ``None`` when the payload reports none of
        them -- a provider that says nothing about its tokens must not be recorded as having used
        zero.
    """
    counts = [_int_or_none(usage.get(field)) for field in _INPUT_TOKEN_FIELDS]
    present = [count for count in counts if count is not None]
    return sum(present) if present else None


def _model_of(payload: dict[str, Any]) -> str:
    """Name the model from the payload, but only when the payload names exactly one."""
    usage = payload.get("modelUsage")
    if isinstance(usage, dict) and len(usage) == 1:
        return str(next(iter(usage)))
    return UNKNOWN_MODEL


def _int_or_none(value: Any) -> int | None:
    """Coerce a reported token count to ``int``, or to ``None`` when it is absent."""
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _float_or_none(value: Any) -> float | None:
    """Coerce a reported cost or duration to ``float``, or to ``None`` when it is absent."""
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _tail(stderr: str | bytes | None) -> str:
    """Render a subprocess's stderr for an error message, truncating a long one."""
    if stderr is None:
        return "<empty>"
    text = stderr.decode("utf-8", errors="replace") if isinstance(stderr, bytes) else stderr
    text = text.strip()
    if not text:
        return "<empty>"
    return text if len(text) <= _STDERR_LIMIT else f"{text[:_STDERR_LIMIT]}... (truncated)"
