"""The claim-coverage arithmetic, once, for every caller that checks a report's numbers.

`tests/test_golden_spec.py` check 7 asks one question of the Phase 1 golden: is every numeric
token of the drafted prose covered by a post-repair claim, and does every post-repair claim have a
token in the prose? `tests/test_archive_fixtures.py` asks the same question of every live run
committed under `eval/results/first-live/`, which is what turns a defect found by reading a $6
report into a defect found by `pytest`. The counting is the same both times and lives here, so the
two cannot drift apart the way the three tokenizers of D-084 did.

**What is deliberately not shared is the tokenizer.** The golden test reads the numeric pattern as
a literal of its own and imports nothing from `quaestor`, because it is the executable
specification and a specification that imports the implementation checks nothing (D-099 keeps the
two copies in step by hand, on purpose). This module therefore takes tokens and claims already in
hand and only counts them: stdlib only, no import of `quaestor`, so the golden test can use it
without acquiring a dependency on the package it specifies (DECISIONS D-118).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import NamedTuple

__all__ = ["ClaimKey", "Coverage", "cover", "token_key"]


class ClaimKey(NamedTuple):
    """What makes two numbers the same claim for coverage purposes.

    Attributes:
        value: The number as written, without separators or per cent sign.
        percent: Whether it was written with a per cent sign, which is a different claim: 22% and
            22 are the same digits about two quantities two orders of magnitude apart.
    """

    value: float
    percent: bool


@dataclass(frozen=True)
class Coverage:
    """The two directions of the question, both of which have to come back empty.

    Attributes:
        uncovered: The tokens of the prose that no claim accounts for, in prose order.
        unclaimed: The claims that have no token left in the prose, in claim order.
    """

    uncovered: list[str]
    unclaimed: list[ClaimKey]


def token_key(token: str) -> ClaimKey:
    """Return the claim key of one numeric token as the drafter wrote it.

    Args:
        token: A numeric token, separators and per cent sign included: ``3,500``, ``22.0%``,
            ``1.92e-05``.

    Returns:
        Its value and whether it was written as a per cent.
    """
    return ClaimKey(float(token.replace(",", "").rstrip("%")), token.endswith("%"))


def cover(tokens: Sequence[str], claims: Sequence[ClaimKey]) -> Coverage:
    """Match the prose's numeric tokens against a report's claims, one for one.

    A claim covers one token, not every token of its value: a report that writes 0.7550 twice and
    claims it once has an uncovered number, which is the case the multiset counting exists for.

    Args:
        tokens: The eligible numeric tokens of the drafted prose, in prose order.
        claims: One key per claim of the report, in any order.

    Returns:
        The tokens nothing accounts for and the claims nothing in the prose does.
    """
    remaining = Counter(claims)
    uncovered: list[str] = []
    for token in tokens:
        key = token_key(token)
        if remaining[key] > 0:
            remaining[key] -= 1
        else:
            uncovered.append(token)
    unclaimed: list[ClaimKey] = []
    for key, count in remaining.items():
        unclaimed.extend([key] * count)
    return Coverage(uncovered=uncovered, unclaimed=unclaimed)
