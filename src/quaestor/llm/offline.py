"""``OfflineLLM``: the deterministic provider behind ``--llm fake``.

``CLAUDE.md``'s command list ends with a line that has to work on a laptop with no network, no API
key and no subscription::

    quaestor validate subjects/credit_default --synthetic --llm fake --out /tmp/r

That line is the project's quick start, its demo and gate condition 5b, so the provider it names
ships inside the package rather than beside the tests. It is a fake and says so -- its
:attr:`name` is ``fake`` and every report it writes records ``fake`` as the model -- but it is not
a stub: it answers each of the four prompts the pipeline sends the way a competent model would, so
that the report a reader sees offline has the shape, the citations and the grounding precision a
real one has (DECISIONS D-080).

* **draft** -- reads the artifact JSON out of the prompt and writes one cited sentence per scalar,
  one per JSON path, and a ``[[table:...]]`` directive per table, opening with the first guidance
  span it was given. It writes only numbers the JSON carries, which is the rule the prompt states,
  so a report it drafts verifies.
* **extract** -- reads the numbered prose back out of the prompt and returns every numeric token
  outside a citation, an inline-code span or a finding id, with the citation that follows it and
  the line number the prompt printed beside it (D-085).
* **plan** -- stops at once, so the bounded loop adds nothing.
* **plain_llm** -- writes the seven headings with one cited sentence each and no findings.

Nothing here reads the clock or a random number: the same prompt gets the same answer in every
process, which is what lets a test compare two whole rendered reports byte for byte.

The three hooks -- :meth:`OfflineLLM.scalar_sentence`, :meth:`OfflineLLM.plan_action` and
:meth:`OfflineLLM.plain_findings` -- exist so that ``tests/reportsupport.py`` can subclass this
into a drafter that forgets a citation or writes the wrong number, which is how the repair loop is
exercised. The defects stay in the test tree; only the competent behaviour ships.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any, Final

from .fake import FakeLLM

__all__ = [
    "FOLLOW_UPS_HEADING",
    "OPEN_ITEMS_HEADING",
    "OfflineLLM",
    "citation_of",
    "masked_line",
    "prompt_kind",
    "written",
]

_CITATION_RE: Final = re.compile(r"\[\[[^\]]*\]\]")
_CODE_RE: Final = re.compile(r"`[^`\n]*`")
_FINDING_ID_RE: Final = re.compile(r"\bF-\d{3}\b")
_TOKEN_RE: Final = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?%?")


def written(value: float) -> str:
    """Write a number the way report prose writes it: positional, no trailing zeros.

    Args:
        value: The number.

    Returns:
        Its decimal form, with no exponent and no trailing zeros, so that the sentence and the
        artifact agree at the precision the sentence chose (D-069).
    """
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.12f}".rstrip("0")
    return text if not text.endswith(".") else f"{text}0"


def masked_line(line: str) -> str:
    """Blank out every citation, inline-code span and finding id, keeping every offset.

    Three of the six classes the pre-pass excludes (D-015). A competent extractor does not claim
    the ``-100`` inside ``scenario.value_change.-100``, and one that did would have the claim
    dropped for a number the pre-pass had already excluded (D-077).

    Args:
        line: One line of prose.

    Returns:
        The line, the same length, with those three regions replaced by spaces.
    """
    masked = line
    for pattern in (_CITATION_RE, _CODE_RE, _FINDING_ID_RE):
        masked = pattern.sub(lambda match: " " * len(match.group(0)), masked)
    return masked


def citation_of(line: str, end: int) -> str | None:
    """Return the citation that follows a token, or ``None`` when nothing follows it.

    Args:
        line: The line the token is on.
        end: The offset just past the token.

    Returns:
        The ``[[art:...]]`` token immediately after it, or ``None``.
    """
    rest = line[end:].lstrip()
    if not rest.startswith("[[art:"):
        return None
    close = rest.find("]]")
    return rest[: close + 2] if close >= 0 else None


def prompt_kind(prompt: str) -> str:
    """Say which of the pipeline's four prompts this is, by the sentence each one opens with.

    Args:
        prompt: The prompt as sent.

    Returns:
        ``draft``, ``extract``, ``plan``, ``plain`` or ``unknown``.
    """
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
        prompt, "Guidance spans retrieved for this section:\n", "\n\nFindings raised"
    ).strip()
    if not block or block.startswith("("):
        return []
    parsed = json.loads(block)
    return list(parsed) if isinstance(parsed, list) else []


def _finding_headings(prompt: str) -> list[str]:
    """Return the finding headings a section-6 prompt asked to be copied."""
    return [line.strip() for line in prompt.splitlines() if line.strip().startswith("### F-")]


OPEN_ITEMS_HEADING: Final = "### Open items"
"""Section 6's open-items heading, as ``quaestor.report.schema`` fixes it.

