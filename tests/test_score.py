"""Phase 12: the scorer -- detection, false alarms, collateral judgements and precision.

`04-SEEDED-DEFECT-STUDY.md` section 4 and `docs/STUDY.md` section 5. Two kinds of test here, and
the distinction is deliberate. The first kind scores **real run directories**, produced offline by
`rules_only` validations of variants this test builds, so that the criterion is exercised against
documents the pipeline actually wrote. The second kind scores **hand-written** `findings.json`,
`claims.json`, `trace.jsonl` and `artifacts/index.json` in a temporary directory, because the
cases that matter most -- a check that crashed, a baseline class raised on a seeded variant, an
unevidenced `plain_llm` finding, a control whose baseline nobody has measured -- cannot be
produced offline on demand and are exactly the cases where a scorer quietly gets it wrong.

Nothing here calls a model, downloads anything or reads real data.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from conftest import REPO_ROOT, load_module
from quaestor.llm.offline import OfflineLLM
from quaestor.pipeline import validate

sys.path.insert(0, str(REPO_ROOT / "eval"))
scorer = load_module("quaestor_eval_score_under_test", REPO_ROOT / "eval" / "score.py")
seed_module = load_module("quaestor_eval_seed_under_test", REPO_ROOT / "eval" / "seed.py")

TAXONOMY_FILE = REPO_ROOT / "eval" / "taxonomy.yaml"
SUBJECTS = REPO_ROOT / "subjects"

PINNED = datetime(2026, 9, 18, 6, 52, 57, tzinfo=UTC)
"""A fixed instant, so a test can assert on `summary.json`'s bytes rather than on a clock."""

SCORED = ("credit__T1__false_claim", "credit__C1__smote_uncalibrated", "control_credit_clean")
"""Three variants: a seeded one whose recipe is a `package.yaml` edit, one whose recipe is a
transform with a known collateral finding, and the clean control they are compared against."""


