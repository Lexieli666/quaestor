"""``package.yaml`` as pydantic models: what a model package is allowed to say about itself.

Spec section 3.2 fixes the file. Every model here sets ``extra="forbid"``, which is the point of
the exercise: a package that misspells ``vintage_holdout`` as ``vintage_holdouts`` must fail
loudly, because the alternative is a validation report that silently never looks at the holdout and
says nothing about it. The one field this project added is :attr:`Feature.note` (DECISIONS D-017),
so that a feature's construction can be documented where a reader meets it.

Nothing here reads a file; :mod:`quaestor.package.loader` does that and turns a
:class:`pydantic.ValidationError` into a :class:`~quaestor.errors.PackageError` that names the
field and the file.
"""

from __future__ import annotations

from collections import Counter
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "ConvexityExpectation",
    "DataSpec",
    "DeveloperClaim",
    "Feature",
    "FeatureTiming",
    "ModelType",
    "PackageSpec",
    "RegimeSpec",
    "RuntimeSpec",
    "ScenariosSpec",
    "SplitRule",
    "SplitsSpec",
    "ThresholdSpec",
]


class ModelType(StrEnum):
    """The two model families v0.1 validates.

    Attributes:
        binary_classification: One row per subject, one binary outcome.
        discrete_time_hazard: One row per subject-period, an event hazard per period.
    """

    binary_classification = "binary_classification"
    discrete_time_hazard = "discrete_time_hazard"


class FeatureTiming(StrEnum):
    """When a feature's value becomes known, relative to the outcome it helps predict.

    This is the declaration the leakage screen is built on: a feature whose value is only known
    during or after the outcome window cannot legitimately be an input.

    Attributes:
        at_origination: Known when the account or loan was opened.
        before_period_start: Known before the observation period begins.
        during_period: Observed inside the outcome window; suspicious.
        after_outcome: Observed after the outcome is known; an ``L1`` defect on its face.
    """

    at_origination = "at_origination"
    before_period_start = "before_period_start"
    during_period = "during_period"
    after_outcome = "after_outcome"


class DataSpec(BaseModel):
    """Where the subject's data comes from and what it predicts.

    Attributes:
        source: Free text for a human: the dataset, its licence and how it was sampled.
        manifest: File name to SHA-256, or ``None``. Verified by the loader when a data directory
            is given; a mismatch is a :class:`~quaestor.errors.PackageError`.
        target: The outcome column.
        event_definition: What the target means, in one sentence.
        time_column: The period column for a hazard subject; ``None`` for a classifier.
        id_column: The subject identifier, used for split overlap and row hashing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str
    manifest: dict[str, str] | None = None
    target: str
    event_definition: str
    time_column: str | None = None
    id_column: str


class SplitRule(BaseModel):
    """How one split was drawn, as the developer describes it.

    Attributes:
        rule: The rule in words, including the seed where one applies.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rule: str


class SplitsSpec(BaseModel):
    """The splits a subject writes predictions for.

    Attributes:
        train: The fitting split.
        test: The held-out split every threshold is stated on.
        out_of_time: A later-period split, or ``None``.
        vintage_holdout: A held-out origination vintage, or ``None``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    train: SplitRule
    test: SplitRule
    out_of_time: SplitRule | None = None
    vintage_holdout: SplitRule | None = None

    def names(self) -> list[str]:
        """Return the names of the splits this package actually declares.

        Returns:
            ``["train", "test"]`` plus whichever optional splits are present, in report order.
        """
        declared = ["train", "test"]
        if self.out_of_time is not None:
            declared.append("out_of_time")
        if self.vintage_holdout is not None:
            declared.append("vintage_holdout")
        return declared


class Feature(BaseModel):
    """One model input and the timing declaration the leakage screen reads.

    Attributes:
        name: The column name in ``data_<split>.csv``.
        timing: When the value becomes known.
        note: Optional free text, so that a construction worth explaining -- a near-collinear
            pair, a capped ratio -- is documented where a reader meets the feature (D-017).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    timing: FeatureTiming
    note: str | None = None