Spelled out here rather than imported: this module is the offline *provider*, and a provider that
imported the report layer would invert the dependency the drafter already declares in the other
direction. Everything this fake knows about a prompt it knows by reading the prompt's text, and
this is one more marker in that list.
"""

FOLLOW_UPS_HEADING: Final = "### Follow-up analyses"
"""The heading a section carries when the bounded loop ran a step on its material (D-101).

Spelled out here for the reason :data:`OPEN_ITEMS_HEADING` is.
"""

_FOLLOW_UP_ARTIFACTS_PREFIX: Final = "artifacts: "
"""How the drafting prompt's follow-up block introduces the names one step produced."""


def _follow_up_artifacts(prompt: str) -> list[str]:
    """Return the logical names the prompt's follow-up block says the loop's steps produced.

    Args:
        prompt: The prompt as sent.

    Returns:
        The names, in prompt order, deduplicated. Empty when the prompt carries no follow-up
        block, which is every section the bounded loop asked nothing about.
    """
    names: list[str] = []
    for line in prompt.splitlines():
        stripped = line.strip()
        if not stripped.startswith(_FOLLOW_UP_ARTIFACTS_PREFIX):
            continue
        for name in stripped[len(_FOLLOW_UP_ARTIFACTS_PREFIX) :].split(","):
            if name.strip() and name.strip() not in names:
                names.append(name.strip())
    return names


def _wants_follow_ups(prompt: str) -> bool:
    """Whether this prompt asks for the follow-up subsection (D-101).

    Args:
        prompt: The prompt as sent.

    Returns:
        ``True`` when the follow-up block named the heading, which section 6's block does not.
    """
    return FOLLOW_UPS_HEADING in prompt


def _wants_open_items(prompt: str) -> bool:
    """Whether this is the section-6 prompt, which asks for the open-items subsection (D-096).

    Args:
        prompt: The prompt as sent.

    Returns:
        ``True`` when the brief named the heading, which only section 6's does.
    """
    return OPEN_ITEMS_HEADING in prompt


