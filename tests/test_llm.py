"""The provider layer, offline. No test in this file reaches a model, a key or the `claude` binary.

`ClaudeCLILLM` is tested by monkeypatching `subprocess.run` and returning the payload captured at
`tests/fixtures/claude_cli_payload.json` -- a real answer from a real CLI, recorded once by hand.
`AnthropicLLM` is tested with an injected stub client. Both adapters' argument vectors are asserted
on directly, because a flag that quietly stops being passed -- `--tools ""`, say -- would turn a
one-turn call into an agent with file access and nothing would fail.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from quaestor.errors import LLMProviderError
from quaestor.llm import AnthropicLLM, ClaudeCLILLM, Completion, FakeLLM, ScriptedLLM
from quaestor.llm.base import LLM
from quaestor.llm.claude_cli import STDIN_THRESHOLD_BYTES, UNKNOWN_MODEL

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PAYLOAD = json.loads((FIXTURES / "claude_cli_payload.json").read_text(encoding="utf-8"))


# --- the protocol ---------------------------------------------------------------------------------


@pytest.mark.parametrize("provider", [FakeLLM(), ScriptedLLM(["one"]), ClaudeCLILLM()])
def test_every_adapter_satisfies_the_protocol(provider: object) -> None:
    assert isinstance(provider, LLM)


def test_completion_is_frozen_and_closed() -> None:
    completion = Completion(text="hi", model="fake-1")
    with pytest.raises(ValueError, match="frozen"):
        completion.text = "bye"


def test_an_unpriced_call_reports_none_rather_than_zero() -> None:
    # A zero that means "unknown" turns a cost ceiling into a check that always passes.
    assert FakeLLM().complete("anything").cost_usd is None


# --- FakeLLM --------------------------------------------------------------------------------------


def test_a_substring_key_answers() -> None:
    llm = FakeLLM({"AUC": "0.7412"})
    assert llm.complete("what is the AUC on test?").text == "0.7412"
    assert llm.calls[0].prompt.startswith("what is")


def test_the_first_matching_substring_wins_in_insertion_order() -> None:
    llm = FakeLLM({"AUC": "first", "test": "second"})
    assert llm.complete("the AUC on test").text == "first"


def test_a_call_key_beats_a_substring() -> None:
    key = FakeLLM.call_key("draft the summary", None, {})
    llm = FakeLLM({key: "exact", "draft": "substring"})
    assert llm.complete("draft the summary").text == "exact"


def test_the_call_key_covers_system_and_params() -> None:
    assert FakeLLM.call_key("p", None, {}) != FakeLLM.call_key("p", "s", {})
    assert FakeLLM.call_key("p", None, {}) != FakeLLM.call_key("p", None, {"model": "opus"})


def test_a_string_default_answers_when_nothing_matches() -> None:
    assert FakeLLM({"AUC": "x"}, default="fallback").complete("no match").text == "fallback"


def test_a_callable_default_sees_the_prompt() -> None:
    llm = FakeLLM(default=lambda prompt: f"saw {len(prompt)} characters")
    assert llm.complete("12345").text == "saw 5 characters"


def test_the_fallback_is_stable_and_obviously_synthetic() -> None:
    llm = FakeLLM()
    first = llm.complete("draft section 3").text
    assert first.startswith("FAKE(")
    assert first == FakeLLM().complete("draft section 3").text
    assert first != llm.complete("draft section 4").text


def test_calls_are_recorded_in_order() -> None:
    llm = FakeLLM()
    llm.complete("one", system="be terse", model="opus")
    llm.complete("two")
    assert llm.call_count == 2
    assert llm.calls[0].system == "be terse"
    assert llm.calls[0].params == {"model": "opus"}
    assert [call.prompt for call in llm.calls] == ["one", "two"]


def test_a_fake_reports_its_configured_cost_and_latency() -> None:
    completion = FakeLLM(default="x", cost_usd=0.25, latency_ms=12.0).complete("p")
    assert completion.cost_usd == pytest.approx(0.25)
    assert completion.latency_ms == pytest.approx(12.0)
    assert completion.raw["matched"] == "default"


# --- ScriptedLLM ----------------------------------------------------------------------------------


def test_a_script_is_read_in_order_and_cycles() -> None:
    llm = ScriptedLLM(["one", "two"])
    assert [llm.complete("p").text for _ in range(4)] == ["one", "two", "one", "two"]


def test_an_empty_script_is_refused() -> None:
    with pytest.raises(LLMProviderError, match="at least one scripted answer"):
        ScriptedLLM([])


# --- ClaudeCLILLM: the argument vector ------------------------------------------------------------


def test_the_default_argument_vector_is_the_flag_list_of_d025() -> None:
    # No --bare: it restricts authentication to ANTHROPIC_API_KEY or an apiKeyHelper and never
    # reads OAuth, and the only login this project has is the operator's subscription (D-025).
    argv = ClaudeCLILLM().argv("draft the summary")
    assert argv == [
        "claude",
        "-p",
        "draft the summary",
        "--output-format",
        "json",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--tools",
        "",
    ]


def test_bare_is_not_passed_by_default() -> None:
    assert "--bare" not in ClaudeCLILLM().argv("p", system="s", model="m")


def test_bare_is_available_as_an_opt_in_for_an_operator_with_a_key() -> None:
    argv = ClaudeCLILLM(bare_flag="--bare").argv("p")
    assert argv[3] == "--bare"


def test_strict_mcp_config_is_passed_and_no_mcp_config_is_given() -> None:
    # --strict-mcp-config restricts MCP servers to those from --mcp-config, of which there are
    # none, so a validation call cannot reach a server configured on the operator's machine.
    argv = ClaudeCLILLM().argv("p")
    assert "--strict-mcp-config" in argv
    assert "--mcp-config" not in argv


def test_strict_mcp_config_can_be_dropped() -> None:
    assert "--strict-mcp-config" not in ClaudeCLILLM(strict_mcp_config_flag=None).argv("p")


def test_the_model_and_system_prompt_are_passed_through() -> None:
    argv = ClaudeCLILLM().argv("p", system="you validate models", model="claude-opus-5")
    assert argv[argv.index("--model") + 1] == "claude-opus-5"
    assert argv[argv.index("--system-prompt") + 1] == "you validate models"


def test_the_tools_flag_is_last_because_it_is_variadic() -> None:
    argv = ClaudeCLILLM(extra_args=["--verbose"]).argv("p", system="s", model="m")
    assert argv[-2:] == ["--tools", ""]
    assert "--verbose" in argv


def test_every_flag_is_one_the_installed_cli_documents() -> None:
    # The flag list was read from `claude --help` (notes/claude-help.txt) and recorded in
    # DECISIONS D-025; nothing may be invented here.
    documented = {
        "-p",
        "--bare",
        "--output-format",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--model",
        "--system-prompt",
        "--tools",
    }
    argv = ClaudeCLILLM(bare_flag="--bare").argv("p", system="s", model="m")
    assert {token for token in argv if token.startswith("-")} <= documented


# --- ClaudeCLILLM: the payload --------------------------------------------------------------------


def fake_run(
    monkeypatch: pytest.MonkeyPatch,
    *,
    payload: object = None,
    stdout: str | None = None,
    returncode: int = 0,
    stderr: str = "",
    raises: BaseException | None = None,
) -> list[list[str]]:
    """Replace `subprocess.run` with one that returns a captured payload. Records every argv."""
    seen: list[list[str]] = []

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        seen.append(list(argv))
        if raises is not None:
            raise raises
        text = stdout if stdout is not None else json.dumps(payload if payload else PAYLOAD)
        return subprocess.CompletedProcess(argv, returncode, text, stderr)

    monkeypatch.setattr(subprocess, "run", run)
    return seen


def test_the_captured_payload_maps_onto_a_completion(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch)
    completion = ClaudeCLILLM(model="claude-opus-5").complete("check the payload")
    assert completion.text == "PAYLOAD_CHECK"
    assert completion.model == "claude-opus-5"
    assert completion.tokens_in == 469
    assert completion.tokens_out == 14
    assert completion.cost_usd == pytest.approx(0.003769, rel=1e-3)
    assert completion.latency_ms == pytest.approx(2211.0)


def test_the_whole_payload_including_model_usage_is_kept_on_raw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The CLI records side calls to a second model; keeping modelUsage is how a trace can say so.
    fake_run(monkeypatch)
    raw = ClaudeCLILLM().complete("p").raw
    assert set(raw["modelUsage"]) == {"claude-haiku-4-5-20251001", "claude-opus-5[1m]"}
    assert raw["session_id"] == PAYLOAD["session_id"]


def test_the_model_is_unknown_when_the_payload_names_more_than_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_run(monkeypatch)
    assert ClaudeCLILLM().complete("p").model == UNKNOWN_MODEL


def test_the_model_is_taken_from_the_payload_when_it_names_exactly_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = dict(PAYLOAD, modelUsage={"claude-opus-5": {}})
    fake_run(monkeypatch, payload=payload)
    assert ClaudeCLILLM().complete("p").model == "claude-opus-5"


def test_whether_bare_was_passed_is_recorded_for_the_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_run(monkeypatch)
    assert ClaudeCLILLM().complete("p").raw["quaestor_bare"] is False
    assert ClaudeCLILLM(bare_flag="--bare").complete("p").raw["quaestor_bare"] is True


def test_an_unhonourable_parameter_is_recorded_rather_than_dropped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_run(monkeypatch)
    raw = ClaudeCLILLM().complete("p", temperature=0.2).raw
    assert raw["quaestor_ignored_params"] == ["temperature"]


def test_the_prompt_reaches_the_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = fake_run(monkeypatch)
    ClaudeCLILLM().complete("draft section 4")
    assert seen[0][2] == "draft section 4"


def calls_of(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Replace `subprocess.run` with one that records the whole call, kwargs included."""
    calls: list[dict[str, Any]] = []

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append({"argv": list(argv), **kwargs})
        return subprocess.CompletedProcess(argv, 0, json.dumps(PAYLOAD), "")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def test_a_short_prompt_is_the_positional_argument_and_nothing_is_written_to_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = calls_of(monkeypatch)
    llm = ClaudeCLILLM()
    prompt = "x" * (STDIN_THRESHOLD_BYTES - 1)
    assert llm.on_stdin(prompt) is False
    llm.complete(prompt)
    assert calls[0]["argv"][:3] == ["claude", "-p", prompt]
    assert calls[0]["input"] is None


