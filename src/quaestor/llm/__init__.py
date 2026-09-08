"""The ``LLM`` protocol, ``Completion``, the offline fakes and the two live adapters.

Filled in Phase 2 from spec section 3.5. The protocol is structurally identical
to Probatio's ``Provider`` on purpose: Probatio's ``provider`` fixture is then a valid ``LLM``,
which is how the test layer records cassettes of Quaestor's own calls. Anthropic is the only live
provider shipped: ``AnthropicLLM`` over the SDK and ``ClaudeCLILLM`` over the Claude Code CLI.

Phase 9 adds two things the command line needs: ``OfflineLLM``, the deterministic provider behind
``--llm fake``, which is what makes the quick start and the demo run with no network at all; and
``RecordingLLM`` / ``ReplayLLM``, which keep a live run's calls beside its report and play them
back (``--record-cassettes``, ``--llm replay``).
"""

from __future__ import annotations

from .anthropic import AnthropicLLM
from .base import LLM, Completion
from .claude_cli import ClaudeCLILLM
from .fake import FakeCall, FakeLLM, ScriptedLLM
from .offline import OfflineLLM
from .recording import RecordingLLM, ReplayLLM
from .structured import (
    JSON_INSTRUCTION,
    PROVENANCE_PREFIX,
    REASK_PURPOSE,
    strip_fence,
    structured,
)

__all__ = [
    "JSON_INSTRUCTION",
    "LLM",
    "PROVENANCE_PREFIX",
    "REASK_PURPOSE",
    "AnthropicLLM",
    "ClaudeCLILLM",
    "Completion",
    "FakeCall",
    "FakeLLM",
    "OfflineLLM",
    "RecordingLLM",
    "ReplayLLM",
    "ScriptedLLM",
    "strip_fence",
    "structured",
]