class OfflineLLM(FakeLLM):
    """A ``FakeLLM`` that answers the drafter, the extractor, the planner and the baseline.

    Attributes:
        name: ``"fake"``, which is what a report's front matter records as its model.
        max_scalars: How many scalar artifacts a section writes about. Six keeps an offline demo
            report readable; the cap is on the fake's verbosity, never on what may be cited.
        seen: The kind of every prompt answered, in order, so a caller can see what ran.
    """

    name: str = "fake"

    def __init__(self, *, max_scalars: int = 6, **kwargs: Any) -> None:
        """Configure how much this fake writes per section.

        Args:
            max_scalars: How many scalar artifacts a drafted section writes a sentence about.
            **kwargs: Passed to :class:`~quaestor.llm.fake.FakeLLM`; the response table it builds
                is consulted only for prompts this class does not recognise.
        """
        super().__init__(**kwargs)
        self.max_scalars = max_scalars
        self.seen: list[str] = []

    # --- the hooks a defective subclass overrides -------------------------------------------

    def scalar_sentence(self, item: Mapping[str, Any], *, repair: bool) -> str:
        """Write one sentence about one scalar artifact, cited.

        Args:
            item: The artifact as the drafting prompt describes it: its logical name, its value
                at four significant figures, its eight-character hash and its citation.
            repair: Whether this draft is a repair round. Unused here -- a competent drafter has
                nothing to repair -- and the reason the hook takes the argument at all.

        Returns:
            The sentence, with the citation the prompt supplied copied after the number.
        """
        del repair
        return (
            f"The value of `{item['name']}` is {written(float(item['value']))} {item['citation']}."
        )

    def choose_scalars(self, items: Sequence[Mapping[str, Any]]) -> Sequence[Mapping[str, Any]]:
        """Choose which of a section's scalar artifacts this fake writes a sentence about.

        Args:
            items: Every scalar the section may cite, in logical-name order.

        Returns:
            The first :attr:`max_scalars` of them. It is a hook because a subclass built to
            produce one specific defect -- an uncited ``challenger.brier``, say -- has to be able
            to reach the artifact its defect is about, and a section's scalar list is long enough
            that alphabetical order alone decides whether it can.
        """
        return items[: self.max_scalars]

    def plan_action(self) -> dict[str, Any]:
        """Return the bounded loop's next action.

        Returns:
            ``{"stop": True}``: the rule-based plan already ran every check this package needs,
            and a fake that invented a follow-up would put a tool call in the study's counts that
            no model asked for.
        """
        return {"stop": True}

    def plain_findings(self) -> list[dict[str, Any]]:
        """Return the findings the ``plain_llm`` baseline reports.

        Returns:
            None. The baseline gets the contract files and no checks, and this fake does not
            pretend to have read them.
        """
        return []

    # --- dispatch ---------------------------------------------------------------------------

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
            return json.dumps(self.plan_action()), "fake-plan"
        if kind == "plain":
            return self._plain(prompt), "fake-plain"
        return super()._respond(prompt, system, params)

    # --- the drafter ------------------------------------------------------------------------

    def _draft(self, prompt: str) -> str:
        """Write one section: a guidance opening, the findings asked for, then the artifacts."""
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
        for heading in _finding_headings(prompt):
            lines.append(heading)
            lines.append("**The check that raised this finding is described below.**")
            lines.append("The evidence for it is cited in the sections above.")
        scalars = [item for item in _artifacts(prompt) if item.get("kind") == "scalar"]
        for item in self.choose_scalars(scalars):
            lines.append(self.scalar_sentence(item, repair=repair))
        for item in _artifacts(prompt):
            if item.get("kind") == "json":
                lines.extend(self._json_sentences(item))
            elif item.get("kind") == "table":
                lines.append(str(item["directive"]))
        reported = self._follow_up_lines(prompt)
        if _wants_open_items(prompt):
            lines.append(OPEN_ITEMS_HEADING)
            lines.extend(
                reported
                or [
                    "No observation of this run needs a developer response beyond the findings "
                    "above; the owner of anything that later does is the model developer."
                ]
            )
        if _wants_follow_ups(prompt):
            lines.append(FOLLOW_UPS_HEADING)
            lines.extend(reported or ["The loop's step produced no scalar this section may cite."])
        return json.dumps({"markdown": "\n".join(lines)})

    def _follow_up_lines(self, prompt: str) -> list[str]:
        """Write one cited sentence per scalar the bounded loop's steps produced.

        The names come out of the prompt's own follow-up block and the citations out of its
        artifact list, so this fake reports exactly the steps it was asked about and cites them
        the way the drafter is told to (D-101).
        """
        citable = {
            str(item["name"]): item
            for item in _artifacts(prompt)
            if item.get("kind") == "scalar" and item.get("value") is not None
        }
        return [
            f"The follow-up analysis records `{name}` as "
            f"{written(float(citable[name]['value']))} {citable[name]['citation']}, "
            "which the model developer is asked to account for."
            for name in _follow_up_artifacts(prompt)
            if name in citable
        ]

    @staticmethod
    def _json_sentences(item: Mapping[str, Any]) -> list[str]:
        """Write one cited sentence per path of a JSON artifact, at most three."""
        name = str(item["name"])
        hash8 = str(item["hash8"])
        values = dict(item.get("values") or {})
        return [
            f"The `{name}` path `{path}` is {written(float(value))} [[art:{hash8}:{name}#{path}]]."
            for path, value in list(values.items())[:3]
        ]

    # --- the extractor ----------------------------------------------------------------------

    @staticmethod
    def _extract(prompt: str) -> str:
        """Return every numeric token of the prose, with its line number and its citation.

        The import of :func:`~quaestor.verifier.extract.numbered_lines` is local because
        ``quaestor.verifier`` imports the ``LLM`` protocol out of this package: a module-level
        import here would make the cycle depend on which of the two packages a caller imported
        first, which is a cycle that works until it does not.
        """
        from ..verifier.extract import numbered_lines

        prose = _between(prompt, "Prose:\n", "\n\nAnswer with one JSON object")
        claims: list[dict[str, Any]] = []
        for number, line in sorted(numbered_lines(prose).items()):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            masked = masked_line(line)
            for match in _TOKEN_RE.finditer(masked):
                token = match.group(0)
                claims.append(
                    {
                        "line": number,
                        "value": float(token.replace(",", "").rstrip("%")),
                        "unit": "percent" if token.endswith("%") else "ratio",
                        "citation": citation_of(line, match.end()),
                    }
                )
        return json.dumps({"claims": claims})

    # --- the plain_llm baseline -------------------------------------------------------------

    def _plain(self, prompt: str) -> str:
        """Write the whole report in one answer: seven headings, one cited sentence each."""
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
        return json.dumps({"markdown": "\n".join(lines), "findings": self.plain_findings()})