@pytest.fixture(scope="module")
def scored(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Build three variants, validate each under `rules_only`, and score the three run dirs."""
    root = tmp_path_factory.mktemp("score")
    variants, results = root / "variants", root / "results"
    taxonomy = seed_module.load_taxonomy(TAXONOMY_FILE)
    for spec in taxonomy.specs:
        if spec.id in SCORED:
            seed_module.seed(SUBJECTS / spec.subject, spec, variants / spec.id, taxonomy=taxonomy)
            validate(
                variants / spec.id,
                llm=OfflineLLM(),
                config="rules_only",
                synthetic=5000,
                out=results / spec.id,
            )
    return {
        "variants": variants,
        "results": results,
        "score": scorer.score(
            scorer.load_runs(results),
            scorer.load_keys(variants),
            scorer.load_baselines(TAXONOMY_FILE),
        ),
    }


# --- against run directories the pipeline wrote ------------------------------------------------


def test_every_seeded_class_is_detected_and_the_control_raises_no_false_alarm(
    scored: dict[str, Any],
) -> None:
    item = scored["score"]["rules_only"]
    assert item.runs == 3
    assert sorted(item.detected) == ["credit__C1__smote_uncalibrated", "credit__T1__false_claim"]
    assert not item.missed and not item.not_scorable
    assert item.per_class["C1"].to_payload() == {
        "seeded": 1,
        "detected": 1,
        "variants": ["credit__C1__smote_uncalibrated"],
        "missed": [],
    }
    assert not item.false_alarms
    assert item.precision == pytest.approx(1.0)


def test_the_control_s_own_baseline_finding_is_not_a_false_alarm(scored: dict[str, Any]) -> None:
    """D-161: `control_credit_clean` raises `E1` low with nothing seeded in it, measured."""
    runs = {run.variant: run for run in scorer.load_runs(scored["results"])}
    assert ("E1", "low") in runs["control_credit_clean"].raised
    assert not scored["score"]["rules_only"].false_alarms


def test_the_collateral_t1_on_a_seeded_c1_is_the_judgement_decided_in_advance(
    scored: dict[str, Any],
) -> None:
    """`docs/STUDY.md` section 5: the seeded miscalibration breaches the package's own bound."""
    verdicts = {
        (item.variant, item.defect_class): item for item in scored["score"]["rules_only"].collateral
    }
    judged = verdicts[("credit__C1__smote_uncalibrated", "T1")]
    assert judged.verdict == scorer.TRUE_CONSEQUENCE
    assert "calibration_slope" in judged.why
    assert not scored["score"]["rules_only"].spurious


def test_a_low_severity_finding_is_below_the_bar_and_is_not_collateral(
    scored: dict[str, Any],
) -> None:
    item = scored["score"]["rules_only"]
    assert all(entry.severity != "low" for entry in item.collateral)


def test_grounding_is_reported_and_rules_only_is_trivially_one(scored: dict[str, Any]) -> None:
    grounding = scored["score"]["rules_only"].grounding
    assert grounding["pre_repair_mean"] == pytest.approx(1.0)
    assert grounding["post_repair_min"] == pytest.approx(1.0)


def test_the_configuration_is_read_from_the_document_and_not_from_the_path(
    scored: dict[str, Any],
) -> None:
    """A result directory that was moved is still scored as what it ran."""
    assert set(scored["score"]) == {"rules_only"}
    assert all(run.configuration == "rules_only" for run in scorer.load_runs(scored["results"]))


# --- the written cases -------------------------------------------------------------------------


def _write_run(  # noqa: PLR0913 - a run directory is the sum of its four files
    root: Path,
    variant: str,
    *,
    configuration: str = "rules_only",
    findings: list[dict[str, Any]] | None = None,
    not_promoted: list[dict[str, Any]] | None = None,
    artifacts: dict[str, str] | None = None,
    failed_tool: tuple[str, str] | None = None,
    developer: list[dict[str, str]] | None = None,
) -> Path:
    """Write one run directory by hand, with exactly the four files the scorer reads."""
    path = root / variant
    (path / "artifacts").mkdir(parents=True)
    (path / "findings.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "package": "credit_default",
                "version": "1.0",
                "configuration": configuration,
                "run_id": f"{variant}-{configuration}",
                "findings": findings or [],
                "candidates_not_promoted": not_promoted or [],
                "checks_without_candidates": {},
            }
        ),
        encoding="utf-8",
    )
    (path / "claims.json").write_text(
        json.dumps(
            {
                "grounding": {
                    "pre_repair": {"precision": 1.0},
                    "post_repair": {"precision": 1.0},
                },
                "developer_claims": developer or [],
            }
        ),
        encoding="utf-8",
    )
    (path / "artifacts" / "index.json").write_text(
        json.dumps(
            {
                "artifacts": {
                    name: {"hash": digest, "kind": "scalar"}
                    for name, digest in (artifacts or {}).items()
                }
            }
        ),
        encoding="utf-8",
    )
    events = [{"type": "tool_call", "tool": "compute_metrics", "ok": True}]
    if failed_tool is not None:
        events.append(
            {"type": "tool_call", "tool": failed_tool[0], "ok": False, "error": failed_tool[1]}
        )
    (path / "trace.jsonl").write_text(
        "\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8"
    )
    return path


def _write_key(  # noqa: PLR0913 - the answer key is the sum of its five fields
    root: Path,
    variant: str,
    *,
    subject: str = "credit_default",
    status: str = "seeded",
    defect_class: str | None = "L1",
    mode: str = "synthetic",
) -> None:
    """Write one variant's `SEED.yaml`, the file the pipeline never opens."""
    path = root / variant
    path.mkdir(parents=True, exist_ok=True)
    (path / "SEED.yaml").write_text(
        json.dumps(
            {
                "variant": variant,
                "subject": subject,
                "status": status,
                "seeded": {"class": defect_class},
                "mode": mode,
            }
        ),
        encoding="utf-8",
    )


def _score(tmp_path: Path, taxonomy: Path | None = None) -> dict[str, Any]:
    result: dict[str, Any] = scorer.score(
        scorer.load_runs(tmp_path / "results"),
        scorer.load_keys(tmp_path / "variants"),
        scorer.load_baselines(taxonomy or TAXONOMY_FILE),
    )
    return result


