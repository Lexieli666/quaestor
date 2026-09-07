"""The exception hierarchy: one base class, one subclass per stage of the pipeline.

Spec section 3.1 fixes the list. Every error carries a message that names the thing that failed --
the package, the tool, the artifact, the claim -- and, where one exists, the command that fixes it.
That second half is the reason this is a hierarchy rather than a handful of ``ValueError``s: a
validator who runs ``quaestor validate`` on somebody else's model package needs to be told what to
run next, not only what went wrong.

The hierarchy is closed. A new stage does not get a new exception class without a ``DECISIONS.md``
entry, because the CLI's top-level handler and the study's resumability both branch on these
types. Two additions this project made: :class:`LLMProviderError`, which is a transport failure
rather than a bad answer (DECISIONS D-024), and :class:`CorpusError`, which is the regulatory
corpus failing to ingest, load or resolve (DECISIONS D-058).
"""

from __future__ import annotations

__all__ = [
    "ArtifactError",
    "CorpusError",
    "LLMOutputError",
    "LLMProviderError",
    "PackageError",
    "QuaestorError",
    "ReportSchemaError",
    "SandboxError",
    "ToolError",
    "VerificationError",
]


class QuaestorError(Exception):
    """Base class for every error Quaestor raises deliberately.

    Attributes:
        message: What went wrong, naming the package, tool, artifact or claim involved.
        fix: A command the user can run to fix it, or ``None`` when there is no single one.
    """

    def __init__(self, message: str, *, fix: str | None = None) -> None:
        """Record the message and the fixing command.

        Args:
            message: What went wrong. Name the thing: a message that says "invalid value" without
                saying which field of which file is a message that costs its reader a grep.
            fix: The command that fixes it, when one exists.
        """
        super().__init__(message)
        self.message = message
        self.fix = fix

    def __str__(self) -> str:
        """Return the message, with the fixing command appended when there is one."""
        return f"{self.message}\n  fix: {self.fix}" if self.fix else self.message


class PackageError(QuaestorError):
    """A model package is malformed, unreadable, or does not match its own manifest."""


class SandboxError(QuaestorError):
    """A subject run failed, breached a cap, or did not write the artifact contract of spec 3.3."""


class ArtifactError(QuaestorError):
    """An artifact is missing, is of the wrong kind, or a citation into it does not resolve."""


class CorpusError(QuaestorError):
    """The regulatory corpus cannot be ingested, read, or asked for a document.

    Distinct from :class:`ArtifactError`, which is a citation into *this run's* computed evidence.
    A ``[[reg:...]]`` citation that names a section the guidance does not have is not raised: it
    resolves to ``dangling``, because a drafter inventing a section is prose to repair, not a
    pipeline failure (DECISIONS D-058).
    """


class ToolError(QuaestorError):
    """A tool was called with arguments it cannot honour, or failed while running."""


class LLMOutputError(QuaestorError):
    """A model answered, but its answer is not what the caller can use.

    Raised by :func:`quaestor.llm.structured` when the JSON is unparsable or fails validation on
    the last attempt. The raw text is carried on the exception, because the study needs to count
    and inspect these without re-running the call.

    Attributes:
        raw: The model's answer as received, unparsed.
    """

    def __init__(self, message: str, *, raw: str | None = None, fix: str | None = None) -> None:
        """Record the message, the raw answer and the fixing command.

        Args:
            message: What was wrong with the answer.
            raw: The model's answer as received. Kept so a failure is diagnosable from the
                exception alone, without a second live call.
            fix: The command that fixes it, when one exists.
        """
        super().__init__(message, fix=fix)
        self.raw = raw


class LLMProviderError(QuaestorError):
    """A provider could not be reached, timed out, or reported a transport-level failure.

    Distinct from :class:`LLMOutputError`, which means the model answered and the answer was
    unusable. The distinction is what lets the study retry a transport failure and record a bad
    answer (DECISIONS D-024).
    """


class VerificationError(QuaestorError):
    """The claim verifier cannot run: a grammar, tolerance or store contract is violated."""


class ReportSchemaError(QuaestorError):
    """A report does not satisfy ``docs/REPORT_SCHEMA.md``, so the renderer refuses to write it."""
