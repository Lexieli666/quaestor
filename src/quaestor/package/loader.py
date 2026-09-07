"""``load_package``: read a model package from disk, or say exactly what is wrong with it.

Three things happen here that do not happen in :mod:`quaestor.package.spec`. The YAML is read and
its parse errors are attributed to the file. A :class:`pydantic.ValidationError` is turned into a
:class:`~quaestor.errors.PackageError` naming the field path and the file, because ``features.3.
timing`` and ``package.yaml`` together are the whole of what a user needs to fix it. And the
package's declared data manifest is verified against real files when a data directory is given.

``SEED.yaml`` is not read here, and no code path in :mod:`quaestor` reads it. It is where the
seeded-defect generator of spec section 5 records which defect it injected; the pipeline that is
being measured must not be able to see the answer key. A test plants a poison value in one and
asserts that nothing loaded mentions it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from ..errors import PackageError
from ..findings import PRE_RUN_TOOL, DefectClass, FindingCandidate, Severity
from ..hashing import sha256_file
from .spec import FeatureTiming, PackageSpec

__all__ = ["MANIFEST_FIX", "PACKAGE_FILE", "ModelPackage", "load_package"]

PACKAGE_FILE = "package.yaml"
"""The one file a package directory must contain."""

MANIFEST_FIX = "recompute the digest with `shasum -a 256 <file>` and update data.manifest"
"""What to do about a manifest mismatch, quoted on the error."""


class ModelPackage(BaseModel):
    """A loaded package: its parsed ``package.yaml`` and where on disk it came from.

    Attributes:
        root: The package directory.
        spec: The parsed and validated ``package.yaml``.
        data_dir: The data directory the manifest was verified against, or ``None`` when no
            manifest was verified (synthetic mode, or a package that declares none).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    root: Path
    spec: PackageSpec
    data_dir: Path | None = None

    @property
    def name(self) -> str:
        """The package name, as declared."""
        return self.spec.name

    @property
    def code_dir(self) -> Path:
        """The subject's code directory, which the sandbox copies before running it."""
        return self.root / "code"

    @property
    def docs_dir(self) -> Path | None:
        """The optional developer documentation directory, or ``None`` when there is none."""
        docs = self.root / "docs"
        return docs if docs.is_dir() else None

    def pre_run_candidates(self) -> list[FindingCandidate]:
        """Return the finding candidates visible in ``package.yaml`` before anything runs.

        One rule today, from spec section 3.2: a feature declared ``timing: after_outcome`` is an
        ``L1`` defect on its face -- it is an input the model could not have had when it scored.
        The candidate carries no evidence because no tool has run; ``check_leakage`` attaches the
        ``leakage.timing`` artifact when it promotes it (see :class:`FindingCandidate`).

        Returns:
            One candidate per offending feature, in declaration order; usually empty.
        """
        offenders = self.spec.features_with_timing(FeatureTiming.after_outcome)
        return [
            FindingCandidate(
                defect_class=DefectClass.L1,
                evidence=[],
                detail=(
                    f"feature {feature.name!r} of package {self.spec.name!r} is declared "
                    f"timing: after_outcome, so its value is not known when the model scores"
                ),
                suggested_severity=Severity.high,
                tool=PRE_RUN_TOOL,
            )
            for feature in offenders
        ]


def load_package(path: Path | str, *, data_dir: Path | str | None = None) -> ModelPackage:
    """Load and validate a model package.

    Args:
        path: The package directory, or the ``package.yaml`` inside it.
        data_dir: Where the data files named by ``data.manifest`` live. When given and the package
            declares a manifest, every digest in it is verified. When ``None`` -- which is what
            ``--synthetic`` passes -- the manifest is not verified, and the report says so in
            Appendix D (DECISIONS D-022).

    Returns:
        The loaded package.

    Raises:
        PackageError: The directory or file is missing, the YAML does not parse, a field fails
            validation, the ``code/`` directory is absent, or a manifest digest does not match.
            Every message names the file, and a validation failure also names the field.
    """
    package_path = _package_file(Path(path))
    spec = _parse(package_path)
    code_dir = package_path.parent / "code"
    if not code_dir.is_dir():
        raise PackageError(
            f"package {spec.name!r} at {package_path} has no code/ directory, so there is no "
            f"subject to run ({spec.entrypoint!r} would have nothing to import)",
            fix=f"mkdir {code_dir}",
        )
    verified_against = _verify_manifest(spec, package_path, data_dir)
    return ModelPackage(root=package_path.parent, spec=spec, data_dir=verified_against)


def _package_file(path: Path) -> Path:
    """Resolve a package directory or file to the ``package.yaml`` inside it."""
    if path.is_dir():
        candidate = path / PACKAGE_FILE
        if not candidate.is_file():
            raise PackageError(
                f"{path} is not a model package: it has no {PACKAGE_FILE}",
                fix=f"write {candidate}; see 02-SPEC.md section 3.2",
            )
        return candidate
    if path.is_file():
        return path
    raise PackageError(f"there is no model package at {path}")


def _parse(package_path: Path) -> PackageSpec:
    """Read one ``package.yaml`` and validate it, naming the file and the field on failure."""
    try:
        raw: Any = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PackageError(f"{package_path} is not valid YAML: {exc}") from exc
    if raw is None:
        raise PackageError(f"{package_path} is empty")
    if not isinstance(raw, dict):
        raise PackageError(
            f"{package_path} is a {type(raw).__name__}, not a mapping of package fields"
        )
    try:
        return PackageSpec.model_validate(raw)
    except ValidationError as exc:
        raise PackageError(
            f"{package_path} is not a valid package: {_render(exc)}",
            fix="see 02-SPEC.md section 3.2 for the field list",
        ) from exc


def _render(exc: ValidationError) -> str:
    """Render a pydantic error as ``field.path: message``, one problem per line."""
    lines = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "<root>"
        lines.append(f"{location}: {error['msg']}")
    return "; ".join(lines)


def _verify_manifest(
    spec: PackageSpec, package_path: Path, data_dir: Path | str | None
) -> Path | None:
    """Verify every digest in ``data.manifest``, or return ``None`` when there is nothing to do."""
    if spec.data.manifest is None or data_dir is None:
        return None
    root = Path(data_dir)
    if not root.is_dir():
        raise PackageError(
            f"package {spec.name!r} declares a data manifest but {root} is not a directory"
        )
    for filename, declared in sorted(spec.data.manifest.items()):
        target = root / filename
        if not target.is_file():
            raise PackageError(
                f"{package_path} declares a manifest digest for {filename!r}, which is not in "
                f"{root}",
                fix=f"rebuild the sample, or remove {filename!r} from data.manifest",
            )
        actual = sha256_file(target)
        if actual != declared:
            raise PackageError(
                f"{target} does not match the digest {package_path} declares for {filename!r}: "
                f"expected {declared}, found {actual}",
                fix=MANIFEST_FIX,
            )
    return root
