"""The committed cases are pinned to the store, to the live run, and to the code that built them.

A Probatio case is committed data, and committed data drifts. A drafting case whose artifacts no
longer match the run's store still drafts something; a `contains` needle that is no longer a claim
of the live report still passes as long as the model happens to write the digits. Neither failure
is visible in a green suite, and both would be replayed from a tape for as long as the tape lives.

So this module runs the real pipeline once, offline, and asserts that every committed file is
byte-identical to what `casebuilder.py` produces from that run **now**. A change to a section
brief, to a selector, to `DRAFT_INSTRUCTION`, to `_LOOP_INSTRUCTION`, to a tool's arguments or to a
pydantic model that a `schema_valid` assertion points at therefore fails here with a diff, and
`python tests/probatio/casebuilder.py` is the fix.

Nothing here calls a model, replays a tape or reads a cassette: it is an ordinary offline test that
happens to live beside the Probatio suite, and it runs under `pytest tests/probatio
--cassette=replay` without making a provider call, which is what gate condition 6 measures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import casebuilder
import probatiosupport
import pytest
from probatio.case import load_cases

CASE_FILES = ("draft_section.yaml", "extract_claims.yaml", "plan_followup.yaml")


@pytest.fixture(scope="module")
def probatio_run(tmp_path_factory: pytest.TempPathFactory) -> casebuilder.Capture:
    """One offline run of the synthetic credit subject, shared by every assertion here.

    The fixture lives in this module rather than in a `tests/probatio/conftest.py`, because pytest
    imports every `conftest.py` under the bare name `conftest` when the directory is not a package
    — and `tests/conftest.py` is what six existing modules import `REPO_ROOT` and `load_module`
    from. A second one here would shadow it and break them (DECISIONS D-143).

    Nothing in it calls a model: `OfflineLLM` is what `quaestor validate --llm fake` uses, so this
    makes exactly as many provider calls as gate condition 6 allows, which is none.
    """
    out_dir = Path(tmp_path_factory.mktemp("probatio_inputs")) / "run"
    return casebuilder.capture(out_dir)


@pytest.fixture(scope="module")
def built(probatio_run: casebuilder.Capture) -> dict[Path, str]:
    """Everything `casebuilder` would write from this session's own offline run."""
    return casebuilder.build(probatio_run)


@pytest.mark.parametrize("name", CASE_FILES)
def test_case_file_matches_the_pipeline(built: dict[Path, str], name: str) -> None:
    path = casebuilder.CASES_DIR / name
    assert path.read_text(encoding="utf-8") == built[path], (
        f"{path.relative_to(casebuilder.REPO_ROOT)} no longer matches what the pipeline builds; "
        "re-run `python tests/probatio/casebuilder.py` and review the diff"
    )


@pytest.mark.parametrize("name", ("drafted_section", "extracted_claims", "follow_up_action"))
def test_schema_file_matches_its_model(built: dict[Path, str], name: str) -> None:
    path = casebuilder.SCHEMAS_DIR / f"{name}.json"
    assert path.read_text(encoding="utf-8") == built[path], (
        f"{path.relative_to(casebuilder.REPO_ROOT)} no longer matches the pydantic model it is "
        "generated from; re-run `python tests/probatio/casebuilder.py`"
    )


def test_every_written_path_is_committed() -> None:
    for path in casebuilder.written_paths():
        assert path.is_file(), f"{path} is written by the builder but not committed"


# -- what the cases say about themselves --------------------------------------------------------


def test_seven_drafting_cases_one_per_section() -> None:
    from quaestor.vocab import SECTION_ORDER

    cases = load_cases(casebuilder.CASES_DIR / "draft_section.yaml")
    assert [case.input["section"] for case in cases] == [section.value for section in SECTION_ORDER]
    assert len(cases) == 7


