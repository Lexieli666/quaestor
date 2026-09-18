"""The study's scorer: run directories in, `summary.json` out, no prose read on the way.

`04-SEEDED-DEFECT-STUDY.md` section 4 and `docs/STUDY.md` section 5. Every number the study
publishes is computed here from four files of a run directory -- `findings.json`, `claims.json`,
`trace.jsonl` and `artifacts/index.json` -- plus the variant's `SEED.yaml` and the taxonomy's
measured control baselines. `report.md` is never opened: a scorer that reads the prose is scoring
the drafter, and the drafter is what the grounding figures are for.

**Detection** is `04` section 4's criterion unchanged: a finding of the *seeded* class at severity
at least `medium`. A finding of another class is not a detection of the seeded one, however
plausibly it follows from it -- those are collateral findings and are judged separately. `T1`
carries a second channel, a developer claim the matcher marked `mismatch`, which exists only under
`--data` (D-016).

**Three rules keep the numbers honest, and each of them was decided before any run.**

*A baseline finding is not a detection and is not a false alarm.* Each control carries a measured
baseline finding set per data mode (D-161, amended by D-171), and on a seeded variant of the same
subject and mode, a finding of a baseline class counts only when it cites an artifact the baseline
did not (`docs/STUDY.md` section 5). Evidence hashes are eight characters in `findings.json` and
sixteen in `artifacts/index.json`, so the comparison is by prefix and never by equality.

*A control whose baseline has not been measured is not scored for false alarms.* `null` in the
taxonomy means "not yet measured" and not "empty"; scoring against it would publish every one of
that control's findings as a false alarm, which is the arithmetic of an unmeasured baseline rather
than a fact about the detector.

*A variant whose seeded class had no check to raise it is not scored at all.* Since D-177 a
rule-based check that raises costs its own row and not the run, so a report can be complete but
for the one check that would have screened for the planted defect. Scoring that as a miss measures
a crash, so the variant is set aside and named -- and it is the trace's own `tool_call` event that
says so, not the report's Appendix D, because this file does not read prose.

A collateral judgement carries the **date it was decided** and where. Five were decided in Phase
10, before any variant was run; the sixth -- a seeded MSR `S1` also raising `C1` -- was decided at
scoring time on 2026-09-17, and says so in `summary.json`, because a reader is entitled to tell a
rule fixed in advance from one written after the numbers were seen.

**Precision** is detections over detections plus everything raised at severity at least medium
that should not have been: false alarms on the controls, collateral findings judged spurious, and
`plain_llm`'s unevidenced findings, which sit in `candidates_not_promoted` with a reason beginning
`unevidenced:` and are a false alarm each (D-072, `04` section 4).

Two columns `docs/STUDY.md` section 5 asks for are deliberately absent, and their absence is the
cut list's, not an oversight: the descriptive open-items column and the cost and latency
aggregation, both of which are recoverable from the traces and the ledger after the fact.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import yaml

from quaestor.configs import SCREENED_CLASSES
from quaestor.findings import DefectClass, Severity, severity_rank

__all__ = [
    "COLLATERAL_RULES",
    "DETECTION_SEVERITY",
    "UNEVIDENCED_PREFIX",
    "Baselines",
    "ClassScore",
    "Collateral",
    "ConfigurationScore",
    "RunDirectory",
    "NoReport",
    "StudyScore",
    "load_no_report",
    "load_runs",
    "main",
    "score",
    "stamp",
]

DETECTION_SEVERITY: Final = Severity.medium
"""The bar a finding clears to count, for detection, for a false alarm and for collateral."""

UNEVIDENCED_PREFIX: Final = "unevidenced:"
"""How `quaestor.pipeline` marks a `plain_llm` finding whose evidence resolves to nothing."""

LEDGER_FILE: Final = "ledger.json"
"""What `quaestor study run` wrote. The only record of a cell that produced no report at all."""

SEED_FILE: Final = "SEED.yaml"
FINDINGS_FILE: Final = "findings.json"
CLAIMS_FILE: Final = "claims.json"
TRACE_FILE: Final = "trace.jsonl"
INDEX_FILE: Final = Path("artifacts") / "index.json"

SYNTHETIC_MODE: Final = "synthetic"
REAL_MODE: Final = "real"

TRUE_CONSEQUENCE: Final = "true_consequence"
SPURIOUS: Final = "spurious"
BASELINE: Final = "baseline"
UNJUDGED: Final = "unjudged"
"""The four verdicts a collateral finding can carry. Only `spurious` counts against precision."""

MISMATCH: Final = "mismatch"
"""The developer-claim status that is the `T1` arm's second detection channel (D-016)."""

