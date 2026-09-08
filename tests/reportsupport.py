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
    "written",
]


class SectionFake(OfflineLLM):
    """The offline fake, with the four ways of being wrong the repair loop has to survive.

    Attributes:
        plan_actions: The bounded loop's answers, in order; the default stops at once.
        plain_findings_list: What the `plain_llm` baseline reports as findings.
        drop_citation_for: Logical names the first draft of a section writes with no citation, so
            that a test can make the repair loop run; a repair draft cites them.
        wrong_value_for: Logical name to the number the drafter writes instead of the artifact's,
            in every draft, so that a test can make two repair rounds fail.
    """

    def __init__(
        self,
        *,
        plan_actions: Sequence[Mapping[str, Any]] | None = None,
        plain_findings: Sequence[Mapping[str, Any]] = (),
        drop_citation_for: Sequence[str] = (),
        wrong_value_for: Mapping[str, float] | None = None,
        max_scalars: int = 6,
        **kwargs: Any,
    ) -> None:
        """Configure what this fake does differently from a competent model."""
        super().__init__(max_scalars=max_scalars, **kwargs)
        self.plan_actions = [dict(action) for action in (plan_actions or [{"stop": True}])]
        self.plain_findings_list = [dict(item) for item in plain_findings]
        self.drop_citation_for = list(drop_citation_for)
        self.wrong_value_for = dict(wrong_value_for or {})

    def scalar_sentence(self, item: Mapping[str, Any], *, repair: bool) -> str:
        """Write the sentence, or the defect this fake was built to write instead."""
        name, value = str(item["name"]), float(item["value"])
        citation = str(item["citation"])
        if name in self.wrong_value_for:
            return f"The value of `{name}` is {written(self.wrong_value_for[name])} {citation}."
        if name in self.drop_citation_for and not repair:
            return f"The value of `{name}` is {written(value)}."
        return super().scalar_sentence(item, repair=repair)

    def plan_action(self) -> dict[str, Any]:
        """Return the next scripted action of the bounded loop, holding the last one."""
        if len(self.plan_actions) == 1:
            return self.plan_actions[0]
        return self.plan_actions.pop(0)

    def plain_findings(self) -> list[dict[str, Any]]:
        """Return the findings the test scripted for the `plain_llm` baseline."""
        return self.plain_findings_list