def test_drafting_inputs_rebuild_into_what_the_drafter_is_given(
    probatio_run: casebuilder.Capture,
) -> None:
    """Each case's four input keys rebuild the objects the pipeline handed the drafter."""
    for case in load_cases(casebuilder.CASES_DIR / "draft_section.yaml"):
        from quaestor.vocab import ReportSection

        given = probatio_run.inputs[ReportSection(case.input["section"])]
        assert [brief.to_payload() for brief in probatiosupport.artifact_briefs(case)] == [
            brief.to_payload() for brief in given.artifacts
        ]
        assert probatiosupport.guidance_spans(case) == list(given.spans)
        assert probatiosupport.candidates(case.input["candidates"]) == list(given.candidates)
        assert probatiosupport.findings(case.metadata["findings"]) == list(given.findings)
        assert probatiosupport.section_brief(case).brief == given_brief(probatio_run, case).brief


def given_brief(run: casebuilder.Capture, case: Any) -> Any:
    """The brief `ordered_briefs` produced for the case's section on this run."""
    from quaestor.vocab import ReportSection

    return run.briefs[ReportSection(case.input["section"])]


def test_drafting_prompts_rebuild_byte_for_byte(probatio_run: casebuilder.Capture) -> None:
    """The prompt a case produces is the prompt the pipeline sent, to the byte.

    This is the assertion that makes the tapes worth recording: a cassette is keyed on the prompt,
    so a case that builds a *nearly* identical prompt records a tape for a call the pipeline never
    makes, and the suite would be measuring the harness.
    """
    from quaestor.llm.offline import OfflineLLM
    from quaestor.report.drafter import Drafter

    drafter = Drafter(OfflineLLM(), package="credit_default", version="1.0")
    for case in load_cases(casebuilder.CASES_DIR / "draft_section.yaml"):
        given = probatio_run.inputs[given_brief(probatio_run, case).section]
        from_case = drafter.prompt(
            probatiosupport.section_brief(case),
            artifacts=probatiosupport.artifact_briefs(case),
            spans=probatiosupport.guidance_spans(case),
            candidates=probatiosupport.candidates(case.input["candidates"]),
            findings=probatiosupport.findings(case.metadata["findings"]),
        )
        from_run = drafter.prompt(
            given_brief(probatio_run, case),
            artifacts=given.artifacts,
            spans=given.spans,
            candidates=given.candidates,
            findings=given.findings,
            follow_ups=given.follow_ups,
        )
        assert from_case == from_run, f"{case.id} no longer rebuilds the pipeline's own prompt"
        assert case.metadata["prompt_bytes"] == len(from_run.encode("utf-8"))


def test_planning_prompts_rebuild_byte_for_byte(probatio_run: casebuilder.Capture) -> None:
    """The `first_step` case rebuilds the prompt the loop's first step was sent."""
    from quaestor.agent.planner import MAX_FOLLOW_UP_STEPS, loop_prompt

    loop = probatio_run.loop
    from_run = loop_prompt(
        probatio_run.registry,
        probatio_run.package,
        remaining=MAX_FOLLOW_UP_STEPS,
        candidates=loop["candidates"],
        completed=loop["completed"],
        artifact_names=loop["artifact_names"],
        data_columns=loop["data_columns"],
        history=(),
    )
    cases = {case.id: case for case in load_cases(casebuilder.CASES_DIR / "plan_followup.yaml")}
    assert probatiosupport.loop_prompt_for(cases["plan_followup.first_step"]) == from_run
    for case in cases.values():
        built = probatiosupport.loop_prompt_for(case)
        assert case.metadata["prompt_bytes"] == len(built.encode("utf-8"))


def test_the_refused_history_carries_the_messages_the_code_produces(
    probatio_run: casebuilder.Capture,
) -> None:
    """The two failures in the `after_refusal` history are the real sentences, not paraphrases."""
    cases = {case.id: case for case in load_cases(casebuilder.CASES_DIR / "plan_followup.yaml")}
    history = cases["plan_followup.after_refusal"].input["history"]
    assert history[0]["reason"] == casebuilder._refusal_reason(probatio_run, "check_stability", {})
    assert history[1]["error"] == casebuilder._tool_error(
        probatio_run, "compute_metrics", history[1]["args"]
    )
    assert history[0]["accepted"] is False
    assert history[1]["accepted"] is True and history[1]["executed"] is False