IN_ADVANCE: Final = "2026-09-09, D-136, before any variant was run"
"""When section 5's original five collateral judgements were made."""


@dataclass(frozen=True)
class CollateralRule:
    """One judgement decided in advance, `docs/STUDY.md` section 5 from D-136's measurements.

    Attributes:
        seeded: The class the variant was seeded with, or `None` for "whichever it was".
        raised: The class that was also raised.
        subject: The subject this holds on, or `None` for both.
        verdict: `true_consequence` or `spurious`.
        why: The sentence section 5 gives, carried into `summary.json` so a reader of the numbers
            does not have to go and find the protocol to learn why a finding was forgiven.
        decided: When the judgement was made and where it is recorded. Section 5's five were
            decided in Phase 10 from D-136's measurements, before any variant was run; a judgement
            made at scoring time carries the date section 5 asks section 9 to record, so that a
            reader of `summary.json` can tell the two apart without being told.
    """

    seeded: str | None
    raised: str
    subject: str | None
    verdict: str
    why: str
    decided: str = IN_ADVANCE


COLLATERAL_RULES: Final[tuple[CollateralRule, ...]] = (
    CollateralRule(
        "S1",
        "T1",
        None,
        TRUE_CONSEQUENCE,
        "the seeded population shift breaches the package's own declared psi bound, which is a "
        "true statement about the model as delivered",
    ),
    CollateralRule(
        "C1",
        "T1",
        None,
        TRUE_CONSEQUENCE,
        "the seeded miscalibration breaches the package's own declared calibration_slope bound, "
        "which is a true statement about the model as delivered",
    ),
    CollateralRule(
        "L1",
        "X1",
        "msr_prepayment",
        TRUE_CONSEQUENCE,
        "the leaked end-of-month balance dominates the projection, so the scenario curve really "
        "is inconsistent",
    ),
    CollateralRule(
        "L1",
        "C1",
        "credit_default",
        TRUE_CONSEQUENCE,
        "the leak distorts the champion, so the fitted probabilities really are miscalibrated",
    ),
    CollateralRule(
        None,
        "R1",
        None,
        SPURIOUS,
        "a sign flip on a coefficient indistinguishable from zero; D-164 tightened the rule "
        "before the study so that one appearing now counts against precision",
    ),
    CollateralRule(
        "S1",
        "C1",
        "msr_prepayment",
        TRUE_CONSEQUENCE,
        "the seeded vintage shift trains the hazard through 2019 and tests it on the 2020-21 "
        "refinancing wave, so the model really does under-predict prepayment on the tested split: "
        "this is the same mechanism D-161 measured on the real MSR control and recorded there as "
        "a true finding, and a mechanism cannot be true on a real panel and spurious on a "
        "synthetic one built to carry it",
        decided="2026-09-17, D-182 amendment, at scoring time",
    ),
)
"""Every collateral verdict that was decided before a run, and nothing else.

A collateral finding no rule covers is recorded `unjudged` and is counted in neither the numerator
nor the denominator of precision. That is not a way of being kind to the detector: `docs/STUDY.md`
section 5 says such a judgement is made at scoring time and written into section 9 with its date,
and a number published before that judgement exists would be a number nobody decided. The sixth
rule is what that procedure looks like when it runs: the free `rules_only` sweep surfaced the
pairing, a human judged it, and it is in the table with its date rather than absorbed into the
five that were fixed in advance.
"""

_CLASS_TOOLS: Final[Mapping[str, tuple[str, ...]]] = {
    item.value: tuple(tool for tool, classes in SCREENED_CLASSES.items() if item in classes)
    for item in DefectClass
}
"""Which checks screen for each class, inverted from the one table that states it."""


