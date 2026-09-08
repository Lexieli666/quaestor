"""One offline fake that answers every prompt the Phase 8 pipeline sends, and nothing else.

`CLAUDE.md` forbids a live model anywhere `pytest` runs, so the drafter, the extractor, the
bounded planning loop and the `plain_llm` baseline all have to be answered by a `FakeLLM`. A fake
that returned the same string to all four would test nothing, so `SectionFake` dispatches on the
prompt and answers each the way a competent model would:

* **draft** — reads the artifact JSON out of the prompt and writes one cited sentence per scalar,
  one cited sentence per JSON path, and a `[[table:...]]` directive per table, opening with the
  first guidance citation it was given. It writes only numbers the JSON carries, which is the rule
  the prompt states, so a report drafted by it verifies.
* **extract** — reads the prose out of the prompt and returns every numeric token outside a
  citation, with the citation that follows it. This is what the offline verifier eval already does
  (`eval/verifier_eval.fake_extractor`); it is repeated here rather than imported because this one
  masks citations before tokenising, which a section full of `[[art:...]]` names needs.
* **plan** — stops, unless the test asked for a scripted follow-up.
* **plain_llm** — writes the seven headings with one cited sentence each and whatever findings the
  test scripted.

Everything is deterministic: the same construction answers the same prompt with the same text in
every process, which is what makes a whole rendered report byte-comparable between runs.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from quaestor.llm import FakeLLM

__all__ = [
    "SectionFake",
    "citation_of",
    "masked_line",
    "prompt_kind",
    "written",
]

_CITATION_RE = re.compile(r"\[\[[^\]]*\]\]")
_CODE_RE = re.compile(r"`[^`\n]*`")
_FINDING_ID_RE = re.compile(r"\bF-\d{3}\b")
_TOKEN_RE = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?%?")


def written(value: float) -> str:
    """Write a number the way report prose writes it: positional, no trailing zeros."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.12f}".rstrip("0")
    return text if not text.endswith(".") else f"{text}0"


def masked_line(line: str) -> str:
    """Blank out every citation, inline-code span and finding id, keeping every offset.

    These are three of the six classes the pre-pass excludes (D-015). A competent extractor does
    not claim the `-100` inside `scenario.value_change.-100`, and one that did would be counted
    against the report for a number the pre-pass had already excluded.
    """
    masked = line
    for pattern in (_CITATION_RE, _CODE_RE, _FINDING_ID_RE):
        masked = pattern.sub(lambda match: " " * len(match.group(0)), masked)
    return masked


def citation_of(line: str, end: int) -> str | None:
    """Return the citation that follows a token, or `None` when nothing follows it."""
    rest = line[end:].lstrip()
    if not rest.startswith("[[art:"):
        return None
    close = rest.find("]]")
    return rest[: close + 2] if close >= 0 else None


def prompt_kind(prompt: str) -> str:
    """Say which of the four prompts this is, by the sentence each one opens with."""
    if "You are extracting the numeric claims" in prompt:
        return "extract"
    if "You are drafting one section" in prompt:
        return "draft"
    if "You are the planning half" in prompt:
        return "plan"
    if "You are writing a model-validation report" in prompt:
        return "plain"
    return "unknown"


def _between(prompt: str, start: str, end: str) -> str:
    """Return the part of a prompt between two markers, or an empty string."""
    if start not in prompt:
        return ""
    tail = prompt.split(start, 1)[1]
    return tail.split(end, 1)[0] if end in tail else tail


def _artifacts(prompt: str) -> list[dict[str, Any]]:
    """Read the artifact JSON out of a drafting prompt."""
    block = _between(
        prompt,
        "Artifacts you may cite (values at four significant figures):\n",
        "\n\nGuidance spans",
    ).strip()
    if not block or block.startswith("[]"):
        return []
    parsed = json.loads(block)
    return list(parsed) if isinstance(parsed, list) else []


def _guidance(prompt: str) -> list[dict[str, Any]]:
    """Read the guidance spans out of a drafting prompt."""
    block = _between(
        prompt, "Guidance spans retrieved for this section:\n", "\n\nFinding candidates"
    ).strip()
    if not block or block.startswith("("):
        return []
    parsed = json.loads(block)
    return list(parsed) if isinstance(parsed, list) else []


def _finding_headings(prompt: str) -> list[str]:
    """Return the finding headings a section-6 prompt asked to be copied."""
    return [line.strip() for line in prompt.splitlines() if line.strip().startswith("### F-")]


