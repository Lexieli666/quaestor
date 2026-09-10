"""`draft_section`: one case per section that drafts, with three metamorphic relations.

Spec section 6's first bullet. The system under test is `Drafter.draft` with Probatio's provider
passed straight in as its `llm`; the case supplies the section, the artifacts, the candidates and
the guidance, all built from one offline run of the synthetic credit subject by `casebuilder.py`.

The three relations say what a drafting call must not depend on:

- `@order_invariant(field="input.artifacts_json", k=3)` -- the section follows from the *set* of
  artifacts it was given, not from which one the selector happened to list first.
- `@format_jitter(field="input.guidance")` -- reformatting the retrieved guidance, without changing
  a word of it, must not change the verdict.
- `@distractor_robust` -- one artifact from the other subject, appended. A drafter that cites a
  mortgage-servicing projection in a credit report has followed the retriever rather than the
  question.

A relation's violation rate is reported beside the case and never changes its verdict, which is
why the same four assertions carry both.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import probatiosupport
import pytest
from casebuilder import DISTRACTOR
from probatio.case import LLMCase, load_cases
from probatio.metamorphic import distractor_robust, format_jitter, order_invariant

CASES = load_cases(Path(__file__).parent / "cases" / "draft_section.yaml")
"""The seven cases, one per section of `docs/REPORT_SCHEMA.md` that the drafter writes."""


@order_invariant(field="input.artifacts_json", k=3)
@format_jitter(field="input.guidance")
@distractor_robust(field="input.artifacts_json", distractors=[DISTRACTOR], positions=["end"])
@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_draft_section(probatio: Any, provider: Any, case: LLMCase) -> None:
    """Draft one section and hold the answer to the case's four assertions."""
    probatio.check(case, lambda one: probatiosupport.draft_answer(one, provider))