def test_a_finding_of_another_class_is_not_a_detection_of_the_seeded_one(tmp_path: Path) -> None:
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "C1", "severity": "high", "evidence": ["aaaaaaaa"]}],
    )
    item = _score(tmp_path)["rules_only"]
    assert item.missed == ["v"] and not item.detected
    assert item.per_class["L1"].missed == ["v"]


def test_a_finding_below_medium_is_not_a_detection(tmp_path: Path) -> None:
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "L1", "severity": "low", "evidence": ["aaaaaaaa"]}],
    )
    assert _score(tmp_path)["rules_only"].missed == ["v"]


def test_a_variant_whose_check_did_not_run_is_set_aside_rather_than_scored_a_miss(
    tmp_path: Path,
) -> None:
    """The contract section 4 owes section 5, read off the trace and not off Appendix D."""
    _write_key(tmp_path / "variants", "v")
    _write_run(tmp_path / "results", "v", failed_tool=("check_leakage", "no id column"))
    item = _score(tmp_path)["rules_only"]
    assert not item.missed and not item.detected
    assert item.not_scorable == [
        {"variant": "v", "class": "L1", "tool": "check_leakage", "message": "no id column"}
    ]
    assert "L1" not in item.per_class


def test_a_check_that_crashed_after_the_class_was_found_anyway_is_still_a_detection(
    tmp_path: Path,
) -> None:
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["aaaaaaaa"]}],
        failed_tool=("check_leakage", "no id column"),
    )
    item = _score(tmp_path)["rules_only"]
    assert item.detected == ["v"] and not item.not_scorable


def test_a_baseline_class_on_a_seeded_variant_needs_evidence_outside_the_baseline(
    tmp_path: Path,
) -> None:
    """The real MSR control raises `C1` on two splits (D-161, D-171); a seed must show more."""
    keys, results = tmp_path / "variants", tmp_path / "results"
    _write_key(keys, "inside", subject="msr_prepayment", defect_class="C1", mode="real")
    _write_run(
        results,
        "inside",
        findings=[{"defect_class": "C1", "severity": "medium", "evidence": ["1111111a"]}],
        artifacts={"calibration_slope.out_of_time": "1111111abbbbbbbb"},
    )
    _write_key(keys, "outside", subject="msr_prepayment", defect_class="C1", mode="real")
    _write_run(
        results,
        "outside",
        findings=[{"defect_class": "C1", "severity": "medium", "evidence": ["2222222a"]}],
        artifacts={"calibration_slope.test": "2222222abbbbbbbb"},
    )
    item = _score(tmp_path)["rules_only"]
    assert item.detected == ["outside"] and item.missed == ["inside"]


def test_the_evidence_join_is_by_prefix_because_the_two_files_keep_different_lengths(
    tmp_path: Path,
) -> None:
    """`findings.json` shortens a hash to eight characters and `artifacts/index.json` keeps 16."""
    _write_key(tmp_path / "variants", "v", defect_class="C1", mode="real", subject="msr_prepayment")
    run = _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "C1", "severity": "medium", "evidence": ["abcdef01"]}],
        artifacts={"calibration_slope.test": "abcdef0123456789"},
    )
    assert scorer._read_run(run).artifact_names(["abcdef01"]) == {"calibration_slope.test"}
    assert scorer._read_run(run).artifact_names(["zzzzzzzz"]) == set()
    assert _score(tmp_path)["rules_only"].detected == ["v"]


def test_a_t1_is_also_detected_by_a_developer_claim_the_matcher_called_a_mismatch(
    tmp_path: Path,
) -> None:
    """The second `T1` channel, which exists only under `--data` (D-016)."""
    _write_key(tmp_path / "variants", "v", defect_class="T1", mode="real")
    _write_run(tmp_path / "results", "v", developer=[{"status": "mismatch"}])
    assert _score(tmp_path)["rules_only"].detected == ["v"]


