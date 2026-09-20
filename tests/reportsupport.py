"""The defective drafters the repair loop is tested with, over the offline fake that ships.

`quaestor.llm.OfflineLLM` answers the drafter, the extractor, the planner and the `plain_llm`
baseline the way a competent model would, and it ships inside the package because `--llm fake` is
`CLAUDE.md`'s own command line (D-080). What does *not* ship is a drafter that breaks the rule the
prompt states, and that is what most of the repair-loop tests need: a section whose first draft
forgets a citation, a number the drafter refuses to correct, a bounded loop that asks for one more
tool call, a baseline that names an artifact which is not in the store.

`SectionFake` is that model. It is `OfflineLLM` with four knobs, each overriding one of the hooks
the offline fake exposes, so the competent behaviour under test is the same code the shipped
command line runs.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from quaestor.llm import OfflineLLM
from quaestor.llm.offline import citation_of, masked_line, prompt_kind, written

__all__ = [
    "SectionFake",
    "citation_of",
    "masked_line",
    "prompt_kind",
    "truncated_hash",
    "written",
]

SHORT_HASH_KEPT = 6
"""How many of a hash8's eight characters `truncated_hash` keeps: the slip that cost a paid cell.

`full_agent/credit__C1__smote_uncalibrated` was rejected on `[[art:1151e4:calibration_slope.train]]`
against a real `1151c8e4`, two characters short (DECISIONS D-192).
"""


def truncated_hash(citation: str, keep: int = SHORT_HASH_KEPT) -> str:
    """Return an `[[art:...]]` citation with its hash prefix cut short of the eight it needs.

    Args:
        citation: A well-formed artifact citation, brackets included.
        keep: How many characters of the hash prefix to keep.

    Returns:
        The same citation with a hash too short to be a citation, which resolves as `dangling` and
        which no rendered report may carry.
    """
    head, hash8, tail = citation.split(":", 2)
    return f"{head}:{hash8[:keep]}:{tail}"


class SectionFake(OfflineLLM):
    """The offline fake, with the four ways of being wrong the repair loop has to survive.

    Attributes:
        plan_actions: The bounded loop's answers, in order; the default stops at once.
        plain_findings_list: What the `plain_llm` baseline reports as findings.
        drop_citation_for: Logical names the first draft of a section writes with no citation, so
            that a test can make the repair loop run; a repair draft cites them.
        wrong_value_for: Logical name to the number the drafter writes instead of the artifact's,
            in every draft, so that a test can make two repair rounds fail.
        truncate_hash_for: Logical names the first draft of a section cites with a hash prefix two
            characters short, the way a real extractor mis-transcribed one out of its own JSON; a
            repair draft cites them whole (DECISIONS D-192).
    """

    def __init__(
        self,
        *,
        plan_actions: Sequence[Mapping[str, Any]] | None = None,
        plain_findings: Sequence[Mapping[str, Any]] = (),
        drop_citation_for: Sequence[str] = (),
        wrong_value_for: Mapping[str, float] | None = None,
        truncate_hash_for: Sequence[str] = (),
        max_scalars: int = 6,
        **kwargs: Any,
    ) -> None:
        """Configure what this fake does differently from a competent model."""
        super().__init__(max_scalars=max_scalars, **kwargs)
        self.plan_actions = [dict(action) for action in (plan_actions or [{"stop": True}])]
        self.plain_findings_list = [dict(item) for item in plain_findings]
        self.drop_citation_for = list(drop_citation_for)
        self.wrong_value_for = dict(wrong_value_for or {})
        self.truncate_hash_for = list(truncate_hash_for)

    def choose_scalars(self, items: Sequence[Mapping[str, Any]]) -> Sequence[Mapping[str, Any]]:
        """Write about the artifacts this fake was built to be wrong about, first.

        A section's scalar list is alphabetical and longer than `max_scalars`, so a fake that took
        the first six would silently never mention `challenger.brier` and the defect it exists to
        produce would not appear in any draft.
        """
        wanted = (
            set(self.drop_citation_for) | set(self.wrong_value_for) | set(self.truncate_hash_for)
        )
        targeted = [item for item in items if str(item["name"]) in wanted]
        rest = [item for item in items if str(item["name"]) not in wanted]
        return targeted + rest[: max(self.max_scalars - len(targeted), 0)]

    def scalar_sentence(self, item: Mapping[str, Any], *, repair: bool) -> str:
        """Write the sentence, or the defect this fake was built to write instead."""
        name, value = str(item["name"]), float(item["value"])
        citation = str(item["citation"])
        if name in self.wrong_value_for:
            return f"The value of `{name}` is {written(self.wrong_value_for[name])} {citation}."
        if name in self.drop_citation_for and not repair:
            return f"The value of `{name}` is {written(value)}."
        if name in self.truncate_hash_for and not repair:
            return f"The value of `{name}` is {written(value)} {truncated_hash(citation)}."
        return super().scalar_sentence(item, repair=repair)

    def plan_action(self) -> dict[str, Any]:
        """Return the next scripted action of the bounded loop, holding the last one."""
        if len(self.plan_actions) == 1:
            return self.plan_actions[0]
        return self.plan_actions.pop(0)

    def plain_findings(self) -> list[dict[str, Any]]:
        """Return the findings the test scripted for the `plain_llm` baseline."""
        return self.plain_findings_list
