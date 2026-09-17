"""The tool contract: ``ToolContext``, ``ToolResult``, ``Tool`` and the ``ToolRegistry``.

Spec section 3.7. A tool is a class with a name, a description, a pydantic ``Args`` model and a
``run(args, ctx) -> ToolResult``. The JSON schema is generated from ``Args`` once, at registration,
and three callers read the same one: the planner (Phase 8), the MCP server (Phase 15) and the CLI's
``quaestor tool NAME --args-json`` (Phase 9). Nothing restates a tool's arguments in prose, which
is what keeps those three from drifting apart.

Every call goes through :meth:`ToolRegistry.call`, which validates the arguments, times the run and
writes the ``tool_call`` trace event of spec section 3.1 -- the tool, the hash of its arguments,
the duration and the artifacts produced -- so that ``eval/score.py`` can count what a run did
without reading a word of its prose. A tool that emitted its own event would be counted twice, so
none does: :class:`~quaestor.tools.run.RunModelTool` deliberately calls
:func:`quaestor.sandbox.run_model` without a trace and lets the registry write the one event.

``Args`` models set ``extra="forbid"``: an action from the bounded follow-up loop that invents an
argument is rejected and traced rather than silently ignored, which is the difference between a
planner that can be held to its schema and one that cannot.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from ..artifacts import Artifact, ArtifactStore
from ..errors import ToolError
from ..findings import FindingCandidate
from ..hashing import stable_hash
from ..package import ModelPackage
from ..trace import EventType, TraceWriter
from .thresholds import Thresholds

__all__ = [
    "Tool",
    "ToolArgs",
    "ToolContext",
    "ToolRegistry",
    "ToolResult",
]


class ToolArgs(BaseModel):
    """The base of every tool's ``Args`` model: closed, frozen and JSON-schema-able.

    ``extra="forbid"`` is the point of the class. An argument a tool does not declare is a
    misunderstanding -- of the schema by a model, or of the tool by a caller -- and a tool that
    ignored it would run the wrong check and report that it had run the right one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)


@dataclass(frozen=True)
class ToolContext:
    """What every tool is given besides its arguments.

    A dataclass rather than a pydantic model because three of its five fields are objects with
    behaviour -- a store, a trace writer, a threshold table -- and validating them structurally
    would buy nothing.

    Attributes:
        package: The loaded package being validated.
        store: Where artifacts go, and where a later tool reads an earlier one's.
        out_dir: Where the subject wrote the standard artifact contract of spec section 3.3. Every
            tool reads its inputs from there and from the store, never from the package's data.
        trace: The run's trace, or ``None`` when a tool is being exercised on its own.
        thresholds: The effective thresholds, defaults included.
    """

    package: ModelPackage
    store: ArtifactStore
    out_dir: Path
    trace: TraceWriter | None = None
    thresholds: Thresholds = Thresholds()

    @property
    def splits(self) -> list[str]:
        """The splits the package declares, in report order."""
        return self.package.spec.splits.names()


class ToolResult(BaseModel):
    """What one tool call produced.

    Attributes:
        tool: The tool's name, so a result can be read on its own.
        artifacts: Every artifact the call stored, in the order it stored them.
        candidates: The finding candidates the call raised; usually none.
        summary: One or two sentences for a human, naming the numbers that decided the candidates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    tool: str
    artifacts: list[Artifact] = []
    candidates: list[FindingCandidate] = []
    summary: str = ""

    @property
    def artifact_names(self) -> list[str]:
        """The logical names of the artifacts this call stored, in order."""
        return [artifact.name for artifact in self.artifacts]

    @property
    def classes(self) -> list[str]:
        """The defect classes this call raised, sorted and deduplicated."""
        return sorted({candidate.defect_class.value for candidate in self.candidates})


ArgsT = TypeVar("ArgsT", bound=ToolArgs)


class Tool(Generic[ArgsT], ABC):
    """One check: a name, a description, an ``Args`` model and a ``run``.

    Attributes:
        name: The name the planner, the CLI and the MCP server call it by.
        description: One sentence, shown to the model in the bounded follow-up loop and to a user
            by ``quaestor tool --help``.
        Args: The pydantic model its arguments are validated against.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    Args: ClassVar[type[ToolArgs]]

    @abstractmethod
    def run(self, args: ArgsT, ctx: ToolContext) -> ToolResult:
        """Run the check and return its artifacts, candidates and summary.

        Args:
            args: The validated arguments.
            ctx: The package, the store, the run's output directory, the trace and the thresholds.

        Returns:
            The result.

        Raises:
            ToolError: The check cannot run against this package or this run directory.
        """

    def parse(self, args: Mapping[str, Any] | ToolArgs | None) -> ToolArgs:
        """Validate raw arguments against this tool's ``Args`` model.

        Args:
            args: A mapping, an already-built ``Args``, or ``None`` for the defaults.

        Returns:
            The validated arguments.

        Raises:
            ToolError: A field is missing, of the wrong type, or not declared at all. The message
                names the field and the tool.
        """
        if isinstance(args, self.Args):
            return args
        if isinstance(args, ToolArgs):
            raise ToolError(
                f"tool {self.name!r} takes {self.Args.__qualname__}, not {type(args).__qualname__}"
            )
        try:
            return self.Args.model_validate(dict(args or {}))
        except ValidationError as exc:
            problems = "; ".join(
                f"{'.'.join(str(part) for part in error['loc']) or '<root>'}: {error['msg']}"
                for error in exc.errors()
            )
            raise ToolError(
                f"tool {self.name!r} cannot take these arguments: {problems}",
                fix=f"quaestor tool {self.name} --args-json '{{}}' to see the schema",
            ) from exc