def test_a_control_finding_the_baseline_does_not_carry_is_a_false_alarm(tmp_path: Path) -> None:
    _write_key(tmp_path / "variants", "control_credit_clean", status="control", defect_class=None)
    _write_run(
        tmp_path / "results",
        "control_credit_clean",
        findings=[
            {"defect_class": "E1", "severity": "low", "evidence": ["aaaaaaaa"]},
            {"defect_class": "M1", "severity": "medium", "evidence": ["bbbbbbbb"]},
        ],
    )
    item = _score(tmp_path)["rules_only"]
    assert item.false_alarms == [
        {"variant": "control_credit_clean", "class": "M1", "severity": "medium"}
    ]
    assert item.precision == pytest.approx(0.0)


def test_a_control_whose_baseline_is_not_measured_is_not_scored_for_false_alarms(
    tmp_path: Path,
) -> None:
    """`null` is "not yet measured", never "empty": both perturbed `real` cells, today."""
    _write_key(
        tmp_path / "variants",
        "control_credit_perturbed",
        status="control",
        defect_class=None,
        mode="real",
    )
    _write_run(
        tmp_path / "results",
        "control_credit_perturbed",
        findings=[{"defect_class": "M1", "severity": "medium", "evidence": ["bbbbbbbb"]}],
    )
    item = _score(tmp_path)["rules_only"]
    assert item.controls_unmeasured == ["control_credit_perturbed"]
    assert not item.false_alarms


def test_a_perturbed_control_is_scored_against_its_own_row_and_not_the_clean_one(
    tmp_path: Path,
) -> None:
    """D-161 gives each control a row, and the four synthetic ones are now all measured (D-184).

    Keying by subject alone would lend the clean control's row to the perturbed one, which is a
    silent pass today -- the two synthetic baselines are equal -- and would be a silent *wrong*
    answer on the day a perturbation stops being harmless.
    """
    baselines = scorer.load_baselines(TAXONOMY_FILE)
    for control in ("control_credit_clean", "control_credit_perturbed"):
        assert baselines.for_control(control, "synthetic").classes == frozenset({("E1", "low")})
    assert not baselines.for_control("control_credit_perturbed", "real").measured
    assert not baselines.for_control("control_msr_perturbed", "real").measured
    assert baselines.for_subject("credit_default", "synthetic").classes == frozenset(
        {("E1", "low")}
    )
    assert baselines.for_subject("msr_prepayment", "synthetic").classes == frozenset()


def test_the_perturbed_controls_carry_the_baseline_measured_offline(tmp_path: Path) -> None:
    """The false-alarm denominator is four controls and not two (D-184)."""
    keys, results = tmp_path / "variants", tmp_path / "results"
    _write_key(keys, "control_credit_perturbed", status="control", defect_class=None)
    _write_run(
        results,
        "control_credit_perturbed",
        findings=[{"defect_class": "E1", "severity": "low", "evidence": ["aaaaaaaa"]}],
    )
    _write_key(
        keys,
        "control_msr_perturbed",
        subject="msr_prepayment",
        status="control",
        defect_class=None,
    )
    _write_run(results, "control_msr_perturbed")
    item = _score(tmp_path)["rules_only"]
    assert not item.controls_unmeasured and not item.false_alarms


def test_the_measured_real_msr_baseline_carries_the_two_decile_tables() -> None:
    """D-171 took that row from three evidence keys to five, and section 5 says to score on it."""
    baseline = scorer.load_baselines(TAXONOMY_FILE).for_subject("msr_prepayment", "real")
    assert baseline.measured and baseline.classes == frozenset({("C1", "medium")})
    assert {"calibration.out_of_time", "calibration.vintage_holdout"} <= baseline.evidence
    assert len(baseline.evidence) == 5


