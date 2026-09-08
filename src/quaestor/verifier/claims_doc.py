"""``claims.json``: the envelope, and the two claim lists that make the pre-repair figure real.

``docs/REPORT_SCHEMA.md`` section 7. The file holds the tolerances that were applied, both
grounding figures, the repairs, every claim as first extracted and matched, every claim after the
last repair round, the developer claims, and the exclusion list. ``eval/score.py`` reads
``grounding`` and never the prose, which is why the figures are stored rather than recomputed from
a rendered table.

Both claim lists are kept for one reason: the pre-repair precision has to be **recomputable**
rather than remembered (D-012). A file that stored only the post-repair claims and a pre-repair
number would let the two disagree, and the number a reader would trust is the one that cannot be
checked. Phase 8 fills ``repairs``; Phase 7 writes the envelope with an empty list, which is
exactly what a ``rules_only`` run produces anyway.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..vocab import Configuration, ReportSection
from .claim import DEFAULT_TOLERANCES, ClaimStatus, Tolerances, VerifiedClaim
from .extract import Exclusion
from .grounding import GroundingFigure, grounding

__all__ = [
    "SCHEMA_VERSION",
    "ClaimsDocument",
    "Repair",
    "RepairSide",
]

SCHEMA_VERSION: Final = 1
"""Stamped on ``claims.json``, as on every file Quaestor persists."""


class RepairSide(BaseModel):
    """A claim's value and status on one side of a repair.

    Attributes:
        value: The number the prose carried.
        status: The verdict it had.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    value: float
    status: ClaimStatus


class Repair(BaseModel):
    """One claim changed by one repair round.

    Attributes:
        section: The section that was re-drafted.
        claim_id: The claim that changed.
        before: Its value and status before the round.
        after: Its value and status after it.
        instruction: The sentence the drafter was given, verbatim.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    section: ReportSection
    claim_id: str
    before: RepairSide
    after: RepairSide
    instruction: str = Field(min_length=1)


class ClaimsDocument(BaseModel):
    """``claims.json`` exactly as ``examples/golden_report/CLAIMS_SCHEMA.json`` describes it.

    Attributes:
        schema_version: Always :data:`SCHEMA_VERSION`.
        package: The package name.
        version: The package version.
        configuration: Which of the three configurations ran.
        run_id: Joins this file to ``trace.jsonl`` and to the report's front matter.
        illustrative: ``true`` only in ``examples/golden_report/``.
        tolerances: The defaults the matcher applied.
        grounding: The two figures, pre- and post-repair.
        repairs: One entry per claim changed by a repair round; Phase 8 fills it.
        pre_repair: Every claim as first extracted and matched.
        post_repair: Every claim after the last repair round; Appendix A renders this list.
        developer_claims: ``package.yaml`` ``claims:``, evaluated only under ``--data``.
        developer_claims_note: Why that list is empty or not evaluated; Appendix D prints it.
        exclusions: The classes of numeric token the pre-pass deliberately ignored.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = SCHEMA_VERSION
    package: str
    version: str
    configuration: Configuration
    run_id: str
    illustrative: bool = False
    tolerances: Tolerances = DEFAULT_TOLERANCES
    grounding: dict[str, GroundingFigure]
    repairs: list[Repair] = Field(default_factory=list)
    pre_repair: list[VerifiedClaim] = Field(default_factory=list)
    post_repair: list[VerifiedClaim] = Field(default_factory=list)
    developer_claims: list[VerifiedClaim] = Field(default_factory=list)
    developer_claims_note: str | None = None
    exclusions: list[Exclusion] = Field(default_factory=list)

    @classmethod
    def build(
        cls,
        *,
        package: str,
        version: str,
        configuration: Configuration,
        run_id: str,
        pre_repair: Sequence[VerifiedClaim],
        post_repair: Sequence[VerifiedClaim] | None = None,
        repairs: Iterable[Repair] = (),
        developer_claims: Sequence[VerifiedClaim] = (),
        developer_claims_note: str | None = None,
        exclusions: Iterable[Exclusion] = (),
        tolerances: Tolerances = DEFAULT_TOLERANCES,
        illustrative: bool = False,
    ) -> ClaimsDocument:
        """Compute both grounding figures from the two claim lists and build the document.

        Args:
            package: The package name.
            version: The package version.
            configuration: Which configuration ran.
            run_id: The run identifier.
            pre_repair: Every claim as first extracted and matched.
            post_repair: Every claim after the last repair round; defaults to ``pre_repair``,
                which is what a run with no repair loop produces.
            repairs: The repair records.
            developer_claims: The ``package.yaml`` claims, verified or not evaluated.
            developer_claims_note: Why the list is empty or not evaluated.
            exclusions: The merged exclusion list of every section.
            tolerances: The tolerances the matcher applied.
            illustrative: ``true`` only for the golden report.

        Returns:
            The document, ready to write.
        """
        after = list(post_repair if post_repair is not None else pre_repair)
        return cls(
            package=package,
            version=version,
            configuration=configuration,
            run_id=run_id,
            illustrative=illustrative,
            tolerances=tolerances,
            grounding={
                "pre_repair": grounding(pre_repair),
                "post_repair": grounding(after),
            },
            repairs=list(repairs),
            pre_repair=list(pre_repair),
            post_repair=after,
            developer_claims=list(developer_claims),
            developer_claims_note=developer_claims_note,
            exclusions=list(exclusions),
        )

    @property
    def precision_pre(self) -> float:
        """Grounding precision before repair, as the front matter prints it."""
        return self.grounding["pre_repair"].precision

    @property
    def precision_post(self) -> float:
        """Grounding precision after the last repair round."""
        return self.grounding["post_repair"].precision

    @property
    def n_claims(self) -> int:
        """The post-repair denominator, which the front matter prints as ``n_claims``."""
        return self.grounding["post_repair"].n_claims

    def to_payload(self) -> dict[str, Any]:
        """Return the document as the JSON object ``CLAIMS_SCHEMA.json`` validates.

        ``developer_claims_note`` is omitted when there is none: the schema makes it optional and
        a ``null`` there would be a third spelling of "no note".

        Returns:
            A plain dict.
        """
        payload = self.model_dump(mode="json")
        if self.developer_claims_note is None:
            payload.pop("developer_claims_note", None)
        return payload

    def write(self, path: Path | str) -> Path:
        """Write ``claims.json``.

        Args:
            path: The file to write; parent directories are created.

        Returns:
            The path written.
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_payload(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
        return target

    @classmethod
    def read(cls, path: Path | str) -> ClaimsDocument:
        """Read a ``claims.json`` back.

        Args:
            path: The file to read.

        Returns:
            The document.
        """
        return cls.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
