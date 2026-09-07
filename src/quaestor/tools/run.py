"""``run_model``: the tool that wraps the sandbox, and the ``R0`` candidate when a run goes wrong.

Spec section 3.7's first row. The work is :func:`quaestor.sandbox.run_model`; what this module
adds is the tool contract around it and the one judgement the sandbox deliberately does not make.
The sandbox raises when a subject fails, because a caller that asked for a run and did not get one
must not carry on as though it had. A *validation* of that subject, though, does carry on: "the
model does not run" is the finding, not the end of the report. So this tool catches the
:class:`~quaestor.errors.SandboxError`, checks that the subject really did execute -- the store
holds ``run.status`` only when the subprocess ran -- and returns an ``R0`` candidate evidenced by
the captured output instead of re-raising.

The sandbox is called without a trace writer on purpose: the registry emits exactly one
``tool_call`` event per call, and a second event from inside would double every count the study
makes.
"""

from __future__ import annotations

from pathlib import Path

from ..artifacts import Artifact
from ..errors import SandboxError, ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from ..sandbox import run_model as sandbox_run_model
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["RunModelTool"]

_RUN_ARTIFACTS = ("run.stdout", "run.stderr", "run.duration_s", "run.status")
"""What the sandbox stores before it raises, and therefore what an ``R0`` can cite."""

MAX_SECONDS_NAME = "threshold.package.max_seconds"
"""Where the package's own wall-clock cap is stored, so an ``R0`` can cite the rule it broke.

In the ``threshold.package.*`` family, but without the ``.<split>.<min|max>`` tail the metric
thresholds carry: ``runtime.max_seconds`` is a ceiling by its own name, is stated on no split, and
naming it ``threshold.package.max_seconds.max`` would put the word twice.
"""


class RunModelTool(Tool["RunModelTool.Args"]):
    """Run the subject in the sandbox and store the standard artifact contract of spec 3.3."""

    name = "run_model"
    description = (
        "Run the package's subject in a capped subprocess and store what it wrote: stdout, "
        "stderr, duration and every file of the spec 3.3 contract under run.<file>."
    )

    class Args(ToolArgs):
        """Arguments of ``run_model``.

        Attributes:
            synthetic: How many rows to ask the subject to generate, for an offline run. Exactly
                one of this and ``data_dir`` is given.
            data_dir: Where the subject's real data is, for a ``--data`` run.
            seed: Passed to the subject as ``--seed``; ``None`` leaves the subject's own default,
                which is the seed ``package.yaml`` documents.
        """

        synthetic: int | None = None
        data_dir: str | None = None
        seed: int | None = None

    def run(self, args: RunModelTool.Args, ctx: ToolContext) -> ToolResult:
        """Run the subject, or raise an ``R0`` candidate describing why it could not be run.

        Args:
            args: Which data mode to run in, and with which seed.
            ctx: The run's context. The subject writes into ``ctx.out_dir`` and its artifacts go
                into ``ctx.store``.

        Returns:
            The artifacts the run produced and, when the run failed or breached its declared
            wall-clock cap, one ``R0`` candidate.

        Raises:
            ToolError: The arguments name neither or both data modes, or the package has no code
                to run -- failures of the request rather than of the subject, which are not
                findings about the model.
        """
        if (args.data_dir is None) == (args.synthetic is None):
            raise ToolError(
                f"run_model on package {ctx.package.name!r} needs exactly one of --synthetic and "
                "--data",
                fix="quaestor tool run_model --pkg <package> --args-json '{\"synthetic\": 5000}'",
            )
        cap = ctx.store.put(
            MAX_SECONDS_NAME,
            float(ctx.package.spec.runtime.max_seconds),
            "scalar",
            "the wall-clock cap package.yaml declares for the subject",
        )
        try:
            result = sandbox_run_model(
                ctx.package,
                Path(args.data_dir) if args.data_dir is not None else None,
                ctx.out_dir,
                synthetic=args.synthetic,
                seed=args.seed,
                store=ctx.store,
            )
        except SandboxError as exc:
            return self._failed(exc, ctx, cap)

        artifacts = [cap, *result.artifacts]
        candidates: list[FindingCandidate] = []
        if result.duration_s > ctx.package.spec.runtime.max_seconds:
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.R0,
                    evidence=[ctx.store.artifact("run.duration_s").hash, cap.hash],
                    detail=(
                        f"the subject of package {ctx.package.name!r} took "
                        f"{result.duration_s:.1f} s against the {result.max_seconds} s cap "
                        "package.yaml declares"
                    ),
                    suggested_severity=Severity.medium,
                    tool=self.name,
                )
            )
        unexpected = (
            f"; {len(result.unexpected_output)} unexpected output file(s): "
            f"{result.unexpected_output}"
            if result.unexpected_output
            else ""
        )
        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"{ctx.package.name} ran in {result.duration_s:.2f} s ({result.data_mode} mode, "
                f"memory cap {result.memory_cap.value}), writing {len(result.files)} contract "
                f"files{unexpected}"
            ),
        )

    def _failed(self, exc: SandboxError, ctx: ToolContext, cap: Artifact) -> ToolResult:
        """Turn a sandbox failure into an ``R0`` candidate, or re-raise if nothing ran.

        The store is what tells the two apart. The sandbox writes ``run.stdout``, ``run.stderr``,
        ``run.duration_s`` and ``run.status`` before it raises anything about how the subprocess
        ended, so their presence means the subject ran and failed -- which is a finding about the
        model. Their absence means the run never started: a package with no ``code/``, a
        contradictory pair of arguments. That is a failure of the request, and a validation report
        must not record it as a defect of the subject.
        """
        evidence = [ctx.store.artifact(name).hash for name in _RUN_ARTIFACTS if name in ctx.store]
        if not evidence:
            raise ToolError(
                f"run_model could not start the subject of package {ctx.package.name!r}: "
                f"{exc.message}",
                fix=exc.fix,
            ) from exc
        artifacts = [
            cap,
            *(ctx.store.artifact(name) for name in _RUN_ARTIFACTS if name in ctx.store),
        ]
        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=[
                FindingCandidate(
                    defect_class=DefectClass.R0,
                    evidence=[*evidence, cap.hash],
                    detail=(
                        f"the subject of package {ctx.package.name!r} did not complete a run: "
                        f"{exc.message}"
                    ),
                    suggested_severity=Severity.high,
                    tool=self.name,
                )
            ],
            summary=f"the subject failed: {exc.message}",
        )