def test_no_case_names_a_tool_the_registry_offers_for_this_package() -> None:
    """The `not_contains` list holds only tools this package's catalogue does not carry."""
    from quaestor.agent.planner import inapplicable_reason
    from quaestor.tools import default_registry

    registry = default_registry()
    offered = {
        str(entry["tool"])
        for entry in registry.catalogue()
        if not inapplicable_reason(str(entry["tool"]), probatiosupport._package())
    }
    for case in load_cases(casebuilder.CASES_DIR / "plan_followup.yaml"):
        banned = {
            needle
            for assertion in case.assertions
            if assertion.type == "not_contains"
            for needle in assertion.all_
        }
        assert not (banned & offered), f"{case.id} forbids a tool it is allowed to ask for"
    assert set(casebuilder.UNOFFERED_TOOLS) < {str(entry["tool"]) for entry in registry.catalogue()}
    assert not set(casebuilder.INVENTED_TOOLS) & {
        str(entry["tool"]) for entry in registry.catalogue()
    }


# -- the extraction case, pinned to the live run ------------------------------------------------


def test_extraction_prose_is_the_live_report_section_two() -> None:
    """The case's prose is section 2 of the committed live run, stripped as the pipeline strips."""
    (case,) = load_cases(casebuilder.CASES_DIR / "extract_claims.yaml")
    assert case.input["prose"] == casebuilder.live_section_two()
    report = (casebuilder.LIVE_RUN / "report.md").read_text(encoding="utf-8")
    assert case.input["prose"] in report, "the case's prose is not a substring of the report"


def test_extraction_needles_are_claims_of_that_run() -> None:
    """Every expected value is a value of a section 2 claim of the run the prose came from."""
    (case,) = load_cases(casebuilder.CASES_DIR / "extract_claims.yaml")
    payload = json.loads((casebuilder.LIVE_RUN / "claims.json").read_text(encoding="utf-8"))
    values = {
        json.dumps(claim["value"])
        for claim in payload["post_repair"]
        if claim["section"] == "conceptual_soundness" and claim.get("value") is not None
    }
    (needles,) = [assertion.all_ for assertion in case.assertions if assertion.type == "contains"]
    assert len(needles) == 6
    for needle in needles:
        assert needle in values, f"{needle} is not a claimed value of the live section 2"
        assert case.input["prose"].count(needle) == 1, f"{needle} is not unique in the prose"


# -- every case, whatever family ----------------------------------------------------------------


def all_cases() -> list[Any]:
    """Every committed case, in load order."""
    return [case for name in CASE_FILES for case in load_cases(casebuilder.CASES_DIR / name)]


def test_every_case_pins_the_prompt_its_tape_will_be_keyed_on() -> None:
    """`metadata.prompt_sha256` is the digest of the prompt the system under test really sends.

    D-147. A byte count does not pin a prompt: D-146 replaced `above_median` with `below_median`
    and `minimum` with `maximum` in `_LOOP_INSTRUCTION`, which changed every planning tape's
    cassette key and not one byte of the case file. This is the assertion that would have caught
    it, and it is the one that will catch the next such edit before a recording pays for it.
    """
    for case in all_cases():
        sent = casebuilder.prompt_sent(case)
        assert case.metadata["prompt_sha256"] == casebuilder.prompt_digest(sent), (
            f"{case.id} pins a prompt that is no longer the one it sends; re-run "
            "`python tests/probatio/casebuilder.py` and re-record this family's tapes"
        )


def test_every_judge_case_pins_the_rubric_its_judge_tape_will_be_keyed_on() -> None:
    """D-148. A rubric is part of every judge prompt, so editing it strands every judge tape."""
    for case in load_cases(casebuilder.CASES_DIR / "draft_section.yaml"):
        (judge,) = [item for item in case.assertions if item.type == "judge"]
        assert case.metadata["rubric_sha256"] == casebuilder.rubric_digest(judge.rubric), (
            f"{case.id} pins a rubric that is no longer the one it grades against; re-run "
            "`python tests/probatio/casebuilder.py` and re-record this family's judge tapes"
        )


