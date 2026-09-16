"""What `subjects/*/artifacts/real/` is allowed to contain: aggregates, and nothing per loan.

Both subjects commit the JSON a real-sample run wrote -- metrics, coefficients, split digests,
features, and for the hazard subject the rate-shock projection -- and neither commits a row.
`CLAUDE.md` forbids a per-loan value anywhere in the tree, and the Freddie Mac terms forbid one
here specifically (`subjects/msr_prepayment/README.md`, "Data source and licence"). Those are
prose rules until something checks them, so this module checks the two properties that a per-loan
value would have to break:

* **no identifying key.** No `loan_id`, no `loan_sequence_number`, no bare `id` anywhere in the
  document. `loan_age` is a feature name and not an identifier, which is why the rule matches
  whole key names rather than the substring `loan`.
* **no list long enough to be a row per loan.** The longest legitimate array in either subject is
  `projection.json`'s `balance_by_month`, which is `scenarios.horizon_months` aggregates per
  shock, and `model_summary.json`'s `baseline_hazard`, which is shorter. The bound is read from
  each package rather than written here twice, so a subject that changes its horizon moves its own
  bound and a subject that starts writing rows does not.

`splits.json`'s `rows_hash` stays: it is a digest of the *set* of dense `loan_id:period` pairs,
where the identifier is an integer `sample_freddie.py` assigned, so it names a split without
naming a loan (the subject README says so at length).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from quaestor.package import load_package

REPO_ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = REPO_ROOT / "subjects"

SUBJECT_NAMES = ("credit_default", "msr_prepayment")

IDENTIFIER_KEY = re.compile(
    r"^(ids?|(loan|client|account|borrower)ids?"
    r"|(loan)?seq(uence)?(num(ber)?)?|(loan)?sequencenumber)$"
)
"""Whole key names that would mean a document is keyed by something other than an aggregate.

Matched against the key with its separators removed and folded to lower case, so `loan_id`,
`loanId` and `LOAN_ID` are one rule. It matches whole names and not the substring `loan`, because
`loan_age` is a feature and `n_loans` is a count.
"""


def _normalised(key: object) -> str:
    """A key with separators dropped and case folded, which is what the rule matches."""
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _real_artifacts(subject: str) -> list[Path]:
    """Every committed JSON of a subject's real-sample run, in name order."""
    return sorted((SUBJECTS / subject / "artifacts" / "real").glob("*.json"))


def _max_list_length(subject: str) -> int:
    """The longest array the subject's own declaration can justify.

    `scenarios.horizon_months` where the package declares scenarios -- the projection writes one
    balance per month per shock -- and otherwise the number of declared features, which bounds
    `features.json` and the coefficient list. Neither is a number this file chooses.
    """
    spec = load_package(SUBJECTS / subject).spec
    horizon = 0 if spec.scenarios is None else int(spec.scenarios.horizon_months)
    return max(len(spec.features), horizon)


def _walk(node: Any, path: str = "") -> list[tuple[str, Any]]:
    """Every (path, node) pair in a JSON document, the root included."""
    found = [(path or "/", node)]
    if isinstance(node, dict):
        for key, value in node.items():
            found.extend(_walk(value, f"{path}/{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(_walk(value, f"{path}[{index}]"))
    return found


@pytest.mark.parametrize("subject", SUBJECT_NAMES)
def test_the_real_artifacts_exist_and_are_json(subject: str) -> None:
    files = _real_artifacts(subject)
    assert files, f"{subject} commits no real-sample aggregates"
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("subject", SUBJECT_NAMES)
def test_no_committed_real_artifact_carries_an_identifying_key(subject: str) -> None:
    for path in _real_artifacts(subject):
        document = json.loads(path.read_text(encoding="utf-8"))
        for where, node in _walk(document):
            if not isinstance(node, dict):
                continue
            offending = [key for key in node if IDENTIFIER_KEY.match(_normalised(key))]
            assert not offending, f"{path.name} carries {offending} at {where}"


@pytest.mark.parametrize("subject", SUBJECT_NAMES)
def test_no_committed_real_artifact_carries_a_per_loan_list(subject: str) -> None:
    bound = _max_list_length(subject)
    for path in _real_artifacts(subject):
        document = json.loads(path.read_text(encoding="utf-8"))
        for where, node in _walk(document):
            if isinstance(node, list):
                assert len(node) <= bound, (
                    f"{path.name} holds a list of {len(node)} at {where}, above the "
                    f"{bound} this subject's package.yaml can justify"
                )


def test_the_hazard_subject_s_bound_is_its_declared_horizon() -> None:
    assert _max_list_length("msr_prepayment") == 180
    assert _max_list_length("credit_default") == 12
