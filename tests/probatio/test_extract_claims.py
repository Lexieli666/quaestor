"""`extract_claims`: the live report's section 2, extracted five times, tolerated at 0.8.

Spec section 6's second bullet. The input is section 2 of `eval/results/first-live/credit/`
verbatim, prose only, with renderer blocks removed exactly as `extract()` removes them; the system
under test is `extract`, and the answer asserted on is the model's own list of claims, before the
deterministic pre-pass touches it.

`@flaky_tolerant(p=0.8, n=5)` is spec section 6's `--runs 5`, declared on the test rather than
passed on the command line so that it applies to this case alone: `n` overrides `--runs` for the
marked test, and a global `--runs 5` would multiply the seven drafting cases and their variants by
five as well. The floor is 0.8 rather than 1.0 because the extractor's unit labels are known to
vary between runs -- the count-against-ratio disagreement of D-111 -- and a `unit` that moves does
not change the values this case asserts on but does change the answer's bytes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import probatiosupport
import pytest
from probatio.case import LLMCase, load_cases
from probatio.stability import flaky_tolerant

CASES = load_cases(Path(__file__).parent / "cases" / "extract_claims.yaml")
"""The one case: section 2 of the committed live credit report."""


@flaky_tolerant(p=0.8, n=5)
@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_extract_claims(probatio: Any, provider: Any, case: LLMCase) -> None:
    """Extract one section's claims five times and require four of the five to pass."""
    probatio.check(case, lambda one: probatiosupport.extract_answer(one, provider))