class SectionFake(FakeLLM):
    """A `FakeLLM` that answers the drafter, the extractor, the planner and the baseline.

    Attributes:
        name: `"fake"`, which is what a report's front matter records as its model.
        plan_actions: The bounded loop's answers, in order; the default stops at once.
        plain_findings: What the `plain_llm` baseline reports as findings.
        drop_citation_for: Logical names the first draft of a section writes with no citation, so
            that a test can make the repair loop run; a repair draft cites them.
        wrong_value_for: Logical name to the number the drafter writes instead of the artifact's,
            in every draft, so that a test can make two repair rounds fail.
        max_scalars: How many scalar artifacts a section writes about, to keep a test's report
            short enough to read when it fails.
    """

    name: str = "fake"

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
        super().__init__(**kwargs)
        self.plan_actions = [dict(action) for action in (plan_actions or [{"stop": True}])]
        self.plain_findings = [dict(item) for item in plain_findings]
        self.drop_citation_for = list(drop_citation_for)
        self.wrong_value_for = dict(wrong_value_for or {})
        self.max_scalars = max_scalars
        self.seen: list[str] = []

    def _respond(
        self, prompt: str, system: str | None, params: Mapping[str, Any]
    ) -> tuple[str, str]:
        """Dispatch on which of the four prompts this is."""
        kind = prompt_kind(prompt)
        self.seen.append(kind)
        if kind == "extract":
            return self._extract(prompt), "fake-extract"
        if kind == "draft":
            return self._draft(prompt), "fake-draft"
        if kind == "plan":
            return self._plan(), "fake-plan"
        if kind == "plain":
            return self._plain(prompt), "fake-plain"
        return super()._respond(prompt, system, params)

    # --- the drafter -----------------------------------------------------------------------

    def _draft(self, prompt: str) -> str:
        repair = "Your previous draft of this section was checked" in prompt
        spans = _guidance(prompt)
        lines: list[str] = []
        if spans:
            lines.append(
                f"This section follows the model risk management guidance at "
                f"{spans[0]['citation']}."
            )
        else:
            lines.append("This section is written from the artifacts of this run.")
        headings = _finding_headings(prompt)
        for heading in headings:
            lines.append(heading)
            lines.append("**The check that raised this finding is described below.**")
            lines.append("The evidence for it is cited in the sections above.")
        scalars = [item for item in _artifacts(prompt) if item.get("kind") == "scalar"]
        for item in scalars[: self.max_scalars]:
            lines.append(self._scalar_sentence(item, repair=repair))
        for item in _artifacts(prompt):
            if item.get("kind") == "json":
                lines.extend(self._json_sentences(item))
            elif item.get("kind") == "table":
                lines.append(str(item["directive"]))
        return json.dumps({"markdown": "\n".join(lines)})

    def _scalar_sentence(self, item: Mapping[str, Any], *, repair: bool) -> str:
        name, value = str(item["name"]), float(item["value"])
        citation = str(item["citation"])
        if name in self.wrong_value_for:
            return f"The value of `{name}` is {written(self.wrong_value_for[name])} {citation}."
        if name in self.drop_citation_for and not repair:
            return f"The value of `{name}` is {written(value)}."
        return f"The value of `{name}` is {written(value)} {citation}."

    def _json_sentences(self, item: Mapping[str, Any]) -> list[str]:
        name = str(item["name"])
        hash8 = str(item["hash8"])
        values = dict(item.get("values") or {})
        return [
            f"The `{name}` path `{path}` is {written(float(value))} [[art:{hash8}:{name}#{path}]]."
            for path, value in list(values.items())[:3]
        ]

    # --- the extractor ---------------------------------------------------------------------

    def _extract(self, prompt: str) -> str:
        prose = _between(prompt, "Prose:\n", "\n\nAnswer with one JSON object")
        claims: list[dict[str, Any]] = []
        for line in prose.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            masked = masked_line(line)
            for match in _TOKEN_RE.finditer(masked):
                token = match.group(0)
                claims.append(
                    {
                        "text": line.strip(),
                        "value": float(token.replace(",", "").rstrip("%")),
                        "unit": "percent" if token.endswith("%") else "ratio",
                        "citation": citation_of(line, match.end()),
                    }
                )
        return json.dumps({"claims": claims})

    # --- the bounded planning loop ---------------------------------------------------------

    def _plan(self) -> str:
        action = self.plan_actions[0] if len(self.plan_actions) == 1 else self.plan_actions.pop(0)
        return json.dumps(action)

    # --- the plain_llm baseline ------------------------------------------------------------

    def _plain(self, prompt: str) -> str:
        headings = [
            line.strip()
            for line in _between(
                prompt, "in this order:\n", "\n\nThen list the defects"
            ).splitlines()
            if line.strip().startswith("## ")
        ]
        citable = json.loads(_between(prompt, "<path>]]:\n", "\n\nAnswer with one JSON").strip())
        scalars = [item for item in citable if item.get("kind") == "scalar"]
        lines: list[str] = []
        for index, heading in enumerate(headings):
            lines.append(heading)
            if index < len(scalars):
                item = scalars[index]
                lines.append(
                    f"The store holds `{item['name']}`, cited here "
                    f"[[art:{item['hash8']}:{item['name']}]]."
                )
            else:
                lines.append("Nothing further to report in this section.")
        return json.dumps({"markdown": "\n".join(lines), "findings": self.plain_findings})