def test_an_unevidenced_plain_llm_candidate_is_a_false_alarm_each(tmp_path: Path) -> None:
    """D-072's arm: ten findings across ten classes, none citing a computed artifact."""
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        configuration="plain_llm",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["aaaaaaaa"]}],
        not_promoted=[
            {"defect_class": "C1", "tool": "plain_llm", "reason": "unevidenced: names nothing"},
            {"defect_class": "S1", "tool": "plain_llm", "reason": "unevidenced: names nothing"},
            {"defect_class": "M1", "tool": "plain_llm", "reason": "merged into F-001"},
        ],
    )
    item = _score(tmp_path)["plain_llm"]
    assert item.unevidenced == 2
    assert item.detected == ["v"]
    assert item.precision == pytest.approx(1 / 3)


def test_a_collateral_finding_nobody_judged_counts_neither_way_and_is_named(
    tmp_path: Path,
) -> None:
    """Section 5 sends an unforeseen pairing to section 9 with a date, not into a number."""
    _write_key(tmp_path / "variants", "v", defect_class="D1")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[
            {"defect_class": "D1", "severity": "medium", "evidence": ["aaaaaaaa"]},
            {"defect_class": "X1", "severity": "high", "evidence": ["bbbbbbbb"]},
        ],
    )
    item = _score(tmp_path)["rules_only"]
    assert [entry.defect_class for entry in item.unjudged] == ["X1"]
    assert "section 9" in item.unjudged[0].why
    assert not item.spurious and item.precision == pytest.approx(1.0)


def test_a_collateral_r1_is_spurious_and_counts_against_precision(tmp_path: Path) -> None:
    """D-164 tightened the sign-flip rule before the study so that one appearing now costs."""
    _write_key(tmp_path / "variants", "v", defect_class="D1")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[
            {"defect_class": "D1", "severity": "medium", "evidence": ["aaaaaaaa"]},
            {"defect_class": "R1", "severity": "medium", "evidence": ["bbbbbbbb"]},
        ],
    )
    item = _score(tmp_path)["rules_only"]
    assert [entry.verdict for entry in item.spurious] == [scorer.SPURIOUS]
    assert item.precision == pytest.approx(0.5)


def test_a_collateral_class_the_clean_control_also_raises_is_the_baseline_showing_through(
    tmp_path: Path,
) -> None:
    """D-161 read the only way it can be: a finding without a seed is not about the seed."""
    _write_key(tmp_path / "variants", "v", subject="msr_prepayment", defect_class="L2", mode="real")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[
            {"defect_class": "L2", "severity": "medium", "evidence": ["aaaaaaaa"]},
            {"defect_class": "C1", "severity": "medium", "evidence": ["bbbbbbbb"]},
        ],
    )
    item = _score(tmp_path)["rules_only"]
    assert [entry.verdict for entry in item.collateral] == [scorer.BASELINE]
    assert not item.spurious and not item.unjudged
    assert item.precision == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("seeded", "raised", "subject", "verdict"),
    [
        ("S1", "T1", "credit_default", scorer.TRUE_CONSEQUENCE),
        ("C1", "T1", "msr_prepayment", scorer.TRUE_CONSEQUENCE),
        ("L1", "X1", "msr_prepayment", scorer.TRUE_CONSEQUENCE),
        ("L1", "C1", "credit_default", scorer.TRUE_CONSEQUENCE),
        ("S1", "C1", "msr_prepayment", scorer.TRUE_CONSEQUENCE),
        ("L1", "X1", "credit_default", scorer.UNJUDGED),
        ("L1", "C1", "msr_prepayment", scorer.UNJUDGED),
        ("S1", "C1", "credit_default", scorer.UNJUDGED),
        ("D1", "R1", "credit_default", scorer.SPURIOUS),
    ],
    ids=[
        "s1-t1",
        "c1-t1",
        "msr-l1-x1",
        "credit-l1-c1",
        "msr-s1-c1",
        "credit-l1-x1",
        "msr-l1-c1",
        "credit-s1-c1",
        "r1",
    ],
)
def test_each_judgement_is_the_one_the_protocol_decided(
    seeded: str, raised: str, subject: str, verdict: str
) -> None:
    """Including the three pairings section 5 names a subject for, which do not carry across."""
    key = scorer.VariantKey("v", subject, "seeded", seeded, "synthetic")
    judged = scorer.judge_collateral(key, raised, "medium", scorer.Baseline(measured=False))
    assert judged.verdict == verdict