@dataclass(frozen=True)
class RunDirectory:
    """One finished run: where it is, what it ran, and the four files it is scored from.

    Attributes:
        path: The run directory.
        variant: The variant id, which is the directory's own name.
        configuration: Read from `findings.json`, not from the path, so a result that was moved is
            still scored as what it is.
        findings: The parsed `findings.json`.
        claims: The parsed `claims.json`.
    """

    path: Path
    variant: str
    configuration: str
    findings: Mapping[str, Any]
    claims: Mapping[str, Any]

    @property
    def raised(self) -> list[tuple[str, str]]:
        """Every finding as `(class, severity)`, in the document's own order."""
        return [
            (str(item["defect_class"]), str(item["severity"]))
            for item in self.findings.get("findings", [])
        ]

    def at_or_above(self, bar: Severity) -> list[Mapping[str, Any]]:
        """The findings at or above a severity."""
        return [
            item
            for item in self.findings.get("findings", [])
            if severity_rank(Severity(item["severity"])) <= severity_rank(bar)
        ]

    @property
    def unevidenced(self) -> int:
        """How many candidates were declined for having no evidence at all (D-072)."""
        return sum(
            1
            for item in self.findings.get("candidates_not_promoted", [])
            if str(item.get("reason", "")).startswith(UNEVIDENCED_PREFIX)
        )

    @property
    def developer_mismatch(self) -> bool:
        """Whether the matcher marked any declared developer claim a mismatch."""
        return any(
            str(item.get("status")) == MISMATCH for item in self.claims.get("developer_claims", [])
        )

    def grounding(self, when: str) -> float | None:
        """The grounding precision `pre_repair` or `post_repair`, or `None` if not recorded."""
        block = self.claims.get("grounding", {}).get(when, {})
        value = block.get("precision")
        return float(value) if value is not None else None

    def artifact_names(self, hashes: Sequence[str]) -> set[str]:
        """The logical names of the artifacts a finding cited, matched by hash prefix.

        `findings.json` shortens an evidence hash to eight characters and `artifacts/index.json`
        keeps sixteen, so the join is a prefix match. A hash that names nothing in the index is
        simply absent from the answer; the run's own grounding figures are where a dangling
        citation is counted, not here.
        """
        index = self.path / INDEX_FILE
        if not index.is_file():
            return set()
        payload = json.loads(index.read_text(encoding="utf-8")).get("artifacts", {})
        names = set()
        for name, entry in payload.items():
            full = str(entry.get("hash", ""))
            if any(full.startswith(short) for short in hashes):
                names.add(str(name))
        return names

    @property
    def checks_that_did_not_run(self) -> dict[str, str]:
        """The tools whose `tool_call` event carries an error, from the trace (D-177).

        The report says this in Appendix D and `ValidationRun` says it in `checks_failed`; the
        trace is the one of the three that is machine-readable *and* in the run directory, which
        is what this file has.
        """
        path = self.path / TRACE_FILE
        if not path.is_file():
            return {}
        failed: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("type") == "tool_call" and event.get("error"):
                failed[str(event["tool"])] = str(event["error"])
        return failed


def load_runs(results_dir: Path | str) -> list[RunDirectory]:
    """Find every run directory under a path, however deeply it is nested.

    A run directory is one that holds a `findings.json`. That admits both shapes the study
    produces -- `quaestor study run`'s `<configuration>/<variant>/` tree and the flat directory of
    `quaestor validate --out` calls that the free `rules_only` sweep wrote -- without either of
    them having to declare which it is, and the configuration is read out of the file rather than
    guessed from the path.

    Args:
        results_dir: Where to look.

    Returns:
        The runs, ordered by configuration and then by variant.

    Raises:
        ValueError: There is no such directory, or it holds no run.
    """
    root = Path(results_dir)
    if not root.is_dir():
        raise ValueError(f"there is no results directory at {root}")
    runs = [_read_run(path.parent) for path in sorted(root.rglob(FINDINGS_FILE))]
    if not runs:
        raise ValueError(f"{root} holds no run directory: nothing under it has a {FINDINGS_FILE}")
    return sorted(runs, key=lambda run: (run.configuration, run.variant))


@dataclass(frozen=True)
class NoReport:
    """A cell the harness ran that produced no report, read from the ledger.

    Attributes:
        variant: Which variant.
        configuration: Which configuration.
        status: `rejected` -- the renderer refused what the model wrote -- or `failed`.
        reason: The error the ledger recorded.
    """

    variant: str
    configuration: str
    status: str
    reason: str

    def to_payload(self) -> dict[str, Any]:
        """The row `summary.json` carries."""
        return {
            "variant": self.variant,
            "status": self.status,
            "reason": self.reason,
        }


