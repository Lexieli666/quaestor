"""Phase 9: `OfflineLLM` on its own — the provider `--llm fake` builds.

The pipeline tests drive this class through the whole of `validate()`, which is the real
assertion: a report drafted by it verifies at grounding precision 1.0 on both subjects. What is
left to test here is what those runs never reach — the answers it gives when a prompt carries none
of what it is looking for, and the three hooks `tests/reportsupport.py` overrides to build a
drafter that breaks the rules.

Nothing here calls a live model; nothing here is a live model.
"""

from __future__ import annotations

import json

from quaestor.llm import OfflineLLM
from quaestor.llm.offline import citation_of, masked_line, prompt_kind, written


def draft(prompt: str) -> str:
    """Return the markdown `OfflineLLM` drafts for one drafting prompt."""
    answer = json.loads(OfflineLLM().complete(prompt).text)
    markdown: str = answer["markdown"]
    return markdown


def test_a_prompt_it_does_not_recognise_falls_through_to_the_fake_it_is_built_on() -> None:
    llm = OfflineLLM(responses={"a question": "an answer"})
    assert llm.complete("a question").text == "an answer"
    assert llm.seen == ["unknown"]
    assert prompt_kind("a question") == "unknown"


def test_a_section_with_no_guidance_and_no_artifacts_says_where_it_came_from() -> None:
    # The prompt carries neither the guidance block nor the artifact block, which is what a
    # section drafted from an empty store looks like. The fake writes no number, so there is
    # nothing for the verifier to fail on.
    markdown = draft("You are drafting one section of a validation report.")
    assert markdown == "This section is written from the artifacts of this run."


def test_a_section_writes_one_cited_sentence_per_scalar_and_a_directive_per_table() -> None:
    prompt = (
        "You are drafting one section of a validation report.\n"
        "Artifacts you may cite (values at four significant figures):\n"
        + json.dumps(
            [
                {
                    "kind": "scalar",
                    "name": "metrics.test.auc",
                    "value": 0.7412,
                    "hash8": "a1b2c3d4",
                    "citation": "[[art:a1b2c3d4:metrics.test.auc]]",
                },
                {
                    "kind": "json",
                    "name": "run.features",
                    "hash8": "b2c3d4e5",
                    "values": {"n": 12},
                },
                {"kind": "table", "name": "deciles.test", "directive": "[[table:deciles.test]]"},
            ]
        )
        + "\n\nGuidance spans retrieved for this section:\n"
        + json.dumps([{"citation": "[[reg:SR26-2:V.1.b]]"}])
        + "\n\nFinding candidates for this section: none\n"
    )
    markdown = draft(prompt)
    assert markdown.splitlines() == [
        "This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].",
        "The value of `metrics.test.auc` is 0.7412 [[art:a1b2c3d4:metrics.test.auc]].",
        "The `run.features` path `n` is 12 [[art:b2c3d4e5:run.features#n]].",
        "[[table:deciles.test]]",
    ]


def test_a_section_six_prompt_writes_the_heading_it_was_given() -> None:
    prompt = (
        "You are drafting one section of a validation report.\n"
        "### F-001 · E1 challenger outperforms · severity **low**\n"
    )
    markdown = draft(prompt)
    assert "### F-001 · E1 challenger outperforms · severity **low**" in markdown


def test_the_extractor_returns_every_token_outside_an_exclusion() -> None:
    prompt = (
        "You are extracting the numeric claims of one section.\n"
        "Prose:\n"
        "## 4. Outcomes\n"
        "The value of `metrics.test.auc` is 0.7412 [[art:a1b2c3d4:metrics.test.auc]].\n"
        "\n"
        "Answer with one JSON object"
    )
    claims = json.loads(OfflineLLM().complete(prompt).text)["claims"]
    assert [claim["value"] for claim in claims] == [0.7412]
    assert claims[0]["citation"] == "[[art:a1b2c3d4:metrics.test.auc]]"
    assert claims[0]["unit"] == "ratio"


def test_the_bounded_loop_is_told_to_stop_and_the_baseline_reports_no_finding() -> None:
    # Both are hooks a defective subclass overrides; the shipped fake invents neither a follow-up
    # tool call nor a finding it did not read.
    llm = OfflineLLM()
    assert llm.plan_action() == {"stop": True}
    assert llm.plain_findings() == []
    assert json.loads(llm.complete("You are the planning half of the agent.").text) == {
        "stop": True
    }


def test_a_number_is_written_the_way_report_prose_writes_it() -> None:
    assert written(3500.0) == "3500"
    assert written(0.7412) == "0.7412"
    assert written(-0.04155) == "-0.04155"
    assert written(1.0) == "1"


def test_the_three_regions_a_competent_extractor_does_not_claim_are_masked() -> None:
    line = "The `bill_mean_6m` of F-001 is 0.5 [[art:a1b2c3d4:scenario.value_change.-300]]."
    masked = masked_line(line)
    assert len(masked) == len(line)
    assert "0.5" in masked
    assert "6m" not in masked and "F-001" not in masked and "-300" not in masked


def test_a_number_with_nothing_after_it_carries_no_citation() -> None:
    assert citation_of("the value is 0.5", len("the value is 0.5")) is None
    line = "the value is 0.5 [[art:a1b2c3d4:metrics.test.auc]]"
    assert citation_of(line, len("the value is 0.5")) == "[[art:a1b2c3d4:metrics.test.auc]]"