def test_the_msr_s1_c1_rule_carries_the_date_it_was_decided_and_its_reasoning() -> None:
    """Section 5's sixth rule, decided at scoring time rather than in advance, and saying so.

    Five rules were fixed in Phase 10 before any variant ran; this one was written after the free
    sweep surfaced the pairing, so `summary.json` carries both dates and a reader can tell them
    apart. D-161 measured the identical mechanism on the *real* MSR control and recorded it there
    as a true finding, which is the reasoning the rule has to carry: a hazard fitted through 2019
    and tested on the 2020-21 refinancing wave under-predicts prepayment whether the panel it is
    fitted on was generated or delivered.
    """
    key = scorer.VariantKey("msr__S1__vintage_shift", "msr_prepayment", "seeded", "S1", "synthetic")
    judged = scorer.judge_collateral(key, "C1", "medium", scorer.Baseline(measured=False))
    assert judged.verdict == scorer.TRUE_CONSEQUENCE
    assert judged.decided == "2026-09-17, D-182 amendment, at scoring time"
    assert "D-161" in judged.why and "refinancing wave" in judged.why
    assert judged.to_payload()["decided"] == judged.decided

    advance = scorer.judge_collateral(
        scorer.VariantKey("v", "credit_default", "seeded", "C1", "synthetic"),
        "T1",
        "high",
        scorer.Baseline(measured=False),
    )
    assert advance.decided == scorer.IN_ADVANCE
    assert "before any variant was run" in advance.decided


# --- the file the study publishes and the command line -----------------------------------------


def test_the_summary_says_what_it_was_computed_from(tmp_path: Path) -> None:
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["aaaaaaaa"]}],
    )
    result = scorer.StudyScore(
        generated=PINNED,
        results_dir=str(tmp_path / "results"),
        variants_dir=str(tmp_path / "variants"),
        taxonomy=str(TAXONOMY_FILE),
        configurations=_score(tmp_path),
    )
    payload = result.to_payload()
    assert payload["schema_version"] == 1
    assert payload["generated"] == "2026-09-18T06:52:57Z"
    assert payload["taxonomy"] == str(TAXONOMY_FILE)
    block = payload["configurations"]["rules_only"]
    assert block["detected"] == ["v"] and block["precision"] == pytest.approx(1.0)
    assert block["per_class"]["L1"]["seeded"] == 1
    assert block["grounding"]["pre_repair_mean"] == pytest.approx(1.0)


def test_a_run_whose_variant_has_no_answer_key_is_named_and_not_scored(tmp_path: Path) -> None:
    (tmp_path / "variants").mkdir()
    _write_run(
        tmp_path / "results",
        "stranger",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["a"]}],
    )
    assert _score(tmp_path) == {}
    code = scorer.main(
        [
            "--results",
            str(tmp_path / "results"),
            "--variants",
            str(tmp_path / "variants"),
            "--out",
            str(tmp_path / "summary.json"),
        ]
    )
    assert code == 1
    payload = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert payload["variants_without_an_answer_key"] == ["stranger"]


def test_the_command_line_scores_a_directory_and_writes_a_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["aaaaaaaa"]}],
    )
    code = scorer.main(
        [
            "--results",
            str(tmp_path / "results"),
            "--variants",
            str(tmp_path / "variants"),
            "--taxonomy",
            str(TAXONOMY_FILE),
            "--out",
            str(tmp_path / "summary.json"),
        ]
    )
    printed = capsys.readouterr().out
    assert code == 0
    assert "rules_only: 1/1 seeded variants detected over 1 run(s)" in printed
    assert "L1: 1/1" in printed and "precision 1.0000" in printed
    assert (tmp_path / "summary.json").is_file()