def load_no_report(results_dir: Path | str) -> list[NoReport]:
    """Read the cells the harness ran that left no `findings.json`, from `ledger.json`.

    **Why the ledger is an input at all.** Every other number here comes from a run directory, and
    a run that produced no report has none -- `pipeline.validate` writes `report.md` before
    `claims.json` and `findings.json`, so a renderer refusal loses all three. Such a cell is
    therefore *invisible* to a scorer that enumerates by `findings.json`, and invisible is the
    worst thing it could be: the arm's recall would be computed over the cells that worked and
    printed as the arm's whole story, dropping exactly the cell where it misbehaved. That flatters
    the detector, silently, which is the class of default D-182 exists to refuse.

    `docs/STUDY.md` section 5 already says what to do with one -- "a run that produces no report is
    scored as a miss with no report, listed in the miss list ... and counted against the
    configuration" -- and this is what lets the scorer obey it.

    Args:
        results_dir: The study directory, whose `ledger.json` is read when it is there.

    Returns:
        One entry per cell the ledger records as `rejected` or `failed`, ordered by configuration
        and then variant. Empty when there is no ledger, which is the case for a directory of
        `quaestor validate` runs.
    """
    path = Path(results_dir) / LEDGER_FILE
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        NoReport(
            variant=str(cell["variant"]),
            configuration=str(cell["configuration"]),
            status=str(cell["status"]),
            reason=str(cell.get("error") or "no reason recorded"),
        )
        for cell in payload.get("cells", [])
        if str(cell["status"]) != "done"
    ]
    return sorted(rows, key=lambda row: (row.configuration, row.variant))


def _read_run(path: Path) -> RunDirectory:
    """Read one run directory's two documents."""
    findings = json.loads((path / FINDINGS_FILE).read_text(encoding="utf-8"))
    claims_path = path / CLAIMS_FILE
    claims = json.loads(claims_path.read_text(encoding="utf-8")) if claims_path.is_file() else {}
    return RunDirectory(
        path=path,
        variant=path.name,
        configuration=str(findings.get("configuration", "")),
        findings=findings,
        claims=claims,
    )


@dataclass(frozen=True)
class VariantKey:
    """What `SEED.yaml` says about a variant: what was planted in it, and on what.

    Attributes:
        variant: The variant id.
        subject: The subject it was seeded from.
        status: `seeded` or `control`.
        defect_class: The class that was planted, or `None` on a control.
        mode: `synthetic` or `real`.
    """

    variant: str
    subject: str
    status: str
    defect_class: str | None
    mode: str

    @property
    def is_control(self) -> bool:
        """Whether this variant is one of the four controls."""
        return self.status == "control"