def test_the_rubric_forbids_the_quoting_that_made_80_per_cent_of_replies_unparseable() -> None:
    """D-148. The rubric asked the judge to quote the deciding sentence inside a JSON string.

    Sixteen of the twenty judge replies of the interrupted record run were unparseable for that
    reason, every one of them carrying a verdict Probatio then discarded. The instruction is now
    the opposite one, and this is the assertion that keeps it that way.
    """
    text = casebuilder.RUBRICS_DIR.joinpath("grounding.md").read_text(encoding="utf-8")
    assert "no quotation marks" in text
    assert "no line breaks" in text
    assert "nothing at all after the closing brace" in text
    assert "at most fifteen words" in text
    assert "quotes the sentence that decided it" not in text


def test_the_rubric_lets_a_section_say_an_analysis_does_not_apply() -> None:
    """D-153. Criterion 5 is about quantities absent from the store, never about activities.

    D-100 forbids a section to call a *number* absent; D-114 is explicit that the prohibition "is
    about numbers" and could not reach an activity, and rejected a standing rule that "would also
    forbid Appendix D's own subject matter". Section 5's brief asks the drafter to "say plainly
    which of these do not apply to this model type" and section 7's to "name anything this
    validation could not cover". A rubric that failed those sentences failed the drafter for
    obeying its own brief, which is what it did on the third record run.
    """
    text = casebuilder.RUBRICS_DIR.joinpath("grounding.md").read_text(encoding="utf-8")
    assert "about numbers, not about activities" in text
    assert "does not apply to this model type" in text
    assert "could not cover something" in text


def test_the_pinned_prompt_is_the_one_structured_sends_not_the_one_the_caller_composes() -> None:
    """The digest covers the strict-JSON instruction and the schema, which the tape key does."""
    from quaestor.llm.structured import JSON_INSTRUCTION

    marker = JSON_INSTRUCTION.split("{schema}")[0].strip()
    for case in all_cases():
        assert marker in casebuilder.prompt_sent(case)


def test_the_loop_prompt_no_longer_carries_the_falsified_example() -> None:
    """D-146: `above_median` cannot select a whole split under D-122, so it is not the example."""
    cases = {case.id: case for case in load_cases(casebuilder.CASES_DIR / "plan_followup.yaml")}
    prompt = probatiosupport.loop_prompt_for(cases["plan_followup.first_step"])
    assert "`below_median` on a column whose median is also its\nmaximum" in prompt
    assert "`above_median` on a column whose median is also its" not in prompt


def test_every_case_declares_a_budget() -> None:
    """No case may reach a record run without a ceiling on what it may spend and how long."""
    for case in all_cases():
        assert case.budget.max_cost_usd is not None, f"{case.id} declares no cost ceiling"
        assert case.budget.max_latency_ms is not None, f"{case.id} declares no latency ceiling"
        assert 0.0 < case.budget.max_cost_usd <= 5.0
        assert case.budget.max_latency_ms >= casebuilder.MAX_LATENCY_CEILING_MS


def test_every_case_records_a_snapshot_and_tags() -> None:
    for case in all_cases():
        assert case.snapshot == "scores"
        assert case.tags


def test_case_ids_are_unique_and_name_their_family() -> None:
    ids = [case.id for case in all_cases()]
    assert len(ids) == len(set(ids))
    assert len(ids) == 10
    for case in all_cases():
        family, _, rest = case.id.partition(".")
        assert family in {"draft_section", "extract_claims", "plan_followup"}
        assert rest


def test_the_schema_files_the_assertions_name_exist_and_are_the_generated_ones() -> None:
    """A `schema_file` path is resolved against rootdir, so it is written from there."""
    generated = casebuilder.schemas()
    for case in all_cases():
        for assertion in case.assertions:
            if assertion.type != "schema_valid":
                continue
            path = casebuilder.REPO_ROOT / str(assertion.schema_file)
            assert path.is_file(), f"{case.id} names a schema file that is not committed"
            assert json.loads(path.read_text(encoding="utf-8")) in generated.values()


def test_the_judge_rubric_resolves_from_the_suite_directory() -> None:
    """The rubric a drafting case names is beside the tests, which is the second search dir."""
    from probatio.judge import resolve_rubric

    rubric = resolve_rubric("grounding", rubric_dirs=[Path(__file__).parent / "rubrics"])
    assert rubric.name == "grounding"
    assert "artifacts_json" in rubric.text
    for case in load_cases(casebuilder.CASES_DIR / "draft_section.yaml"):
        (judge,) = [assertion for assertion in case.assertions if assertion.type == "judge"]
        assert judge.rubric == "grounding"
        assert judge.threshold == 1.0


