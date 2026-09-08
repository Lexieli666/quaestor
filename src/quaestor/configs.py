"""The three configurations of spec section 3.13, as data, and what each tool screens for.

| configuration | plan | narrative | verifier |
|---|---|---|---|
| ``full_agent`` | rules + bounded loop | one model call per section, cited | on, with repair |
| ``rules_only`` | rules | a template over the candidates, no model call | on, trivially verified |
| ``plain_llm`` | ``run_model`` only | one model call over the contract files | on, no repair |

They are here as *data* rather than as three code paths because the study compares them: a
difference between two runs has to be a difference in this table, not a difference in what some
branch happened to do. :mod:`quaestor.pipeline` reads the table and runs one pipeline (D-070).

:data:`SCREENED_CLASSES` is the other half of the file: which defect classes each tool is looking
for, which is what ``findings.json``'s ``checks_without_candidates`` is built from -- a check that
ran and raised nothing is evidence, and the study's miss list needs it as structured data rather
than as prose (D-012). ``run_model`` screens for nothing: ``R0`` is raised when a run *fails*,
which is not a screen, and the golden report's ``checks_without_candidates`` does not list it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from .findings import DefectClass
from .vocab import Configuration

__all__ = [
    "CONFIGURATIONS",
    "SCREENED_CLASSES",
    "SYNTHETIC_DEFAULT_N",
    "ConfigSpec",
    "Narrative",
    "PlanMode",
    "config_for",
    "synthetic_default_n",
]


class PlanMode:
    """How a configuration decides which tools to run.

    Attributes:
        rules_and_loop: The rule-based plan, then the bounded follow-up loop.
        rules: The rule-based plan alone.
        run_only: ``run_model`` and nothing else.
    """

    rules_and_loop: Final = "rules_and_loop"
    rules: Final = "rules"
    run_only: Final = "run_only"


class Narrative:
    """Who writes the report's prose.

    Attributes:
        llm_sections: One model call per section, each with the section's artifacts and rules.
        template: A deterministic template over the same inputs; no model call.
        one_call: One model call for the whole report, over the raw contract files.
    """

    llm_sections: Final = "llm_sections"
    template: Final = "template"
    one_call: Final = "one_call"


@dataclass(frozen=True)
class ConfigSpec:
    """One configuration, as the study compares them.

    Attributes:
        name: Which of the three.
        plan: How the tools are chosen.
        narrative: Who writes the prose.
        repair: Whether the repair loop runs.
        max_follow_ups: How many steps the bounded loop may take; ``0`` when it does not run.
        retrieve_guidance: Whether the plan retrieves guidance per section.
        description: One sentence, for ``--help`` and for the study's own report.
    """

    name: Configuration
    plan: str
    narrative: str
    repair: bool
    max_follow_ups: int
    retrieve_guidance: bool
    description: str

    @property
    def calls_a_model(self) -> bool:
        """Whether this configuration calls a model at all.

        ``rules_only`` does not, and that is asserted rather than assumed: its runs emit zero
        ``llm_call`` trace events, which is what makes it the ``$0`` arm of the study.
        """
        return self.narrative != Narrative.template

    @property
    def uses_tools(self) -> bool:
        """Whether this configuration runs the checks, or only the subject."""
        return self.plan != PlanMode.run_only


CONFIGURATIONS: Final[Mapping[Configuration, ConfigSpec]] = {
    Configuration.full_agent: ConfigSpec(
        name=Configuration.full_agent,
        plan=PlanMode.rules_and_loop,
        narrative=Narrative.llm_sections,
        repair=True,
        max_follow_ups=4,
        retrieve_guidance=True,
        description=(
            "the product: the rule-based plan, a bounded follow-up loop, one drafted section per "
            "model call with citations, and the verifier with its repair loop"
        ),
    ),
    Configuration.rules_only: ConfigSpec(
        name=Configuration.rules_only,
        plan=PlanMode.rules,
        narrative=Narrative.template,
        repair=False,
        max_follow_ups=0,
        retrieve_guidance=True,
        description=(
            "what the deterministic checks catch on their own: the rule-based plan, a template "
            "narrative over the candidates, no model call anywhere, and $0 of cost"
        ),
    ),
    Configuration.plain_llm: ConfigSpec(
        name=Configuration.plain_llm,
        plan=PlanMode.run_only,
        narrative=Narrative.one_call,
        repair=False,
        max_follow_ups=0,
        retrieve_guidance=False,
        description=(
            "the baseline: run the subject, hand one model call its metrics, model summary, "
            "features, splits and raw profile, and verify what it wrote without repairing it"
        ),
    ),
}
"""The three configurations, as spec section 3.13's table."""

SCREENED_CLASSES: Final[Mapping[str, tuple[DefectClass, ...]]] = {
    "profile_data": (DefectClass.D1, DefectClass.S1),
    "compute_metrics": (DefectClass.T1, DefectClass.C1, DefectClass.O1),
    "check_leakage": (DefectClass.L1, DefectClass.L2),
    "check_stability": (DefectClass.R1,),
    "check_collinearity": (DefectClass.M1,),
    "challenger_compare": (DefectClass.E1,),
    "run_scenarios": (DefectClass.X1,),
    "verify_developer_claims": (DefectClass.T1,),
}
"""Which classes each check looks for, so a check that raised nothing can say what it looked for.

``run_model`` and ``retrieve_guidance`` are deliberately absent. ``run_model``'s ``R0`` is raised
by a run that failed rather than by a screen over a model that ran, and ``retrieve_guidance``
raises nothing by construction (spec 3.7): a search result is not evidence that anything is wrong.
"""


def config_for(name: Configuration | str) -> ConfigSpec:
    """Return one configuration's specification.

    Args:
        name: The configuration, or its name.

    Returns:
        Its :class:`ConfigSpec`.
    """
    return CONFIGURATIONS[Configuration(name)]


SYNTHETIC_DEFAULT_N: Final[Mapping[str, int]] = {
    "credit_default": 5000,
    "msr_prepayment": 2000,
}
"""How many rows each shipped subject generates when ``--synthetic`` is given no number.

``CLAUDE.md``'s command list writes ``--synthetic`` bare, and the two subjects document different
sizes: 5,000 rows for ``credit_default`` (spec 4.1) and 2,000 loans for ``msr_prepayment``
(spec 4.2), which is what every measurement in ``PROGRESS.md`` was taken at. The table lives here
rather than in ``cli.py`` because it is a property of the subjects, and a package that declares its
own ``synthetic_default_n`` later replaces the lookup without touching the parser (D-081).
"""


def synthetic_default_n(package: str) -> int | None:
    """Return the documented synthetic size of one subject.

    Args:
        package: The package name, as ``package.yaml`` declares it.

    Returns:
        The row count ``--synthetic`` uses when given no number, or ``None`` for a package this
        table does not know -- for which the caller must ask the human for a number rather than
        invent one, since the size of a generated panel decides every figure computed from it.
    """
    return SYNTHETIC_DEFAULT_N.get(package)