def load_keys(variants_dir: Path | str) -> dict[str, VariantKey]:
    """Read every variant's answer key.

    Args:
        variants_dir: Where `quaestor study build` wrote the variants.

    Returns:
        One key per variant that carries a `SEED.yaml`, by variant id.

    Raises:
        ValueError: There is no such directory.
    """
    root = Path(variants_dir)
    if not root.is_dir():
        raise ValueError(f"there is no variants directory at {root}")
    keys: dict[str, VariantKey] = {}
    for path in sorted(root.glob(f"*/{SEED_FILE}")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        seeded = payload.get("seeded") or {}
        keys[str(payload["variant"])] = VariantKey(
            variant=str(payload["variant"]),
            subject=str(payload["subject"]),
            status=str(payload["status"]),
            defect_class=seeded.get("class"),
            mode=str(payload.get("mode", SYNTHETIC_MODE)),
        )
    return keys


@dataclass(frozen=True)
class Baseline:
    """One control's measured baseline for one data mode, or the fact that it has none.

    Attributes:
        measured: Whether the taxonomy carries a measurement for this control and mode. `False`
            means `null`, which is "not yet measured" and never "empty".
        classes: The classes the baseline raises, as `(class, severity)`.
        evidence: The artifact names the baseline's findings cite, pooled.
    """

    measured: bool
    classes: frozenset[tuple[str, str]] = frozenset()
    evidence: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Baselines:
    """Every measured baseline the taxonomy carries, in the two shapes scoring needs.

    Attributes:
        by_control: One baseline per control id and data mode. This is what a *control* is scored
            against: D-161 gives each control its own row, and the two perturbed controls' rows are
            `null` until a human measures them.
        by_subject: One baseline per subject and data mode, from the *clean* control's row. This
            is what a *seeded* variant is scored against, because the question a seeded variant
            asks is what the subject does with nothing planted in it.
    """

    by_control: Mapping[tuple[str, str], Baseline]
    by_subject: Mapping[tuple[str, str], Baseline]

    def for_control(self, variant: str, mode: str) -> Baseline:
        """The baseline this control is scored against."""
        return self.by_control.get((variant, mode), Baseline(measured=False))

    def for_subject(self, subject: str, mode: str) -> Baseline:
        """The baseline a seeded variant of this subject is scored against."""
        return self.by_subject.get((subject, mode), Baseline(measured=False))


def _baseline_of(declared: Any, mode: str) -> Baseline:
    """Read one control row's baseline for one data mode.

    `null` is "not yet measured" and an absent mode is the same thing; only a list -- empty
    included -- is a measurement.
    """
    rows = declared.get(mode) if isinstance(declared, dict) else None
    if rows is None:
        return Baseline(measured=False)
    return Baseline(
        measured=True,
        classes=frozenset((str(row["class"]), str(row["severity"])) for row in rows),
        evidence=frozenset(str(name) for row in rows for name in (row.get("evidence") or [])),
    )


def load_baselines(taxonomy_path: Path | str) -> Baselines:
    """Read the measured control baselines out of the taxonomy.

    Args:
        taxonomy_path: `eval/taxonomy.yaml`.

    Returns:
        The baselines, by control and by subject.
    """
    payload = yaml.safe_load(Path(taxonomy_path).read_text(encoding="utf-8"))
    by_control: dict[tuple[str, str], Baseline] = {}
    by_subject: dict[tuple[str, str], Baseline] = {}
    for control in payload.get("controls", []):
        declared = control.get("baseline")
        for mode in (SYNTHETIC_MODE, REAL_MODE):
            baseline = _baseline_of(declared, mode)
            by_control[(str(control["id"]), mode)] = baseline
            if control.get("recipe") == "none":
                by_subject[(str(control["subject"]), mode)] = baseline
    return Baselines(by_control=by_control, by_subject=by_subject)


@dataclass
class Collateral:
    """One finding of a class the variant was not seeded with, and its verdict."""

    variant: str
    defect_class: str
    severity: str
    verdict: str
    why: str
    decided: str | None = None

    def to_payload(self) -> dict[str, Any]:
        """The row `summary.json` carries."""
        return {
            "variant": self.variant,
            "class": self.defect_class,
            "severity": self.severity,
            "verdict": self.verdict,
            "why": self.why,
            "decided": self.decided,
        }


def judge_collateral(
    key: VariantKey, defect_class: str, severity: str, baseline: Baseline
) -> Collateral:
    """Judge one collateral finding by the rules decided before the study.

    Args:
        key: The variant's answer key.
        defect_class: The class that was raised and not seeded.
        severity: Its severity.
        baseline: The clean control's baseline for this subject and mode.

    Returns:
        The finding with its verdict. A class the subject's own clean control raises at the same
        severity is `baseline`, which is D-161's rule read the only way it can be: a finding the
        unseeded subject also produces is not evidence about the seeding.
    """
    if baseline.measured and (defect_class, severity) in baseline.classes:
        return Collateral(
            key.variant,
            defect_class,
            severity,
            BASELINE,
            f"the clean {key.subject} control raises {defect_class} at {severity} on {key.mode} "
            "data with nothing seeded in it (D-161)",
            "2026-09-16, D-161, measured before the study",
        )
    for rule in COLLATERAL_RULES:
        if rule.raised != defect_class:
            continue
        if rule.seeded is not None and rule.seeded != key.defect_class:
            continue
        if rule.subject is not None and rule.subject != key.subject:
            continue
        return Collateral(key.variant, defect_class, severity, rule.verdict, rule.why, rule.decided)
    return Collateral(
        key.variant,
        defect_class,
        severity,
        UNJUDGED,
        "no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, "
        "with its date, before this finding enters a published number",
    )


@dataclass
class ClassScore:
    """Detection for one defect class, as counts and never as a bare percentage."""

    seeded: int = 0
    detected: int = 0
    variants: list[str] = field(default_factory=list)
    missed: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        """The row `summary.json` carries."""
        return {
            "seeded": self.seeded,
            "detected": self.detected,
            "variants": list(self.variants),
            "missed": list(self.missed),
        }


@dataclass
class ConfigurationScore:
    """Everything the study publishes about one configuration.

    Attributes:
        configuration: Which one.
        runs: How many run directories it was scored from.
        per_class: Detection by seeded class.
        detected: Variants whose seeded class was found.
        missed: Variants whose seeded class was not.
        not_scorable: Variants set aside because the check that screens their class did not run,
            with the tool and its own message.
        no_report: Cells the harness ran that produced no report at all, from the ledger. A seeded
            one is a **miss** -- `docs/STUDY.md` section 5's own rule -- named rather than
            silently absent; a control has no detection to lose and is listed only.
        false_alarms: Findings on the controls that the control's baseline does not carry.
        controls_unmeasured: Controls whose baseline is `null`, so their false-alarm arm is not
            scored at all.
        collateral: Every non-seeded finding at or above the bar, with its verdict.
        unevidenced: `plain_llm`'s unevidenced candidates, one false alarm each.
        grounding: Mean and minimum grounding precision, pre- and post-repair.
    """

    configuration: str
    runs: int = 0
    per_class: dict[str, ClassScore] = field(default_factory=dict)
    detected: list[str] = field(default_factory=list)
    missed: list[str] = field(default_factory=list)
    not_scorable: list[dict[str, str]] = field(default_factory=list)
    no_report: list[NoReport] = field(default_factory=list)
    false_alarms: list[dict[str, str]] = field(default_factory=list)
    controls_unmeasured: list[str] = field(default_factory=list)
    collateral: list[Collateral] = field(default_factory=list)
    unevidenced: int = 0
    grounding: dict[str, float | None] = field(default_factory=dict)

    @property
    def spurious(self) -> list[Collateral]:
        """The collateral findings that count against precision."""
        return [item for item in self.collateral if item.verdict == SPURIOUS]

    @property
    def unjudged(self) -> list[Collateral]:
        """The collateral findings nobody has judged yet, which count neither way."""
        return [item for item in self.collateral if item.verdict == UNJUDGED]

    @property
    def precision(self) -> float | None:
        """Detections over detections plus everything raised that should not have been."""
        wrong = len(self.false_alarms) + len(self.spurious) + self.unevidenced
        total = len(self.detected) + wrong
        return len(self.detected) / total if total else None

    def to_payload(self) -> dict[str, Any]:
        """The block `summary.json` carries for this configuration."""
        return {
            "configuration": self.configuration,
            "runs": self.runs,
            "seeded_scored": len(self.detected) + len(self.missed),
            "detected": list(self.detected),
            "missed": list(self.missed),
            "not_scorable": list(self.not_scorable),
            "no_report": [item.to_payload() for item in self.no_report],
            "per_class": {name: item.to_payload() for name, item in sorted(self.per_class.items())},
            "false_alarms": list(self.false_alarms),
            "controls_with_unmeasured_baseline": list(self.controls_unmeasured),
            "collateral": [item.to_payload() for item in self.collateral],
            "collateral_spurious": len(self.spurious),
            "collateral_unjudged": len(self.unjudged),
            "unevidenced_findings": self.unevidenced,
            "precision": self.precision,
            "grounding": dict(self.grounding),
        }


@dataclass
class StudyScore:
    """Every configuration's score, and what the whole thing was computed from.

    Attributes:
        generated: When the scoring ran, UTC to the second. `summary.json` is the file the README
            and `docs/STUDY.md` quote from, and it travels without the run directory it was
            computed in -- so the date a reader needs has to be inside it, not in the name of a
            directory they may not have. Spelled exactly as the report's own front matter spells
            its `generated`, because a reader comparing the two should not have to parse two
            formats. Injectable, so that a test's `summary.json` is byte-stable.
        results_dir: Where the run directories were read from.
        variants_dir: Where the answer keys were read from.
        taxonomy: Which taxonomy's control baselines were used.
        configurations: One score per configuration.
        unknown_variants: Runs whose variant carries no answer key.
    """

    generated: datetime
    results_dir: str
    variants_dir: str
    taxonomy: str
    configurations: dict[str, ConfigurationScore] = field(default_factory=dict)
    unknown_variants: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        """`summary.json`."""
        return {
            "schema_version": 1,
            "generated": stamp(self.generated),
            "results_dir": self.results_dir,
            "variants_dir": self.variants_dir,
            "taxonomy": self.taxonomy,
            "configurations": {
                name: item.to_payload() for name, item in sorted(self.configurations.items())
            },
            "variants_without_an_answer_key": list(self.unknown_variants),
        }


def stamp(moment: datetime) -> str:
    """Spell one instant the way the report's front matter spells `generated`: UTC, to the second.

    Args:
        moment: The instant, in any time zone.

    Returns:
        ISO-8601 in UTC with a `Z` suffix and no microseconds.
    """
    return moment.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _detects(run: RunDirectory, key: VariantKey, baseline: Baseline) -> bool:
    """Whether this run found what was planted, by `04` section 4's criterion.

    A finding of the seeded class at severity at least medium detects it, unless that class is one
    the subject's own clean control raises in this data mode -- in which case the finding has to
    cite an artifact the baseline's findings do not, or it is the baseline showing through rather
    than the seed being found. `T1` is additionally detected by a developer claim the matcher
    marked `mismatch`, a channel that exists only under `--data` (D-016).
    """
    if key.defect_class == DefectClass.T1.value and run.developer_mismatch:
        return True
    hits = [
        item
        for item in run.at_or_above(DETECTION_SEVERITY)
        if str(item["defect_class"]) == key.defect_class
    ]
    if not hits:
        return False
    if not baseline.measured or not any(cls == key.defect_class for cls, _ in baseline.classes):
        return True
    return any(
        run.artifact_names([str(h) for h in item.get("evidence", [])]) - baseline.evidence
        for item in hits
    )


def _blocked_by(run: RunDirectory, key: VariantKey) -> tuple[str, str] | None:
    """The check that would have screened for the seeded class and did not run, if there is one."""
    failed = run.checks_that_did_not_run
    for tool in _CLASS_TOOLS.get(key.defect_class or "", ()):
        if tool in failed:
            return tool, failed[tool]
    return None


def score(
    runs: Sequence[RunDirectory],
    keys: Mapping[str, VariantKey],
    baselines: Baselines,
    no_report: Sequence[NoReport] = (),
) -> dict[str, ConfigurationScore]:
    """Score every run, grouped by the configuration each one recorded.

    Args:
        runs: The run directories.
        keys: The answer keys, by variant id.
        baselines: The measured control baselines.
        no_report: Cells the ledger records as having produced no report. A seeded one counts
            against its configuration as a miss with no report, which is `docs/STUDY.md` section
            5's rule and the reason the ledger is read at all.

    Returns:
        One score per configuration.
    """
    scores: dict[str, ConfigurationScore] = {}
    for run in runs:
        key = keys.get(run.variant)
        if key is None:
            continue
        item = scores.setdefault(run.configuration, ConfigurationScore(run.configuration))
        item.runs += 1
        item.unevidenced += run.unevidenced
        if key.is_control:
            _score_control(item, run, key, baselines.for_control(key.variant, key.mode))
        else:
            _score_seeded(item, run, key, baselines.for_subject(key.subject, key.mode))
    for entry in no_report:
        item = scores.setdefault(entry.configuration, ConfigurationScore(entry.configuration))
        item.no_report.append(entry)
        key = keys.get(entry.variant)
        if key is None or key.is_control or key.defect_class is None:
            continue
        row = item.per_class.setdefault(key.defect_class, ClassScore())
        row.seeded += 1
        row.variants.append(key.variant)
        row.missed.append(key.variant)
        item.missed.append(key.variant)
    for item in scores.values():
        item.grounding = _grounding(
            [run for run in runs if run.configuration == item.configuration]
        )
    return scores


def _score_seeded(
    item: ConfigurationScore, run: RunDirectory, key: VariantKey, baseline: Baseline
) -> None:
    """Score one seeded variant: detection, then everything else it raised."""
    planted = str(key.defect_class)
    detected = _detects(run, key, baseline)
    blocked = None if detected else _blocked_by(run, key)
    if blocked is not None:
        item.not_scorable.append(
            {"variant": key.variant, "class": planted, "tool": blocked[0], "message": blocked[1]}
        )
    else:
        row = item.per_class.setdefault(planted, ClassScore())
        row.seeded += 1
        row.variants.append(key.variant)
        if detected:
            row.detected += 1
            item.detected.append(key.variant)
        else:
            row.missed.append(key.variant)
            item.missed.append(key.variant)
    for finding in run.at_or_above(DETECTION_SEVERITY):
        raised = str(finding["defect_class"])
        if raised == planted:
            continue
        item.collateral.append(judge_collateral(key, raised, str(finding["severity"]), baseline))


def _score_control(
    item: ConfigurationScore, run: RunDirectory, key: VariantKey, baseline: Baseline
) -> None:
    """Score one control: every finding the measured baseline does not carry is a false alarm."""
    if not baseline.measured:
        item.controls_unmeasured.append(key.variant)
        return
    for finding in run.at_or_above(DETECTION_SEVERITY):
        pair = (str(finding["defect_class"]), str(finding["severity"]))
        if pair in baseline.classes:
            continue
        item.false_alarms.append({"variant": key.variant, "class": pair[0], "severity": pair[1]})


def _grounding(runs: Sequence[RunDirectory]) -> dict[str, float | None]:
    """Mean and minimum grounding precision over a configuration's runs, pre- and post-repair."""
    out: dict[str, float | None] = {}
    for when in ("pre_repair", "post_repair"):
        values = [value for value in (run.grounding(when) for run in runs) if value is not None]
        out[f"{when}_mean"] = sum(values) / len(values) if values else None
        out[f"{when}_min"] = min(values) if values else None
    return out


def _lines(result: StudyScore) -> Iterator[str]:
    """The human summary, which says the same things `summary.json` does and fits on a screen."""
    for name, item in sorted(result.configurations.items()):
        scored = len(item.detected) + len(item.missed)
        yield (
            f"{name}: {len(item.detected)}/{scored} seeded variants detected "
            f"over {item.runs} run(s)"
        )
        for cls, row in sorted(item.per_class.items()):
            missed = f"; missed {', '.join(row.missed)}" if row.missed else ""
            yield f"  {cls}: {row.detected}/{row.seeded}{missed}"
        for gone in item.no_report:
            yield (
                f"  no report: {gone.variant} ({gone.status}) — counted as a miss; "
                f"{gone.reason[:90]}"
            )
        for skipped in item.not_scorable:
            yield (
                f"  not scored: {skipped['variant']} ({skipped['class']}) — "
                f"{skipped['tool']} did not run: {skipped['message']}"
            )
        yield (
            f"  false alarms {len(item.false_alarms)}, collateral spurious "
            f"{len(item.spurious)}, unevidenced {item.unevidenced}, precision "
            + ("n/a" if item.precision is None else f"{item.precision:.4f}")
        )
        for pending in item.unjudged:
            yield (
                f"  collateral unjudged: {pending.variant} raised {pending.defect_class} "
                f"{pending.severity} — docs/STUDY.md section 9 owes a dated judgement"
            )
        for control in item.controls_unmeasured:
            yield f"  false alarms not scored on {control}: its baseline is not measured"
        pre, post = item.grounding.get("pre_repair_mean"), item.grounding.get("post_repair_mean")
        if pre is not None and post is not None:
            yield f"  grounding precision mean {pre:.4f} pre-repair, {post:.4f} post-repair"
    if result.unknown_variants:
        yield f"no answer key for: {', '.join(result.unknown_variants)}"


def main(argv: Sequence[str] | None = None, *, generated: datetime | None = None) -> int:
    """Score a directory of runs and print the summary. Returns an exit code.

    Returns:
        `0` when every variant was scored and nothing is waiting on a person, `1` when something
        is: a run with no answer key, a variant set aside because its check did not run, a control
        whose baseline is not measured, a collateral pairing nobody has judged, or a cell that
        produced no report -- which is scored as a miss *and* is a thing to look at, because a
        renderer refusal is usually about this codebase rather than about the model. An ordinary
        **miss** is not one of these -- a miss is a result, and the study publishes it. Each of
        these five is homework, and none of them is a defect in the detector.
    """
    parser = argparse.ArgumentParser(
        prog="python eval/score.py",
        description="Score the seeded-defect study from its run directories.",
    )
    parser.add_argument("--results", type=Path, required=True, help="a directory of run dirs")
    parser.add_argument(
        "--variants", type=Path, required=True, help="where the SEED.yaml files are"
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=Path(__file__).resolve().parent / "taxonomy.yaml",
        help="where the measured control baselines are",
    )
    parser.add_argument("--out", type=Path, default=None, help="write summary.json here")
    args = parser.parse_args(list(argv) if argv is not None else None)

    runs = load_runs(args.results)
    keys = load_keys(args.variants)
    baselines = load_baselines(args.taxonomy)
    no_report = load_no_report(args.results)
    result = StudyScore(
        generated=generated or datetime.now(UTC),
        results_dir=str(args.results),
        variants_dir=str(args.variants),
        taxonomy=str(args.taxonomy),
        configurations=score(runs, keys, baselines, no_report),
        unknown_variants=sorted({run.variant for run in runs} - set(keys)),
    )
    for line in _lines(result):
        print(line)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result.to_payload(), indent=2) + "\n", encoding="utf-8")
        print(f"summary: {args.out}")
    owed = bool(result.unknown_variants) or any(
        item.controls_unmeasured or item.unjudged or item.not_scorable or item.no_report
        for item in result.configurations.values()
    )
    return 1 if owed else 0


if __name__ == "__main__":  # pragma: no cover - the module's command-line entry point
    sys.exit(main())