class RegimeSpec(BaseModel):
    """The column that splits the data into regimes for the stability check.

    Attributes:
        column: The regime column, or ``None`` when the package declares none, in which case
            ``check_stability`` does not run and Appendix D says so.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    column: str | None = None


class ThresholdSpec(BaseModel):
    """A developer-declared pass/fail rule. A breach is a ``T1`` finding.

    Every value here is stored as an artifact under ``threshold.package.*`` so that the report can
    cite the rule it applied rather than restating it in prose.

    Attributes:
        metric: What the rule governs -- ``auc``, ``brier``, ``psi``, ``calibration_slope``.
        split: The split the rule applies to, or ``None`` for a rule over all features.
        features: ``"all"`` for a rule over every feature, or a feature name; ``None`` otherwise.
        min: The floor, if the rule has one.
        max: The ceiling, if the rule has one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: str
    split: str | None = None
    features: str | None = None
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _bound_required(self) -> ThresholdSpec:
        """Reject a rule with neither a floor nor a ceiling, which can never be breached."""
        if self.min is None and self.max is None:
            raise ValueError(
                f"the threshold on {self.metric!r} declares neither min nor max, so nothing can "
                "breach it; give it a bound or delete it"
            )
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(
                f"the threshold on {self.metric!r} has min {self.min} above max {self.max}"
            )
        return self


class DeveloperClaim(BaseModel):
    """A number the developer declares about the real fit, verified like a report claim.

    Under ``--synthetic`` these are not evaluated and are listed in Appendix D; under ``--data``
    each becomes a ``VerifiedClaim`` with ``source: developer`` (DECISIONS D-016).

    Attributes:
        text: The claim as the developer wrote it.
        metric: What the number measures, or ``None``.
        split: The split it is stated on, or ``None``.
        value: The declared number.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str
    metric: str | None = None
    split: str | None = None
    value: float


class ConvexityExpectation(StrEnum):
    """Which way the developer says the projected value curve bends. Hazard packages only.

    Spec section 3.7's ``X1`` rule fires when the projection's sign pattern is "inconsistent with
    declared convexity expectation", which presupposes a declaration; this is it.

    Attributes:
        negative: Value falls further under the down shock than it rises under the up shock, which
            is what a mortgage-servicing right does: the borrower's prepayment option is worth
            more as rates fall.
        positive: Value rises further under the up shock than it falls under the down shock.
    """

    negative = "negative"
    positive = "positive"


class ScenariosSpec(BaseModel):
    """The rate shocks a hazard subject projects under, and how it values them. Hazard only.

    The last three fields are additions to spec section 3.2's block, decided in Cowork before
    Phase 4 (DECISIONS D-037): spec section 4.2 requires the projection to report "the servicing
    value change per shock from a declared servicing fee", which needs a fee and a discount rate,
    and ``X1`` needs the expectation it compares the realised sign pattern with. All three are
    required rather than defaulted, because a threshold rule that silently supplies its own
    declaration is not a developer declaration.

    Attributes:
        rate_shocks_bp: Parallel shocks in basis points, including ``0`` for the base case.
        horizon_months: How far the projection runs.
        servicing_fee_bp: The annual servicing fee, in basis points on the surviving balance.
        discount_rate_annual: The annual rate the servicing cash flows are discounted at.
        convexity_expectation: Which way the value curve is expected to bend.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate_shocks_bp: list[int] = Field(min_length=1)
    horizon_months: int = Field(gt=0)
    servicing_fee_bp: float = Field(gt=0.0)
    discount_rate_annual: float = Field(gt=0.0)
    convexity_expectation: ConvexityExpectation

    @model_validator(mode="after")
    def _has_a_base_case(self) -> ScenariosSpec:
        """Insist on the unshocked case, which every value change is measured against."""
        if 0 not in self.rate_shocks_bp:
            raise ValueError(
                f"scenarios.rate_shocks_bp is {self.rate_shocks_bp} and does not include 0; the "
                "base case is what every value change is stated relative to"
            )
        return self


