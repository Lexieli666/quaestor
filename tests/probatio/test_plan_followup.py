"""`plan_followup`: one step of the bounded loop, parsed, on the plan the checklist leaves behind.

Spec section 6's third bullet. The system under test is one step's action parse -- `loop_prompt`
followed by the `structured()` call that turns the answer into a `FollowUpAction` -- and the answer
asserted on is what the model wrote, so `schema_valid` is a statement about the model rather than
about pydantic.

Two cases, both on the synthetic credit subject after its thirteen rule-based calls:

- `first_step`: the loop's first question, with no history. It may legitimately answer
  `{"stop": true}`, so nothing here requires a tool; what is required is that the answer validates
  and that it does not name a tool the catalogue did not offer.
- `after_refusal`: the same, two steps in, with a history carrying two real failures -- an action
  refused as inapplicable (`check_stability` on a package with no `regime.column`, D-089) and one
  accepted whose tool then raised (a sub-population of `credit_limit`, which is not a column of
  this subject, D-088 and D-107). Both messages are the ones the code actually produces. The
  assertion is that the third step repeats neither.

D-121's own guard -- the refusal of a slice that resolves to the whole split -- has no case here,
and DECISIONS D-142 records why: under D-122 `above_median` is `> median`, so it can never select
more than half a split, and no column of this subject makes any rule reach the 0.95 ceiling. There
is no honest input on this subject that would provoke that refusal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import probatiosupport
import pytest
from probatio.case import LLMCase, load_cases

CASES = load_cases(Path(__file__).parent / "cases" / "plan_followup.yaml")
"""The two cases: the loop's first step, and a step after two recorded mistakes."""


@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_plan_followup(probatio: Any, provider: Any, case: LLMCase) -> None:
    """Take one step of the bounded loop and hold the action to the case's assertions."""
    probatio.check(case, lambda one: probatiosupport.plan_answer(one, provider))