def test_a_prompt_over_the_threshold_goes_on_stdin_with_no_positional_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A single argument this long is refused by the operating system before the CLI is reached,
    # so `-p` is passed with no prompt after it and the CLI reads the prompt from stdin (D-078).
    calls = calls_of(monkeypatch)
    llm = ClaudeCLILLM()
    prompt = "y" * (STDIN_THRESHOLD_BYTES + 1)
    assert llm.on_stdin(prompt) is True
    completion = llm.complete(prompt, system="s")
    assert completion.text == "PAYLOAD_CHECK"
    argv = calls[0]["argv"]
    assert argv[:3] == ["claude", "-p", "--output-format"]
    assert prompt not in argv
    assert calls[0]["input"] == prompt


def test_the_threshold_is_counted_in_utf8_bytes_not_in_characters() -> None:
    # A prompt of half as many multi-byte characters is the same number of bytes on the wire.
    llm = ClaudeCLILLM()
    assert llm.on_stdin("€" * (STDIN_THRESHOLD_BYTES // 3 + 1)) is True
    assert llm.on_stdin("€" * (STDIN_THRESHOLD_BYTES // 3 - 1)) is False


def test_a_payload_reporting_an_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, payload=dict(PAYLOAD, is_error=True, subtype="error_during_execution"))
    with pytest.raises(LLMProviderError, match="reported an error"):
        ClaudeCLILLM().complete("p")


def test_a_payload_with_a_non_success_subtype_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, payload=dict(PAYLOAD, subtype="error_max_turns"))
    with pytest.raises(LLMProviderError, match="error_max_turns"):
        ClaudeCLILLM().complete("p")


def test_a_payload_without_a_result_string_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {key: value for key, value in PAYLOAD.items() if key != "result"}
    fake_run(monkeypatch, payload=payload)
    with pytest.raises(LLMProviderError, match="no 'result' string"):
        ClaudeCLILLM().complete("p")


def test_a_payload_without_usage_reports_no_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {key: value for key, value in PAYLOAD.items() if key != "usage"}
    fake_run(monkeypatch, payload=payload)
    completion = ClaudeCLILLM().complete("p")
    assert completion.tokens_in is None
    assert completion.tokens_out is None


def test_the_cached_input_tokens_are_counted_as_input_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """D-093: `input_tokens` alone is what the cache neither wrote nor read, and is not the bill."""
    usage = dict(
        PAYLOAD["usage"],
        input_tokens=2,
        cache_creation_input_tokens=6_643,
        cache_read_input_tokens=600,
    )
    fake_run(monkeypatch, payload=dict(PAYLOAD, usage=usage))
    assert ClaudeCLILLM().complete("p").tokens_in == 7_245


def test_a_usage_object_that_reports_no_input_field_reports_no_tokens_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A provider that says nothing about its tokens must not be recorded as having used zero."""
    usage = {"output_tokens": 14}
    fake_run(monkeypatch, payload=dict(PAYLOAD, usage=usage))
    completion = ClaudeCLILLM().complete("p")
    assert completion.tokens_in is None
    assert completion.tokens_out == 14


def test_a_payload_without_a_duration_falls_back_to_measured_latency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {key: value for key, value in PAYLOAD.items() if key != "duration_api_ms"}
    fake_run(monkeypatch, payload=payload)
    assert ClaudeCLILLM().complete("p").latency_ms > 0.0


def test_a_non_zero_exit_raises_and_quotes_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, returncode=1, stderr="not logged in")
    with pytest.raises(LLMProviderError, match="not logged in"):
        ClaudeCLILLM().complete("p")


def test_unparsable_stdout_raises_and_quotes_the_beginning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_run(monkeypatch, stdout="Usage: claude [options]")
    with pytest.raises(LLMProviderError, match="no parsable json on stdout"):
        ClaudeCLILLM().complete("p")


def test_stdout_that_is_not_an_object_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, stdout="[]")
    with pytest.raises(LLMProviderError, match="not a JSON object"):
        ClaudeCLILLM().complete("p")


def test_a_missing_executable_names_the_install_command(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, raises=FileNotFoundError("claude"))
    with pytest.raises(LLMProviderError, match="was not found on PATH") as caught:
        ClaudeCLILLM().complete("p")
    assert "npm install" in str(caught.value)


def test_a_timeout_is_reported_with_its_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, raises=subprocess.TimeoutExpired("claude", 300.0, stderr=b"slow"))
    with pytest.raises(LLMProviderError, match="did not answer within 300s"):
        ClaudeCLILLM().complete("p")


def test_an_empty_stderr_is_rendered_rather_than_left_blank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_run(monkeypatch, returncode=2, stderr="   ")
    with pytest.raises(LLMProviderError, match="<empty>"):
        ClaudeCLILLM().complete("p")


def test_a_long_stderr_is_truncated(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, returncode=2, stderr="x" * 5000)
    with pytest.raises(LLMProviderError, match=r"\.\.\. \(truncated\)"):
        ClaudeCLILLM().complete("p")


# --- AnthropicLLM ---------------------------------------------------------------------------------


class StubBlock:
    def __init__(self, text: str, kind: str = "text") -> None:
        self.text = text
        self.type = kind


class StubResponse:
    def __init__(self, blocks: list[StubBlock]) -> None:
        self.content = blocks
        self.model = "claude-sonnet-4-5"
        self.stop_reason = "end_turn"
        self.usage = type("Usage", (), {"input_tokens": 120, "output_tokens": 45})()


class StubMessages:
    def __init__(self, response: object = None, raises: BaseException | None = None) -> None:
        self.response = response
        self.raises = raises
        self.requests: list[dict[str, Any]] = []

    def create(self, **request: Any) -> object:
        self.requests.append(request)
        if self.raises is not None:
            raise self.raises
        return self.response


class StubClient:
    def __init__(self, messages: StubMessages) -> None:
        self.messages = messages


def test_an_injected_client_needs_no_sdk_and_no_key() -> None:
    messages = StubMessages(StubResponse([StubBlock("drafted")]))
    llm = AnthropicLLM(client=StubClient(messages), model="claude-sonnet-4-5")
    completion = llm.complete("draft section 1", system="you validate models")
    assert completion.text == "drafted"
    assert completion.tokens_in == 120
    assert completion.tokens_out == 45
    assert completion.cost_usd is None
    request = messages.requests[0]
    assert request["messages"] == [{"role": "user", "content": "draft section 1"}]
    assert request["system"] == "you validate models"
    assert request["model"] == "claude-sonnet-4-5"


def test_parameters_override_the_defaults() -> None:
    messages = StubMessages(StubResponse([StubBlock("x")]))
    llm = AnthropicLLM(client=StubClient(messages))
    llm.complete("p", model="claude-opus-5", max_tokens=99, temperature=0.0)
    request = messages.requests[0]
    assert request["model"] == "claude-opus-5"
    assert request["max_tokens"] == 99
    assert request["temperature"] == 0.0


def test_text_blocks_are_concatenated_and_others_ignored() -> None:
    blocks = [StubBlock("one "), StubBlock("ignored", kind="thinking"), StubBlock("two")]
    llm = AnthropicLLM(client=StubClient(StubMessages(StubResponse(blocks))))
    assert llm.complete("p").text == "one two"


def test_a_response_with_no_text_block_raises() -> None:
    llm = AnthropicLLM(client=StubClient(StubMessages(StubResponse([]))))
    with pytest.raises(LLMProviderError, match="no text block"):
        llm.complete("p")


def test_an_sdk_failure_is_wrapped() -> None:
    llm = AnthropicLLM(client=StubClient(StubMessages(raises=RuntimeError("overloaded"))))
    with pytest.raises(LLMProviderError, match="overloaded"):
        llm.complete("p")


def test_no_system_prompt_means_no_system_key() -> None:
    messages = StubMessages(StubResponse([StubBlock("x")]))
    AnthropicLLM(client=StubClient(messages)).complete("p")
    assert "system" not in messages.requests[0]


def test_a_timeout_with_no_stderr_is_still_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_run(monkeypatch, raises=subprocess.TimeoutExpired("claude", 1.0))
    with pytest.raises(LLMProviderError, match="<empty>"):
        ClaudeCLILLM(timeout_s=1.0).complete("p")


def test_a_missing_sdk_names_the_extra_to_install(monkeypatch: pytest.MonkeyPatch) -> None:
    # `sys.modules[name] = None` is what an absent package looks like to `import`, so this holds
    # whether or not the optional extra happens to be installed in the running environment.
    monkeypatch.setitem(sys.modules, "anthropic", None)
    with pytest.raises(LLMProviderError, match="anthropic SDK is not installed") as caught:
        AnthropicLLM()
    assert "quaestor-mrm[anthropic]" in str(caught.value)


def test_the_sdk_client_is_built_only_when_none_is_injected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A stub module standing in for the SDK: this is the one code path that imports it, and it
    # must pass the key through to the client rather than reading it from anywhere itself.
    built: list[str | None] = []

    class StubSDK:
        @staticmethod
        def Anthropic(*, api_key: str | None = None) -> object:  # noqa: N802 - the SDK's name
            built.append(api_key)
            return StubClient(StubMessages(StubResponse([StubBlock("x")])))

    monkeypatch.setitem(sys.modules, "anthropic", StubSDK)
    llm = AnthropicLLM(api_key="not-a-real-key")
    assert built == ["not-a-real-key"]
    assert llm.complete("p").text == "x"