def test_the_distractor_is_not_an_artifact_of_this_run(probatio_run: casebuilder.Capture) -> None:
    """The appended artifact belongs to no section of this subject, which is what makes it one."""
    from quaestor.artifacts.store import ArtifactStore

    store = ArtifactStore(probatio_run.out_dir / "artifacts")
    payload = json.loads(casebuilder.DISTRACTOR)
    assert payload["name"] not in set(store.names())
    for case in load_cases(casebuilder.CASES_DIR / "draft_section.yaml"):
        names = {item["name"] for item in case.input["artifacts_json"]}
        assert payload["name"] not in names


def test_the_guidance_separator_survives_every_format_jitter() -> None:
    """Every jitter transform leaves the span count `guidance_spans` reads unchanged."""
    from probatio.metamorphic.relations import JITTER_TRANSFORMS

    for case in load_cases(casebuilder.CASES_DIR / "draft_section.yaml"):
        text = str(case.input["guidance"])
        expected = len(case.metadata["spans"])
        assert text.count(casebuilder.GUIDANCE_SEPARATOR) == expected - 1
        for transform in JITTER_TRANSFORMS.values():
            jittered = transform(text)
            assert jittered.count(casebuilder.GUIDANCE_SEPARATOR) == expected - 1


# -- the judge's own validation record ------------------------------------------------------------


def test_the_grounding_judge_has_a_validation_record_for_the_rubric_it_grades_with() -> None:
    """D-157. `probatio validate-judge` measured this judge against 40 human labels.

    The record lives where the plugin reads it -- `<rootdir>/.probatio/judges/`, which
    `ProbatioSettings.validation_dir` fixes and no flag moves -- and it is pinned to the rubric's
    content hash, so an edit to `rubrics/grounding.md` makes the judge unvalidated again and the
    seven "rubric has no validation record" warnings come back. That is the mechanism, and this is
    the assertion that says the record on disk is the one this suite's rubric was measured with.
    """
    from probatio.judge import resolve_rubric, rubric_is_validated
    from probatio.judge.validation import load_validation_record

    validation_dir = casebuilder.REPO_ROOT / ".probatio" / "judges"
    rubric = resolve_rubric("grounding", rubric_dirs=[casebuilder.RUBRICS_DIR])
    record = load_validation_record("grounding", validation_dir=validation_dir)
    assert record is not None, "tests/probatio/rubrics/grounding.md has no validation record"
    assert rubric_is_validated(rubric, validation_dir=validation_dir)
    assert record.rubric_hash == rubric.content_hash == casebuilder.rubric_digest("grounding")
    assert record.method == "columns"
    assert record.n == 40
    assert round(record.kappa, 3) == 0.771
    assert round(record.agreement, 3) == 0.95


def test_the_validation_record_names_the_committed_labels_it_was_measured_on() -> None:
    """The 40 labelled rows are committed beside the rubric, and the record's hash is theirs."""
    import csv

    from probatio.judge.validation import hash_labels_file, load_validation_record

    validation_dir = casebuilder.REPO_ROOT / ".probatio" / "judges"
    record = load_validation_record("grounding", validation_dir=validation_dir)
    assert record is not None
    labels = casebuilder.REPO_ROOT / record.labels_file
    assert labels.is_file(), f"{record.labels_file} is named by the record but not committed"
    assert record.labels_hash == hash_labels_file(labels)

    with labels.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == record.n
    pairs = [(row["human"], row["judge"]) for row in rows]
    assert pairs.count(("pass", "pass")) == 34
    assert pairs.count(("pass", "fail")) == 1
    assert pairs.count(("fail", "pass")) == 1
    assert pairs.count(("fail", "fail")) == 4
    assert sum(1 for human, judge in pairs if human == judge) == 38
    assert [human for human, _ in pairs].count("pass") == 35
    assert [judge for _, judge in pairs].count("pass") == 35
    disagreed = {row["id"] for row in rows if row["human"] != row["judge"]}
    assert disagreed == {"conceptual_soundness-03", "summary-03"}