def test_the_command_line_says_what_a_human_still_owes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A miss is a result; an unmeasured baseline is homework, and homework exits 1."""
    _write_key(
        tmp_path / "variants",
        "control_credit_perturbed",
        status="control",
        defect_class=None,
        mode="real",
    )
    _write_run(tmp_path / "results", "control_credit_perturbed")
    code = scorer.main(
        ["--results", str(tmp_path / "results"), "--variants", str(tmp_path / "variants")]
    )
    assert code == 1
    assert "its baseline is not measured" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("make", "needle"),
    [
        (lambda root: root / "nowhere", "no results directory"),
        (lambda root: root, "holds no run directory"),
    ],
    ids=["no-directory", "no-runs"],
)
def test_a_results_directory_that_holds_no_run_says_so(
    tmp_path: Path, make: Any, needle: str
) -> None:
    with pytest.raises(ValueError, match=needle):
        scorer.load_runs(make(tmp_path))


def test_a_variants_directory_that_is_not_there_says_so(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no variants directory"):
        scorer.load_keys(tmp_path / "nowhere")


def test_a_variant_set_aside_because_its_check_crashed_is_homework_too(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A miss is a result and exits 0; a variant nobody could score is a thing to go and fix."""
    _write_key(tmp_path / "variants", "v")
    _write_run(tmp_path / "results", "v", failed_tool=("check_leakage", "no id column"))
    code = scorer.main(
        ["--results", str(tmp_path / "results"), "--variants", str(tmp_path / "variants")]
    )
    assert code == 1
    assert "not scored: v (L1) — check_leakage did not run" in capsys.readouterr().out


def test_a_plain_miss_is_a_result_and_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "C1", "severity": "high", "evidence": ["aaaaaaaa"]}],
    )
    code = scorer.main(
        ["--results", str(tmp_path / "results"), "--variants", str(tmp_path / "variants")]
    )
    assert code == 0
    assert "L1: 0/1; missed v" in capsys.readouterr().out


def test_the_summary_carries_the_date_it_was_scored_and_spells_it_as_a_report_does(
    tmp_path: Path,
) -> None:
    """`summary.json` travels without its run directory, so the date has to be inside it.

    The README and `docs/STUDY.md` quote from the published `summary.json`; a reader of those
    numbers may never see the directory whose name carries the stamp, and a directory name is the
    operator's anyway rather than something the scoring wrote. The spelling is the one the
    report's own front matter uses -- UTC, to the second, `Z`-suffixed -- so that comparing the
    two does not mean parsing two formats.
    """
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["aaaaaaaa"]}],
    )
    out = tmp_path / "summary.json"
    code = scorer.main(
        [
            "--results",
            str(tmp_path / "results"),
            "--variants",
            str(tmp_path / "variants"),
            "--out",
            str(out),
        ],
        generated=PINNED,
    )
    assert code == 0
    assert json.loads(out.read_text(encoding="utf-8"))["generated"] == "2026-09-18T06:52:57Z"


def test_the_stamp_is_utc_whatever_zone_it_is_handed() -> None:
    """A clock in another zone is converted, not printed; microseconds are dropped."""
    assert scorer.stamp(datetime(2026, 9, 18, 6, 52, 57, 123456, tzinfo=UTC)) == (
        "2026-09-18T06:52:57Z"
    )
    local = datetime(2026, 9, 17, 23, 52, 57, tzinfo=timezone(timedelta(hours=-7)))
    assert scorer.stamp(local) == "2026-09-18T06:52:57Z"


def test_scoring_with_no_timestamp_uses_the_clock(tmp_path: Path) -> None:
    """The default path, which no other test can assert on without asserting on a clock."""
    _write_key(tmp_path / "variants", "v")
    _write_run(
        tmp_path / "results",
        "v",
        findings=[{"defect_class": "L1", "severity": "high", "evidence": ["aaaaaaaa"]}],
    )
    out = tmp_path / "summary.json"
    before = datetime.now(UTC).replace(microsecond=0)
    scorer.main(
        [
            "--results",
            str(tmp_path / "results"),
            "--variants",
            str(tmp_path / "variants"),
            "--out",
            str(out),
        ]
    )
    written = json.loads(out.read_text(encoding="utf-8"))["generated"]
    assert written.endswith("Z")
    assert before <= datetime.fromisoformat(written.replace("Z", "+00:00"))