class RuntimeSpec(BaseModel):
    """The caps the sandbox enforces on the subject's subprocess.

    Attributes:
        max_seconds: Wall-clock cap; a subject that outruns it is killed and gets an ``R0``.
        max_memory_mb: Address-space cap, enforced with ``setrlimit`` where the platform has it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_seconds: int = Field(gt=0)
    max_memory_mb: int = Field(gt=0)


class PackageSpec(BaseModel):
    """The whole of ``package.yaml``.

    Attributes:
        name: The package name, which is also the directory name by convention.
        version: The model version, as a string. YAML's ``1.0`` is a float and is rejected: a
            version is an identifier, and ``1.10`` must not equal ``1.1``.
        model_type: Which family the subject belongs to.
        entrypoint: The command the sandbox runs, ``python -m code.run`` by convention.
        data: Where the data comes from and what it predicts.
        splits: The splits the subject writes predictions for.
        features: The model inputs and their timings.
        regime: The regime column, if any.
        thresholds: Developer-declared pass/fail rules.
        claims: Developer-declared numbers about the real fit.
        scenarios: Rate shocks, for a hazard subject only.
        runtime: The sandbox caps.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    version: str
    model_type: ModelType
    entrypoint: str
    data: DataSpec
    splits: SplitsSpec
    features: list[Feature] = Field(min_length=1)
    regime: RegimeSpec = RegimeSpec()
    thresholds: list[ThresholdSpec] = Field(default_factory=list)
    claims: list[DeveloperClaim] = Field(default_factory=list)
    scenarios: ScenariosSpec | None = None
    runtime: RuntimeSpec

    @model_validator(mode="before")
    @classmethod
    def _null_blocks_take_their_defaults(cls, data: Any) -> Any:
        """Read an explicit ``regime: null`` or ``claims: null`` as "not declared".

        A hand-written ``package.yaml`` says ``scenarios: null`` for a classifier, and the same
        author will write ``regime: null`` rather than ``regime: {column: null}``. Both mean the
        same thing to a reader, so both mean the same thing here; a required block written as
        ``null`` still fails, and names its own field.
        """
        if not isinstance(data, dict):
            return data
        cleaned = dict(data)
        for key in ("regime", "thresholds", "claims", "features"):
            if key in cleaned and cleaned[key] is None:
                del cleaned[key]
        return cleaned

    @model_validator(mode="after")
    def _coherent(self) -> PackageSpec:
        """Check the cross-field rules the spec states in prose."""
        counts = Counter(feature.name for feature in self.features)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        if duplicates:
            raise ValueError(f"features declares {duplicates} more than once")
        if self.model_type is ModelType.discrete_time_hazard and self.data.time_column is None:
            raise ValueError(
                "a discrete_time_hazard package must declare data.time_column: the panel has one "
                "row per subject-period and nothing else names the period"
            )
        if self.model_type is ModelType.binary_classification and self.scenarios is not None:
            raise ValueError(
                "scenarios apply to a discrete_time_hazard package only; a binary classifier has "
                "no projection to shock"
            )
        if self.data.target in {f.name for f in self.features}:
            raise ValueError(
                f"data.target {self.data.target!r} is also declared as a feature, which is total "
                "leakage rather than a modelling choice"
            )
        return self

    @property
    def feature_names(self) -> list[str]:
        """Return the declared feature names, in declaration order."""
        return [feature.name for feature in self.features]

    def features_with_timing(self, timing: FeatureTiming) -> list[Feature]:
        """Return the features declared with one timing.

        Args:
            timing: The timing to select.

        Returns:
            The matching features, in declaration order.
        """
        return [feature for feature in self.features if feature.timing is timing]
