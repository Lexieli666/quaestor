"""The effective thresholds: the spec 3.7 defaults, and the package's own declared rules.

Spec section 3.7 states each candidate rule with a number in it -- a VIF of 10, an overlap of
0.5%, a challenger gap of 0.03 -- and section 12 rejects "thresholds hard-coded in prose rather
than stored as artifacts". Both halves are implemented here: every number a rule uses is a keyed
entry whose key *is* its logical artifact name, and :meth:`Thresholds.artifact` is the only way a
tool reads one, so a threshold that decided a candidate is in the store by construction and its
hash is in that candidate's evidence.

Spec section 3.7 says the defaults live in ``configs.py``, which arrives with the three
configurations in Phase 8. They live here instead and ``configs.py`` will import them: a tool
module that imported ``configs`` would make the tool layer depend on the pipeline layer, and the
values are needed by Phase 5's tools three phases before there is a configuration to hold them
(DECISIONS D-049).

Two families of name appear in the store:

* ``threshold.<CLASS>.<name>`` -- a class default from the table below, such as
  ``threshold.M1.vif``;
* ``threshold.package.<metric>[.<split>].<min|max>`` -- a rule the developer declared in
  ``package.yaml``, such as ``threshold.package.auc.test.min``.

``rule.calibration_first_event_rate`` is neither: it is not a pass/fail bound but the event rate
below which the report puts calibration before discrimination (spec section 3.11), and it is
carried here because it is the same kind of thing -- a number a check applies that a reader is
entitled to cite.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Final

from ..artifacts import Artifact, ArtifactKind, ArtifactStore
from ..errors import ToolError
from ..package import ThresholdSpec

__all__ = [
    "DEFAULT_THRESHOLDS",
    "THRESHOLD_SUMMARIES",
    "Thresholds",
    "package_threshold_names",
]

DEFAULT_THRESHOLDS: Final[Mapping[str, float]] = {
    "threshold.C1.calibration_slope.max": 1.20,
    "threshold.C1.calibration_slope.min": 0.80,
    "threshold.C1.mean_ratio_rel": 0.25,
    "threshold.D1.missing_gap": 0.10,
    "threshold.E1.delta_auc": 0.03,
    "threshold.L1.single_feature_auc": 0.90,
    "threshold.L2.overlap": 0.005,
    "threshold.M1.condition_number": 30.0,
    "threshold.M1.vif": 10.0,
    "threshold.O1.auc_gap": 0.08,
    "threshold.O1.holdout_gap": 0.05,
    "threshold.R1.auc_gap": 0.10,
    "threshold.R1.sign_flip_coef": 0.05,
    "threshold.S1.psi": 0.25,
    "rule.calibration_first_event_rate": 0.05,
}
"""Every number spec section 3.7 states, keyed by the logical name it is stored under."""

THRESHOLD_SUMMARIES: Final[Mapping[str, str]] = {
    "threshold.C1.calibration_slope.max": "C1: the top of the calibration slope band",
    "threshold.C1.calibration_slope.min": "C1: the bottom of the calibration slope band",
    "threshold.C1.mean_ratio_rel": "C1: mean predicted against observed, relative",
    "threshold.D1.missing_gap": "D1: the missingness gap between splits, as a fraction",
    "threshold.E1.delta_auc": "E1: the challenger's AUC lead over the champion",
    "threshold.L1.single_feature_auc": "L1: the AUC one feature may reach on its own",
    "threshold.L2.overlap": "L2: the fraction of test rows that may also be in train",
    "threshold.M1.condition_number": "M1: Belsley's condition number of the design (D-035)",
    "threshold.M1.vif": "M1: the variance inflation factor of any retained feature",
    "threshold.O1.auc_gap": "O1: the train-to-test AUC gap (D-050)",
    "threshold.O1.holdout_gap": "O1: how far a period split's AUC may fall below test",
    "threshold.R1.auc_gap": "R1: the AUC difference across regimes",
    "threshold.R1.sign_flip_coef": "R1: the coefficient a sign flip must exceed in both regimes",
    "threshold.S1.psi": "S1: the population stability index, train against test (D-046)",
    "rule.calibration_first_event_rate": (
        "the event rate below which the report puts calibration before discrimination"
    ),
}
"""The caption each threshold is stored with, so Appendix B says what a number governs."""


class Thresholds:
    """The numbers the candidate rules apply, with the spec 3.7 defaults and any overrides.

    A threshold is read through :meth:`artifact`, which stores it and returns the artifact, or
    through ``[]`` when only the value is wanted. Both reject an unknown key, so a rule cannot
    apply a threshold that nothing in the store explains.

    Attributes:
        values: The effective thresholds, keyed by logical artifact name.
    """

    def __init__(self, overrides: Mapping[str, float] | None = None) -> None:
        """Build the effective thresholds from the defaults and an optional override map.

        Args:
            overrides: Values replacing the defaults, keyed by the same logical names. A key that
                is not a default is rejected, because a threshold nothing reads is a threshold
                whose author believes a rule is looser than it is.

        Raises:
            ToolError: An override names a threshold that does not exist.
        """
        merged = dict(DEFAULT_THRESHOLDS)
        for key, value in (overrides or {}).items():
            if key not in DEFAULT_THRESHOLDS:
                raise ToolError(
                    f"{key!r} is not a threshold quaestor applies; the thresholds are "
                    f"{sorted(DEFAULT_THRESHOLDS)}"
                )
            merged[key] = float(value)
        self.values: dict[str, float] = merged

    def __getitem__(self, key: str) -> float:
        """Return one threshold's value.

        Args:
            key: Its logical artifact name, such as ``threshold.M1.vif``.

        Returns:
            The effective value.

        Raises:
            ToolError: The key is not a threshold.
        """
        if key not in self.values:
            raise ToolError(
                f"{key!r} is not a threshold quaestor applies; the thresholds are "
                f"{sorted(DEFAULT_THRESHOLDS)}"
            )
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        """Yield every threshold's logical name, sorted."""
        return iter(sorted(self.values))

    def __len__(self) -> int:
        """How many thresholds there are."""
        return len(self.values)

    def artifact(self, store: ArtifactStore, key: str) -> Artifact:
        """Store one threshold and return its artifact, so a candidate can cite the rule it used.

        Args:
            store: Where the artifact goes.
            key: The threshold's logical name.

        Returns:
            The stored artifact.

        Raises:
            ToolError: The key is not a threshold.
        """
        return store.put(key, self[key], ArtifactKind.scalar, THRESHOLD_SUMMARIES[key])


def package_threshold_names(rule: ThresholdSpec) -> dict[str, float]:
    """Return the logical names and values of one developer-declared rule's bounds.

    Args:
        rule: One entry of ``package.yaml``'s ``thresholds`` block.

    Returns:
        ``threshold.package.<metric>[.<split>].<min|max>`` to the declared value, one entry per
        bound the rule states. A rule over every feature declares no split and so gets the shorter
        name, which is what the golden report cites as ``threshold.package.psi.max``.
    """
    stem = f"threshold.package.{rule.metric}"
    if rule.split is not None:
        stem = f"{stem}.{rule.split}"
    bounds: dict[str, float] = {}
    if rule.min is not None:
        bounds[f"{stem}.min"] = float(rule.min)
    if rule.max is not None:
        bounds[f"{stem}.max"] = float(rule.max)
    return bounds