class ToolRegistry:
    """The tools a run may call, their generated schemas, and the one place a call is traced.

    Attributes:
        tools: Name to tool, in registration order.
    """

    def __init__(self, tools: Iterable[Tool[Any]] = ()) -> None:
        """Build a registry over some tools.

        Args:
            tools: The tools to register, in the order they should be listed.
        """
        self.tools: dict[str, Tool[Any]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: Tool[Any]) -> None:
        """Add one tool and generate its JSON schema once.

        Args:
            tool: The tool to add.

        Raises:
            ToolError: A tool of that name is already registered, or the tool does not declare a
                name, a description and an ``Args`` model.
        """
        name = getattr(tool, "name", "")
        if not name or not getattr(tool, "description", ""):
            raise ToolError(
                f"{type(tool).__qualname__} does not declare both a name and a description; spec "
                "3.7 requires each, because the planner is shown them"
            )
        if name in self.tools:
            raise ToolError(f"a tool named {name!r} is already registered")
        self.tools[name] = tool
        self._schemas[name] = tool.Args.model_json_schema()

    def names(self) -> list[str]:
        """Return every registered tool's name, in registration order."""
        return list(self.tools)

    def __contains__(self, name: object) -> bool:
        """Whether a tool of this name is registered."""
        return name in self.tools

    def __len__(self) -> int:
        """How many tools are registered."""
        return len(self.tools)

    def __iter__(self) -> Iterator[Tool[Any]]:
        """Yield the tools in registration order."""
        return iter(self.tools.values())

    def get(self, name: str) -> Tool[Any]:
        """Return one tool.

        Args:
            name: Its name.

        Returns:
            The tool.

        Raises:
            ToolError: No tool of that name is registered; the message lists the ones that are, so
                that a planner's mistake is diagnosable from the trace alone.
        """
        tool = self.tools.get(name)
        if tool is None:
            raise ToolError(
                f"there is no tool named {name!r}; the registered tools are {self.names()}"
            )
        return tool

    def schema(self, name: str) -> dict[str, Any]:
        """Return one tool's JSON schema, generated at registration and not regenerated.

        Args:
            name: The tool's name.

        Returns:
            The JSON schema of its ``Args`` model.

        Raises:
            ToolError: No tool of that name is registered.
        """
        self.get(name)
        return self._schemas[name]

    def schemas(self) -> dict[str, dict[str, Any]]:
        """Return every tool's JSON schema, keyed by tool name."""
        return dict(self._schemas)

    def catalogue(self) -> list[dict[str, Any]]:
        """Return the name, description and schema of every tool, as the planner is shown them.

        Returns:
            One entry per tool, in registration order.
        """
        return [
            {
                "tool": name,
                "description": tool.description,
                "schema": self._schemas[name],
            }
            for name, tool in self.tools.items()
        ]

    def call(
        self,
        name: str,
        args: Mapping[str, Any] | ToolArgs | None,
        ctx: ToolContext,
    ) -> ToolResult:
        """Validate, run and trace one tool call.

        Args:
            name: The tool to call.
            args: Its arguments, as a mapping from the planner or an already-built ``Args``.
            ctx: The run's context.

        Returns:
            The tool's result.

        Raises:
            ToolError: The tool is unknown, the arguments do not validate, or the check cannot run.
                A failure after the arguments validate is still traced, with ``ok: false``, so a
                run that died inside a tool leaves a record of which one.
        """
        tool = self.get(name)
        parsed = tool.parse(args)
        args_hash = stable_hash({"tool": name, "args": parsed.model_dump(mode="json")})
        started = time.monotonic()
        try:
            result = tool.run(parsed, ctx)
        except ToolError as exc:
            self._emit(ctx, name, args_hash, time.monotonic() - started, None, error=exc.message)
            raise
        self._emit(ctx, name, args_hash, time.monotonic() - started, result)
        return result

    @staticmethod
    def _emit(
        ctx: ToolContext,
        name: str,
        args_hash: str,
        duration: float,
        result: ToolResult | None,
        error: str | None = None,
    ) -> None:
        """Write the one ``tool_call`` event for a call, successful or not.

        A failed call carries the tool's own message on ``error``, as ``plan_step`` has carried it
        for a loop-requested call since D-088. Before this the event said ``ok: false`` and nothing
        else, so a trace could say which check died and not why -- and once a dead check no longer
        ends the run (D-177), the trace is the only place the reason is written in full.
        """
        if ctx.trace is None:
            return
        ctx.trace.emit(
            EventType.tool_call,
            tool=name,
            args_hash=args_hash,
            duration_s=duration,
            artifacts=[artifact.hash for artifact in result.artifacts] if result else [],
            candidates=result.classes if result else [],
            ok=result is not None,
            **({"error": error} if error else {}),
        )
