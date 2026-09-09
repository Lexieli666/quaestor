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

Three families of name appear in the store:

* ``threshold.<CLASS>.<name>`` -- a class default from the table below, such as
  ``threshold.M1.vif``;
* ``threshold.package.<metric>[.<split>].<min|max>`` -- a rule the developer declared in
  ``package.yaml``, such as ``threshold.package.auc.test.min``;
* ``<declared>.<rule>_effective`` -- the bound a rule *applied*, where the rule derives it from
  the data rather than reading it off the table, such as
  ``threshold.L2.overlap.features_effective``. :func:`effective_name` is the one spelling of it,
  and a rule that computes a bound stores it, because a report that compares a value with an
  unstored number is a report whose comparison nothing can check (DECISIONS D-091).

``rule.calibration_first_event_rate`` is neither: it is not a pass/fail bound but the event rate
below which the report puts calibration before discrimination (spec section 3.11), and it is
carried here because it is the same kind of thing -- a number a check applies that a reader is
entitled to cite. ``threshold.O1.slice_auc_gap`` and ``threshold.O1.slice_min_share`` are two more
of that kind: they raise no candidate and decide only where a sub-population's result is reported,
and they are here because a sentence that says a slice is materially worse has to be able to cite
the number that decided it (DECISIONS D-102).
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Final

from ..artifacts import Artifact, ArtifactKind, ArtifactStore
from ..errors import ToolError
from ..package import ThresholdSpec

__all__ = [
    "DEFAULT_THRESHOLDS",
    "EFFECTIVE_SUFFIX",
    "SLICE_GAP_BOUND",
    "SLICE_SHARE_FLOOR",
    "THRESHOLD_SUMMARIES",
    "Thresholds",
    "effective_name",
    "package_threshold_names",
]

SLICE_GAP_BOUND: Final = "threshold.O1.slice_auc_gap"
"""How far a sub-population's AUC may fall below its split's before the result is an open item.

The one spelling of the name, read by the tool that stores the bound
(:mod:`quaestor.tools.metrics`) and by the section plan that applies it
(:mod:`quaestor.report.sections`), so that the number the rule uses and the number the prose cites
cannot come apart (DECISIONS D-102).
"""

SLICE_SHARE_FLOOR: Final = "threshold.O1.slice_min_share"
"""The share of a split a sub-population must hold before its gap can raise an open item (D-102).

A slice of thirty rows can differ from its split's AUC by anything at all, and asking a developer
to answer for it is asking them to explain sampling noise.
"""

EFFECTIVE_SUFFIX: Final = "_effective"
"""The tail a derived bound's logical name carries, so a reader can see it was computed.

``threshold.L2.overlap`` is the number ``package.yaml`` and spec section 3.7 state;
``threshold.L2.overlap.features_effective`` is the number the feature-overlap rule actually
applied, which under D-086 is ``max(threshold.L2.overlap, 2 x leakage.duplicates.train)`` and is
therefore a property of the data as well as of the rule.
"""


def effective_name(base: str, rule: str) -> str:
    """Return the logical name a rule's computed bound is stored under.

    Args:
        base: The declared threshold's logical name, such as ``threshold.L2.overlap``.
        rule: Which arm of the rule the bound belongs to, such as ``features``.

    Returns:
        ``<base>.<rule>_effective``.
    """
    return f"{base}.{rule}{EFFECTIVE_SUFFIX}"


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
    "threshold.O1.slice_auc_gap": 0.08,
    "threshold.O1.slice_min_share": 0.10,
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
    "threshold.M1.condition_number": "M1: Belsley's condition number of the design",
    "threshold.M1.vif": "M1: the variance inflation factor of any retained feature",
    "threshold.O1.auc_gap": "O1: the train-to-test AUC gap",
    "threshold.O1.holdout_gap": "O1: how far a period split's AUC may fall below test",
    "threshold.O1.slice_auc_gap": (
        "how far a sub-population's AUC may fall below the split's before the result is an open "
        "item; it raises no candidate"
    ),
    "threshold.O1.slice_min_share": (
        "the share of a split a sub-population must hold before it can raise an open item"
    ),
    "threshold.R1.auc_gap": "R1: the AUC difference across regimes",
    "threshold.R1.sign_flip_coef": "R1: the coefficient a sign flip must exceed in both regimes",
    "threshold.S1.psi": "S1: the population stability index, train against test",
    "rule.calibration_first_event_rate": (
        "the event rate below which the report puts calibration before discrimination"
    ),
}
"""The caption each threshold is stored with, so Appendix B says what a number governs.

No caption names a ``DECISIONS.md`` entry. A summary is shown to the drafter and printed in
Appendix B, so a ``(D-050)`` in one is a reference to this project's own decision log inside a
document addressed to a model developer, who cannot look it up -- and the third live run copied
one into its prose, where the ``50`` was counted as a claim of fifty (DECISIONS D-116). The
reference belongs in this module's docstrings, which carry it. ``tests/test_pipeline.py``
asserts that no artifact either synthetic run stores carries one.
"""


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
