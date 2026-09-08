"""Phase 8: the three configurations as data, and the class list each check screens for.

Spec 3.13's table is the whole of what separates the study's three arms, so it is asserted here
field by field rather than left to the pipeline's branches. `SCREENED_CLASSES` is the other half:
`findings.json`'s `checks_without_candidates` is built from it, and a tool name that drifts from
the registry would silently empty that list.
"""

from __future__ import annotations

import pytest

from quaestor.configs import (
    CONFIGURATIONS,
    SCREENED_CLASSES,
    Narrative,
    PlanMode,
    config_for,
)
from quaestor.findings import DefectClass
from quaestor.tools import default_registry
from quaestor.verifier.developer import DEVELOPER_TOOL
from quaestor.vocab import Configuration


def test_there_are_exactly_three_configurations_and_they_are_the_vocabulary_s() -> None:
    assert set(CONFIGURATIONS) == set(Configuration)
    assert [spec.name for spec in CONFIGURATIONS.values()] == list(Configuration)


def test_full_agent_is_the_product() -> None:
    spec = config_for("full_agent")
    assert spec.plan == PlanMode.rules_and_loop
    assert spec.narrative == Narrative.llm_sections
    assert spec.repair is True
    assert spec.max_follow_ups == 4
    assert spec.retrieve_guidance is True
    assert spec.calls_a_model and spec.uses_tools


def test_rules_only_is_the_arm_that_calls_no_model() -> None:
    spec = config_for(Configuration.rules_only)
    assert spec.plan == PlanMode.rules
    assert spec.narrative == Narrative.template
    assert spec.repair is False
    assert spec.max_follow_ups == 0
    assert spec.calls_a_model is False
    assert spec.uses_tools is True
    assert "$0" in spec.description


def test_plain_llm_is_the_arm_that_runs_no_check() -> None:
    spec = config_for(Configuration.plain_llm)
    assert spec.plan == PlanMode.run_only
    assert spec.narrative == Narrative.one_call
    assert spec.repair is False
    assert spec.retrieve_guidance is False
    assert spec.calls_a_model is True
    assert spec.uses_tools is False


def test_every_configuration_has_a_description_a_reader_can_tell_apart() -> None:
    descriptions = {spec.description for spec in CONFIGURATIONS.values()}
    assert len(descriptions) == 3
    assert all(len(text) > 40 for text in descriptions)


def test_an_unknown_configuration_is_not_one() -> None:
    with pytest.raises(ValueError, match="vibes"):
        config_for("vibes")


def test_every_screened_class_is_a_real_class_and_every_screen_a_real_tool() -> None:
    registry = default_registry()
    for tool, classes in SCREENED_CLASSES.items():
        assert tool in registry or tool == DEVELOPER_TOOL, tool
        assert classes
        assert all(isinstance(item, DefectClass) for item in classes)


def test_run_model_and_retrieve_guidance_screen_for_nothing() -> None:
    """`R0` is a run that failed, not a screen over a model that ran; a search is not evidence."""
    assert "run_model" not in SCREENED_CLASSES
    assert "retrieve_guidance" not in SCREENED_CLASSES


def test_every_defect_class_but_r0_is_screened_for_by_something() -> None:
    screened = {item for classes in SCREENED_CLASSES.values() for item in classes}
    assert screened == set(DefectClass) - {DefectClass.R0}
