"""The seeded-defect generator: subject + defect -> variant package.

`02-SPEC.md` section 5 and `04-SEEDED-DEFECT-STUDY.md` section 2. `seed()` copies a subject
package, applies one recipe from `eval/taxonomy.yaml` to it, and writes `SEED.yaml` beside the
copy. A recipe operates on the package as a model developer would have: it patches `code/`, it
changes the data-building step inside the subject's own entrypoint, or it edits `package.yaml`.
Nothing here writes a data file, and nothing here runs a model.

**`SEED.yaml` is the answer key and the pipeline never reads it.** `quaestor.package.loader` opens
`package.yaml` and nothing else; `tests/test_seed.py` plants a poison value in a variant's
`SEED.yaml`, validates that variant end to end and asserts the value reaches no trace event, no
artifact, no claim and no line of `report.md`.

This module lives in `eval/` rather than in `src/quaestor/` on purpose, and the reason is the same
one: the thing being measured must not be able to import the thing that plants the defects. It is
a development tool that only makes sense inside a checkout -- it reads `subjects/`, it writes a
gitignored tree -- so `quaestor study build` loads it from beside the taxonomy it was given
(DECISIONS D-127).

Every recipe is a text patch with a named anchor, and an anchor that is not found is an error
rather than a silent no-op: a seeded-defect generator that quietly seeds nothing would put a
guaranteed miss in the study and blame the detector for it.

**Data modes.** A recipe is the same patch in both modes, because every one of them hangs off the
seam *after* the subject has chosen where its rows come from, or only edits `package.yaml`. Four
recipes are the exception -- they need a *column* the real sample does not carry -- and under
`--data` they are skipped by name, with their reason, rather than built into packages that cannot
run (`SYNTHETIC_ONLY_RECIPES`, D-137 as amended).
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

from quaestor.package import ModelPackage, load_package

__all__ = [
    "CONTROL_STATUS",
    "DROPPED_STATUS",
    "RECIPES",
    "SEED_FILE",
    "SEEDED_STATUS",
    "SYNTHETIC_ONLY_RECIPES",
    "DefectSpec",
    "Taxonomy",
    "Variant",
    "build_all",
    "directory_digest",
    "load_taxonomy",
    "main",
    "seed",
]

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
"""The checkout this file lives in; `subjects/` and `eval/taxonomy.yaml` are found from it."""

TAXONOMY_PATH: Final = REPO_ROOT / "eval" / "taxonomy.yaml"
SUBJECTS_DIR: Final = REPO_ROOT / "subjects"

SEED_FILE: Final = "SEED.yaml"
"""The provenance file every variant carries and no code path in `quaestor` opens."""

SEEDED_STATUS: Final = "seeded"
CONTROL_STATUS: Final = "control"
DROPPED_STATUS: Final = "dropped"
"""A taxonomy row marked `status: dropped` is recorded and not built (`04` section 2)."""

RECIPE_SEED: Final = 20260910
"""The one seed every recipe draws from, so a variant is byte-identical on every rebuild.

It is deliberately *not* the subject's declared 20260901: a recipe's own draw -- which test rows
to copy, which to blank -- must not be a function of the same stream that drew the panel, or a
change to the panel size would silently re-select the defect as well.
"""

_SKIP_NAMES: Final = ("__pycache__", ".DS_Store", SEED_FILE)
_SKIP_SUFFIXES: Final = (".pyc", ".pyo")
"""What is never copied into a variant: caches, and any answer key the source happens to carry."""

_MAIN_GUARD: Final = 'if __name__ == "__main__":'
"""Where a subject's entrypoint stops being definitions and starts being a program."""

SYNTHETIC_MODE: Final = "synthetic"
REAL_MODE: Final = "real"
"""What `SEED.yaml`'s `mode:` says, and the key a control's baseline is measured under."""

SYNTHETIC_ONLY_RECIPES: Final[Mapping[str, str]] = {
    "add_post_outcome_feature": (
        "needs a pay_amt_next column the real sample does not carry, and the synthetic "
        "construction reads the generating process's latent margin (D-132), which a real panel "
        "has none of"
    ),
    "end_of_month_balance": (
        "patches build_panel, which a --data run never calls: sample_freddie.py builds the panel "
        "and code/run.py reads back the four split files it wrote"
    ),
    "regime_sign_flip": "needs an application_cohort column the real sample does not carry",
    "reintroduce_collinear": (
        "needs bill_last_adj, computed by the patched engineer from the raw statement schema that "
        "--data mode never sees"
    ),
}
"""The four recipes that cannot be applied to a real data directory, and why (D-137, amended).

D-137 named five *variants*; they are four *recipes*, because both `credit__L1` arms run
`add_post_outcome_feature`. Each needs a column the real sample does not have, and a column is
built by `sample.py` and `sample_freddie.py` rather than by a recipe. The amendment of 2026-09-17
replaces the recorded fix -- an edit to the samplers -- with a transform on the delivered split
files, which is testable offline where a sampler edit is not; that transform is the cut list's
cut 3 and is not in this commit, so under `--data` these four rows are skipped and said so.
"""


@dataclass(frozen=True)
class DefectSpec:
    """One row of `eval/taxonomy.yaml`: which class, which recipe, which parameters.

    A control is a `DefectSpec` too, with `defect_class` `None` and `status` `control`: the study
    scores it in the same loop and the only difference is what is expected of it.
    """

    id: str
    subject: str
    recipe: str
    defect_class: str | None = None
    params: Mapping[str, Any] = field(default_factory=dict)
    expected_signal: str | None = None
    met_where: str | None = None
    status: str = SEEDED_STATUS
    dropped_reason: str | None = None
    baseline: Mapping[str, list[Mapping[str, Any]] | None] | None = None
    """What this control raises before any seed, per data mode, measured rather than expected.

    Controls only: a seeded row's baseline is `None`, because the question a baseline answers --
    what does this package raise with nothing wrong with it -- is a question about a control.
    Keyed by data mode (`synthetic`, `real`); a mode's value is a list of finding descriptions, or
    `None` where the baseline has not been measured yet (DECISIONS D-161). Nothing here reaches
    `SEED.yaml`: it is the scorer's input, and `eval/score.py` reads it in Phase 12.
    """

    @property
    def is_control(self) -> bool:
        """Whether this row is one of the four clean or harmlessly perturbed controls."""
        return self.status == CONTROL_STATUS

    @property
    def is_dropped(self) -> bool:
        """Whether the taxonomy marks this recipe as one that could not produce its signal."""
        return self.status == DROPPED_STATUS


@dataclass(frozen=True)
class Taxonomy:
    """`eval/taxonomy.yaml` as loaded: the study block, the controls and the seeded defects."""

    path: Path
    version: int
    subjects: list[str]
    variants: int
    seed: int
    specs: list[DefectSpec]

    @property
    def buildable(self) -> list[DefectSpec]:
        """The rows `study build` writes: everything not marked `status: dropped`."""
        return [spec for spec in self.specs if not spec.is_dropped]

    @property
    def dropped(self) -> list[DefectSpec]:
        """The rows a recipe could not be made to fire on, with their reasons."""
        return [spec for spec in self.specs if spec.is_dropped]

    def digest(self) -> str:
        """SHA-256 of the taxonomy file, recorded in every `SEED.yaml` it produced."""
        return hashlib.sha256(self.path.read_bytes()).hexdigest()


def _baseline(raw: Any) -> Mapping[str, list[Mapping[str, Any]] | None] | None:
    """Read a control row's `baseline` block, which is absent, `null`, or a map by data mode.

    Args:
        raw: Whatever the row carried under `baseline`.

    Returns:
        The block as a plain mapping, or `None` when the row declares none.
    """
    if raw is None:
        return None
    return {
        str(mode): None if rows is None else [dict(row) for row in rows]
        for mode, rows in raw.items()
    }


def load_taxonomy(path: Path | str = TAXONOMY_PATH) -> Taxonomy:
    """Read `eval/taxonomy.yaml` into controls and defects, in file order.

    Args:
        path: The taxonomy file.

    Returns:
        The parsed taxonomy.

    Raises:
        ValueError: A row names a recipe this module does not implement, an id repeats, or a
            seeded row is missing the class, the expected signal or the `met_where` sentence --
            each of which the study reads and none of which has a default.
    """
    resolved = Path(path)
    raw = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    study = raw.get("study") or {}
    specs: list[DefectSpec] = []
    for row in raw.get("controls") or []:
        specs.append(
            DefectSpec(
                id=str(row["id"]),
                subject=str(row["subject"]),
                recipe=str(row["recipe"]),
                params=dict(row.get("params") or {}),
                status=str(row.get("status", CONTROL_STATUS)),
                dropped_reason=row.get("dropped_reason"),
                baseline=_baseline(row.get("baseline")),
            )
        )
    for row in raw.get("defects") or []:
        status = str(row.get("status", SEEDED_STATUS))
        for key in ("class", "expected_signal", "met_where"):
            if not row.get(key):
                raise ValueError(f"taxonomy row {row.get('id')!r} has no {key!r}")
        specs.append(
            DefectSpec(
                id=str(row["id"]),
                subject=str(row["subject"]),
                recipe=str(row["recipe"]),
                defect_class=str(row["class"]),
                params=dict(row.get("params") or {}),
                expected_signal=str(row["expected_signal"]),
                met_where=str(row["met_where"]),
                status=status,
                dropped_reason=row.get("dropped_reason"),
            )
        )
    seen: set[str] = set()
    for spec in specs:
        if spec.id in seen:
            raise ValueError(f"taxonomy declares the variant id {spec.id!r} twice")
        seen.add(spec.id)
        if spec.recipe not in RECIPES:
            raise ValueError(
                f"taxonomy row {spec.id!r} names the recipe {spec.recipe!r}, which eval/seed.py "
                f"does not implement; it implements {sorted(RECIPES)}"
            )
        if spec.is_dropped and not spec.dropped_reason:
            raise ValueError(f"taxonomy row {spec.id!r} is dropped with no dropped_reason")
    return Taxonomy(
        path=resolved,
        version=int(raw.get("version", 1)),
        subjects=list(raw.get("subjects") or []),
        variants=int(study.get("variants", 0)),
        seed=int(study.get("seed", 0)),
        specs=specs,
    )


class Variant:
    """A copied subject package being patched, and the record of what was done to it.

    Every edit goes through :meth:`replace`, :meth:`append` or :meth:`edit_package`, each of which
    appends one sentence to :attr:`notes`. Those sentences are what `SEED.yaml` publishes as
    `applied:`, so a reader of a variant can see the whole of the change without diffing it.
    """

    def __init__(self, root: Path, name: str | None = None) -> None:
        """Wrap a copied package directory.

        Args:
            root: The variant package's own directory.
            name: What to call the variant in the files it writes; the directory's name by
                default. It is a parameter so that a variant's bytes do not depend on where it
                was written, which is what makes building the same recipe twice idempotent.
        """
        self.root = root
        self.name = name or root.name
        self.notes: list[str] = []

    def read(self, relative: str) -> str:
        """Return one file of the variant as text."""
        return (self.root / relative).read_text(encoding="utf-8")

    def write(self, relative: str, text: str) -> None:
        """Write one file of the variant as text, with a trailing newline."""
        (self.root / relative).write_text(text if text.endswith("\n") else text + "\n", "utf-8")

    def replace(self, relative: str, old: str, new: str, *, note: str, count: int = 1) -> None:
        """Replace an anchor in one file, insisting it appears exactly `count` times.

        Args:
            relative: The file, relative to the package root.
            old: The anchor text.
            new: What replaces it.
            note: The sentence `SEED.yaml` records for this edit.
            count: How many occurrences the anchor must have.

        Raises:
            ValueError: The anchor appears a different number of times, which means the subject
                moved and the recipe would otherwise have seeded nothing.
        """
        text = self.read(relative)
        found = text.count(old)
        if found != count:
            raise ValueError(
                f"the recipe's anchor appears {found} time(s) in {relative} of "
                f"{self.name}, not {count}; the anchor is {old!r}"
            )
        self.write(relative, text.replace(old, new))
        self.notes.append(f"{relative}: {note}")

    def append(self, relative: str, text: str, *, note: str) -> None:
        """Add a block to one file of the variant, before its command-line guard if it has one.

        A subject's entrypoint ends with ``if __name__ == "__main__": sys.exit(main())``, and a
        definition written after that line does not exist when ``python -m code.run`` reaches it.
        So a block goes above the guard where there is one and at the end of the file where there
        is not, and a file with more than one guard is an error rather than a guess.
        """
        text = text.strip("\n") + "\n"
        body = self.read(relative)
        if body.count(_MAIN_GUARD) > 1:
            raise ValueError(f"{relative} of {self.name} has more than one main guard")
        if _MAIN_GUARD in body:
            head, _, tail = body.partition(_MAIN_GUARD)
            body = head.rstrip("\n") + "\n\n\n" + text + "\n" + _MAIN_GUARD + tail
        else:
            body = body.rstrip("\n") + "\n\n" + text
        self.write(relative, body)
        self.notes.append(f"{relative}: {note}")

    def package_yaml(self) -> dict[str, Any]:
        """Return `package.yaml` as a mapping, in file order."""
        loaded = yaml.safe_load(self.read("package.yaml"))
        assert isinstance(loaded, dict)
        return loaded

    def edit_package(self, edit: Callable[[dict[str, Any]], str]) -> None:
        """Apply one edit to `package.yaml` and rewrite it.

        The rewrite is a `yaml.safe_dump`, so the subject's comments do not survive it. That is
        deliberate: a variant is a generated artefact that is never committed, and a comment
        carried forward from the clean subject onto a line the recipe has changed would be a lie
        in the one file a reader of the variant trusts. The header written here says what the
        file is and points at `SEED.yaml`.

        Args:
            edit: Mutates the mapping in place and returns the sentence to record.
        """
        data = self.package_yaml()
        note = edit(data)
        header = (
            f"# package.yaml of the seeded variant {self.name}, written by eval/seed.py.\n"
            f"# The clean subject's comments are not carried over; SEED.yaml, beside this file,\n"
            f"# records the recipe and its parameters and is never read by quaestor.\n"
        )
        body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
        self.write("package.yaml", header + body)
        self.notes.append(f"package.yaml: {note}")


def _copyable(root: Path) -> Iterator[Path]:
    """Yield every file of a subject package that a variant gets a copy of, sorted."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(root).parts)
        if parts & set(_SKIP_NAMES) or path.suffix in _SKIP_SUFFIXES:
            continue
        yield path


def directory_digest(root: Path) -> str:
    """Return a SHA-256 over a directory's file names and contents, ignoring times.

    Used by the idempotence test: building a variant twice must give the same digest, which is
    what spec section 5's "applying a recipe twice is idempotent" means for a tree.
    """
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


# --------------------------------------------------------------------------------------------
# Seams. Both subjects have one place where the data-building step has finished and the model has
# not started: the classifier's `splits = {...}` line and the hazard subject's. Every recipe that
# transforms the data hangs off that line, so a variant's diff is one call plus one function.
# --------------------------------------------------------------------------------------------

_CREDIT_SEAM: Final = '    splits = {"train": train_ids, "test": test_ids}'
_MSR_SEAM: Final = "    splits = {\n        name: Split("


def _credit_seam(variant: Variant, body: str, note: str) -> None:
    """Insert a `_seeded` call before the classifier's split assembly and define the function."""
    variant.replace(
        "code/run.py",
        _CREDIT_SEAM,
        "    frame, train_ids, test_ids = _seeded(frame, train_ids, test_ids)\n" + _CREDIT_SEAM,
        note="the data-building step is passed through the seeded transform",
    )
    variant.append("code/run.py", body, note=note)


def _msr_seam(variant: Variant, body: str, note: str) -> None:
    """Insert a `_seeded` call before the hazard subject's split assembly and define it."""
    variant.replace(
        "code/run.py",
        _MSR_SEAM,
        "    panel, masks = _seeded(panel, masks)\n" + _MSR_SEAM,
        note="the panel and its split masks are passed through the seeded transform",
    )
    variant.append("code/run.py", body, note=note)


def _feature_entry(
    data: dict[str, Any], name: str, timing: str, note: str, after: str | None = None
) -> None:
    """Insert one feature declaration into `package.yaml`, after a named feature or at the end."""
    entry: dict[str, Any] = {"name": name, "timing": timing, "note": note}
    features: list[dict[str, Any]] = data["features"]
    position = len(features)
    if after is not None:
        position = next(i for i, f in enumerate(features) if f["name"] == after) + 1
    features.insert(position, entry)


# --------------------------------------------------------------------------------------------
# L1 -- target leakage
# --------------------------------------------------------------------------------------------

_POST_OUTCOME_BODY = '''
POST_OUTCOME_TEMPERATURE = 0.25
"""How sharply the month t+1 payment collapses as the latent margin crosses zero.

A quarter of a margin unit, so a client one unit into distress pays about two per cent of their
usual amount and one unit clear of it pays essentially all of it. That is what the payment
received *after* the account has gone bad looks like: near zero, not merely reduced."""

POST_OUTCOME_NOISE_SD = 0.35
"""Multiplicative lognormal noise on the payment, so the leak is strong and not invertible."""


def _post_outcome_payment(rng, bills, pay_ratio, margin):
    """The payment received in the month *after* the observation window.

    Derived from the latent margin of the same logistic draw the outcome is a threshold of --
    `default_next_month` is `margin > 0` -- and not from the outcome column itself, so a client
    deep in distress pays almost nothing while a comfortable one pays their usual amount, and the
    two columns are not recoverable from one another. Drawn after the target so that every other
    column of the panel is the clean control's, value for value.
    """
    usual = bills[:, 0] * pay_ratio
    paying = _sigmoid(-margin / POST_OUTCOME_TEMPERATURE)
    noise = np.exp(rng.normal(0.0, POST_OUTCOME_NOISE_SD, margin.size))
    return np.round(np.maximum(usual * paying * noise, 0.0), 2)
'''


def _recipe_add_post_outcome_feature(variant: Variant, spec: DefectSpec) -> None:
    """Add a feature observed after the outcome, declared honestly or dishonestly."""
    name = str(spec.params.get("feature", "pay_amt_next"))
    timing = str(spec.params.get("declared_timing", "after_outcome"))
    variant.replace(
        "code/synthetic.py",
        "    target = (rng.random(n) < probability).astype(int)",
        "    draw = np.clip(rng.random(n), 1e-12, 1.0 - 1e-12)\n"
        "    target = (draw < probability).astype(int)\n"
        "    margin = intercept + drivers - np.log(draw / (1.0 - draw))",
        note="the logistic draw keeps its latent margin, of which the outcome is the sign",
    )
    variant.replace(
        "code/synthetic.py",
        "    frame[TARGET_COLUMN] = target\n    return frame",
        f'    frame["{name}"] = _post_outcome_payment(rng, bills, pay_ratio, margin)\n'
        "    frame[TARGET_COLUMN] = target\n    return frame",
        note=f"{name} is drawn from the latent margin, after the outcome",
    )
    variant.append("code/synthetic.py", _POST_OUTCOME_BODY, note="the payment's own draw")
    variant.replace(
        "code/features.py",
        '    + [f"delinq_{i}" for i in range(1, N_STATEMENTS + 1)]\n)',
        f'    + [f"delinq_{{i}}" for i in range(1, N_STATEMENTS + 1)]\n    + ["{name}"]\n)',
        note=f"{name} joins the raw statement schema",
    )
    variant.replace(
        "code/features.py",
        '    "bill_trend_6m",\n]',
        f'    "bill_trend_6m",\n    "{name}",\n]',
        note=f"{name} joins the declared feature list",
    )
    variant.replace(
        "code/features.py",
        '    "bill_trend_6m": "before_period_start",\n}',
        f'    "bill_trend_6m": "before_period_start",\n    "{name}": "{timing}",\n}}',
        note=f"{name} is declared {timing} in features.json",
    )
    variant.replace(
        "code/features.py",
        '            "bill_trend_6m": _trend(bills),\n        }',
        f'            "bill_trend_6m": _trend(bills),\n'
        f'            "{name}": raw["{name}"].to_numpy(dtype=float),\n        }}',
        note=f"{name} is passed through the engineering step unchanged",
    )
    variant.edit_package(
        lambda data: (
            _feature_entry(
                data,
                name,
                timing,
                "payment received in the month after the observation month",
            )
            or f"{name} is declared as a feature with timing {timing}"
        )
    )


def _recipe_end_of_month_balance(variant: Variant, spec: DefectSpec) -> None:
    """Point the hazard subject's beginning-of-month balance at the *closing* balance."""
    del spec
    variant.replace(
        "code/features.py",
        '            "bom_balance_log": np.log(\n'
        "                np.maximum(previous_balance[keep].to_numpy(dtype=float), BALANCE_FLOOR)\n"
        "            ),",
        '            "bom_balance_log": np.log(\n'
        '                np.maximum(kept["eom_balance"].to_numpy(dtype=float), BALANCE_FLOOR)\n'
        "            ),",
        note="bom_balance_log is read from the closing balance of month t, not month t-1",
    )
    variant.edit_package(
        lambda data: (
            _renote(
                data,
                "bom_balance_log",
                "log of unpaid balance at the beginning of month t (prior month close)",
            )
            or "the bom_balance_log note keeps the declaration the code no longer honours"
        )
    )


def _renote(data: dict[str, Any], name: str, note: str) -> None:
    """Set one declared feature's note, leaving the declaration itself alone."""
    for feature in data["features"]:
        if feature["name"] == name:
            feature["note"] = note
            return
    raise ValueError(f"package.yaml declares no feature named {name!r}")


# --------------------------------------------------------------------------------------------
# L2 -- train/test contamination
# --------------------------------------------------------------------------------------------

_CREDIT_CONTAMINATION = '''
CONTAMINATION_FRACTION = {fraction!r}
"""What share of the held-out clients is copied back into the fitting split."""

CONTAMINATION_SEED = {seed}


def _seeded(frame, train_ids, test_ids):
    """Copy a share of the test rows into train, re-keyed with client ids of their own.

    This is the re-issued-account instance: the holdout was drawn after de-duplicating on account
    id, and the same customer came back under a new id. The identifier screen cannot see it and
    the feature-vector screen can, which is the arm the study is testing.
    """
    rng = np.random.default_rng(CONTAMINATION_SEED)
    held = np.sort(test_ids.ids)
    n_copy = max(int(round(CONTAMINATION_FRACTION * held.size)), 1)
    chosen = np.sort(rng.choice(held, size=n_copy, replace=False))
    copied = frame[np.isin(frame[ID_COLUMN].to_numpy(), chosen)].copy()
    base = int(frame[ID_COLUMN].to_numpy().max()) + 1
    copied[ID_COLUMN] = np.arange(base, base + len(copied), dtype=np.int64)
    grown = pd.concat([frame, copied], ignore_index=True)
    fitted = np.sort(np.concatenate([train_ids.ids, copied[ID_COLUMN].to_numpy()]))
    return grown, Split("train", fitted), test_ids
'''

_MSR_CONTAMINATION = '''
CONTAMINATION_FRACTION = {fraction!r}
"""What share of the held-out loan-months is copied back into the fitting split."""

CONTAMINATION_SEED = {seed}


def _seeded(panel, masks):
    """Copy a share of the test loan-months into train under loan ids of their own."""
    rng = np.random.default_rng(CONTAMINATION_SEED)
    positions = np.flatnonzero(masks["test"])
    n_copy = max(int(round(CONTAMINATION_FRACTION * positions.size)), 1)
    chosen = np.sort(rng.choice(positions, size=n_copy, replace=False))
    copied = panel.iloc[chosen].copy()
    base = int(panel[ID_COLUMN].to_numpy().max()) + 1
    copied[ID_COLUMN] = np.arange(base, base + len(copied), dtype=np.int64)
    grown = pd.concat([panel, copied], ignore_index=True)
    grown_masks = {{}}
    for name, mask in masks.items():
        extra = np.full(len(copied), name == "train", dtype=bool)
        grown_masks[name] = np.concatenate([mask, extra])
    return grown, grown_masks
'''


def _recipe_duplicate_test_into_train(variant: Variant, spec: DefectSpec) -> None:
    """Copy a share of the held-out rows into the fitting split, re-keyed."""
    fraction = float(spec.params.get("fraction", 0.03))
    fresh = bool(spec.params.get("fresh_ids", True))
    if not fresh:
        raise ValueError(
            f"{spec.id}: this recipe implements the re-keyed arm only (fresh_ids: true); the "
            "identifier arm would need a second body and the taxonomy asks for neither"
        )
    template = _CREDIT_CONTAMINATION if spec.subject == "credit_default" else _MSR_CONTAMINATION
    body = template.format(fraction=fraction, seed=RECIPE_SEED)
    note = f"{fraction:.1%} of the held-out rows are copied into train under new identifiers"
    if spec.subject == "credit_default":
        _credit_seam(variant, body, note)
    else:
        _msr_seam(variant, body, note)


# --------------------------------------------------------------------------------------------
# R1 -- a regime-dependent feature
# --------------------------------------------------------------------------------------------

_REGIME_FLIP_BODY = '''
REGIME_COLUMN = "{column}"
"""The application cohort the variant declares as `regime.column`."""

REGIME_LEVELS = {levels!r}
"""Two cohorts, assigned by client index so that the panel's own draws do not move."""

REGIME_FLIP_FEATURE = "{feature}"
REGIME_FLIP_BETA = {beta!r}
"""The log-odds effect of the standardised statement trend, positive in one cohort and negative
in the other. The pooled fit averages the two into a coefficient near zero, which is the whole
shape of the defect: the champion looks stable and is not."""


def _application_cohort(n):
    """Assign the two cohorts by client index: deterministic, balanced, and rng-free."""
    return np.where(np.arange(n) % 2 == 0, REGIME_LEVELS[0], REGIME_LEVELS[1])


def _regime_flip(bills, cohort):
    """Return the cohort-dependent contribution of the statement trend to the log odds."""
    months = np.arange(N_STATEMENTS, dtype=float)
    centred = months - months.mean()
    trend = (bills[:, ::-1] * centred).sum(axis=1) / float((centred**2).sum())
    spread = float(trend.std())
    standardised = (trend - float(trend.mean())) / (spread if spread > 0.0 else 1.0)
    sign = np.where(cohort == REGIME_LEVELS[0], 1.0, -1.0)
    return REGIME_FLIP_BETA * sign * standardised
'''


def _recipe_regime_sign_flip(variant: Variant, spec: DefectSpec) -> None:
    """Write a two-level cohort into the panel and reverse one feature's sign on one cohort."""
    column = str(spec.params.get("regime_column", "application_cohort"))
    feature = str(spec.params.get("feature", "bill_trend_6m"))
    levels = list(spec.params.get("levels", ["2013", "2016"]))
    beta = float(spec.params.get("beta", 1.10))
    variant.append(
        "code/synthetic.py",
        _REGIME_FLIP_BODY.format(column=column, levels=levels, feature=feature, beta=beta),
        note=f"the cohort and the sign-flipping contribution of {feature}",
    )
    variant.replace(
        "code/synthetic.py",
        "    intercept = _solve_intercept(drivers, process)",
        "    cohort = _application_cohort(n)\n"
        "    drivers = drivers + _regime_flip(bills, cohort)\n"
        "    intercept = _solve_intercept(drivers, process)",
        note=f"{feature}'s effect enters the process with opposite signs by cohort",
    )
    variant.replace(
        "code/synthetic.py",
        "    frame[TARGET_COLUMN] = target\n    return frame[[*RAW_COLUMNS, TARGET_COLUMN]]",
        "    frame[REGIME_COLUMN] = cohort\n"
        "    frame[TARGET_COLUMN] = target\n"
        "    return frame[[*RAW_COLUMNS, REGIME_COLUMN, TARGET_COLUMN]]",
        note=f"{column} is written beside the raw statement schema",
    )
    variant.replace(
        "code/features.py",
        "    if TARGET_COLUMN in raw.columns:",
        f'    if "{column}" in raw.columns:\n'
        f'        engineered["{column}"] = raw["{column}"].to_numpy()\n'
        "    if TARGET_COLUMN in raw.columns:",
        note=f"{column} is carried through the engineering step as a non-feature column",
    )
    variant.replace(
        "code/run.py",
        '        _write_csv(out_dir / f"data_{name}.csv", '
        "part[[ID_COLUMN, *retained, TARGET_COLUMN]])",
        "        _write_csv(\n"
        '            out_dir / f"data_{name}.csv",\n'
        f'            part[[ID_COLUMN, *retained, "{column}", TARGET_COLUMN]],\n'
        "        )",
        note=f"{column} is written into data_<split>.csv beside the features",
    )
    variant.edit_package(
        lambda data: (
            data.__setitem__("regime", {"column": column})
            or f"regime.column is declared as {column}"
        )
    )


# --------------------------------------------------------------------------------------------
# C1 -- miscalibration
# --------------------------------------------------------------------------------------------

_SMOTE_BODY = '''
SMOTE_RATIO = {ratio!r}
"""The minority-to-majority ratio the resampling targets; 1.0 is parity."""

SMOTE_NEIGHBOURS = 5
SMOTE_SEED = {seed}


def _smote(matrix, target):
    """Synthetic Minority Over-sampling, written out rather than imported.

    `imbalanced-learn` is not a dependency of this repository and adding one to a seeded variant
    would make the variant harder to run than the subject it came from, so the five lines of
    Chawla et al. (2002) are here: pick a minority row, pick one of its k minority neighbours,
    and take a uniform point on the segment between them. The champion is then fitted on the
    balanced matrix and its probabilities are reported as they come out, with no mapping back to
    the base rate -- which is the defect.
    """
    minority = matrix[target == 1]
    wanted = int(round(SMOTE_RATIO * float((target == 0).sum()))) - minority.shape[0]
    if wanted <= 0 or minority.shape[0] <= SMOTE_NEIGHBOURS:
        return matrix, target
    rng = np.random.default_rng(SMOTE_SEED)
    neighbours = NearestNeighbors(n_neighbors=SMOTE_NEIGHBOURS + 1).fit(minority)
    _, index = neighbours.kneighbors(minority)
    base = rng.integers(0, minority.shape[0], wanted)
    pick = index[base, 1 + rng.integers(0, SMOTE_NEIGHBOURS, wanted)]
    step = rng.random((wanted, matrix.shape[1]))
    drawn = minority[base] + step * (minority[pick] - minority[base])
    return (
        np.vstack([matrix, drawn]),
        np.concatenate([target, np.ones(wanted, dtype=int)]),
    )
'''


def _recipe_smote_no_recalibration(variant: Variant, spec: DefectSpec) -> None:
    """Fit the classifier on a SMOTE-balanced training matrix and report raw probabilities."""
    ratio = float(spec.params.get("ratio", 1.0))
    variant.replace(
        "code/run.py",
        "from sklearn.metrics import log_loss, roc_auc_score",
        "from sklearn.metrics import log_loss, roc_auc_score\n"
        "from sklearn.neighbors import NearestNeighbors",
        note="NearestNeighbors is imported for the hand-written resampling",
    )
    variant.replace(
        "code/run.py",
        "    ).fit(matrix.loc[train_mask, retained], frame.loc[train_mask, TARGET_COLUMN])",
        "    ).fit(*_resampled(matrix.loc[train_mask, retained], "
        "frame.loc[train_mask, TARGET_COLUMN]))",
        note="the champion is fitted on the resampled training matrix",
    )
    variant.append(
        "code/run.py",
        _SMOTE_BODY.format(ratio=ratio, seed=RECIPE_SEED)
        + '''

def _resampled(design, target):
    """Return the balanced fitting matrix, as a frame so the column names survive."""
    values, labels = _smote(design.to_numpy(dtype=float), target.to_numpy(dtype=int))
    return pd.DataFrame(values, columns=list(design.columns)), labels
''',
        note="the hand-written SMOTE and the frame it hands the pipeline",
    )


_OVERSAMPLE_BODY = '''
OVERSAMPLE_FACTOR = {factor}
"""How many times each prepayment event is repeated in the fitting matrix."""


def _oversampled(rows, target):
    """Repeat every prepaid loan-month `OVERSAMPLE_FACTOR` times in the fit and nowhere else.

    The hazard the champion learns is therefore about five times the hazard the book actually
    runs at, and nothing maps it back: the reported monthly probabilities are the resampled
    ones. The split files and the predictions are the panel's own rows, so the defect is a
    calibration defect and not a data defect.
    """
    events = rows[target[rows] == 1]
    return np.sort(np.concatenate([rows] + [events] * (OVERSAMPLE_FACTOR - 1)))
'''


def _recipe_oversample_events(variant: Variant, spec: DefectSpec) -> None:
    """Repeat the hazard subject's events in the fit and report the raw hazards."""
    factor = int(spec.params.get("factor", 5))
    variant.replace(
        "code/run.py",
        "    ).fit(design[train_mask], panel.loc[train_mask, TARGET_COLUMN])",
        "    ).fit(design[_fit_rows], panel[TARGET_COLUMN].to_numpy(dtype=int)[_fit_rows])",
        note="the champion is fitted on the over-sampled rows",
    )
    variant.replace(
        "code/run.py",
        "    champion = Pipeline(",
        "    _fit_rows = _oversampled(\n"
        "        np.flatnonzero(train_mask), panel[TARGET_COLUMN].to_numpy(dtype=int)\n"
        "    )\n"
        "    champion = Pipeline(",
        note=f"the fitting rows repeat every event {factor} times",
    )
    variant.append("code/run.py", _OVERSAMPLE_BODY.format(factor=factor), note="the resampling")


# --------------------------------------------------------------------------------------------
# S1 -- population shift
# --------------------------------------------------------------------------------------------

_SEGMENT_BODY = '''
SEGMENT_COLUMN = "{column}"
SEGMENT_RULE = "{rule}"
"""The champion is fitted on one half of the book and scores all of it.

`below_median` is `<= median` and `above_median` is `> median`, the partition Quaestor's own
sub-population rule uses, so the segment named here and the segment a reader would compute from
the same words are the same rows.
"""


def _seeded(frame, train_ids, test_ids):
    """Keep only the segment's clients in the fitting split; the held-out split is untouched."""
    values = frame.set_index(ID_COLUMN)[SEGMENT_COLUMN]
    median = float(values.median())
    inside = values <= median if SEGMENT_RULE == "below_median" else values > median
    kept = np.sort(np.asarray([i for i in train_ids.ids if bool(inside.loc[i])]))
    return frame, Split("train", kept), test_ids
'''


def _recipe_train_on_segment(variant: Variant, spec: DefectSpec) -> None:
    """Fit the classifier on one half of the book and score the whole of it."""
    column = str(spec.params.get("column", "limit_bal"))
    rule = str(spec.params.get("rule", "below_median"))
    if rule not in {"below_median", "above_median"}:
        raise ValueError(f"{spec.id}: rule {rule!r} is not below_median or above_median")
    _credit_seam(
        variant,
        _SEGMENT_BODY.format(column=column, rule=rule),
        note=f"the fitting split is narrowed to {column} {rule}, and every client is scored",
    )


_PRE_POST_BODY = '''
TRAIN_VINTAGE = {train_vintage}
"""The one origination year the champion is fitted on."""

TEST_FROM_PERIOD = {test_from}
"""The first month of the held-out split: the refinancing wave the training window never sees."""


def _seeded(panel, masks):
    """Re-cut train and test by calendar time, leaving the two period splits as declared.

    This rewrites which rows `splits.json` calls what and nothing else -- the panel, the features
    and the lagging are the clean subject's. The shift therefore lands on the *train-to-test*
    comparison, which is the one Quaestor tests (D-046); the same shift written as an
    out-of-time split would be reported and not tested, and the recipe would be a guaranteed miss.
    """
    years = origination_year(panel["orig_period"].to_numpy())
    periods = panel[TIME_COLUMN].to_numpy(dtype=np.int64)
    early = periods <= PERIOD_CUT
    return panel, {{
        "train": (years == TRAIN_VINTAGE) & early,
        "test": np.isin(years, TRAIN_VINTAGES) & (periods >= TEST_FROM_PERIOD),
        "out_of_time": masks["out_of_time"],
        "vintage_holdout": masks["vintage_holdout"],
    }}
'''


def _recipe_train_pre_test_post(variant: Variant, spec: DefectSpec) -> None:
    """Re-cut the hazard subject's train and test splits by calendar time."""
    train = dict(spec.params.get("train") or {})
    test = dict(spec.params.get("test") or {})
    vintages = list(train.get("vintages") or [2014])
    through = str(train.get("periods_through", "2019-12"))
    start = str(test.get("periods_from", "2020-01"))
    if len(vintages) != 1:
        raise ValueError(f"{spec.id}: this recipe fits one vintage, not {vintages}")
    if through.replace("-", "") != "201912":
        raise ValueError(
            f"{spec.id}: periods_through is {through!r}, but the subject's own PERIOD_CUT is "
            "201912 and the recipe reuses it rather than declaring a second cut"
        )
    variant.replace(
        "code/run.py",
        "from .features import (\n    BURNOUT_MONTHS,",
        "from .features import (\n    BURNOUT_MONTHS,\n    PERIOD_CUT,\n    TRAIN_VINTAGES,",
        note="the split rule's own constants are imported",
    )
    variant.replace(
        "code/run.py",
        "    design_matrix,\n    rows_hash,",
        "    design_matrix,\n    origination_year,\n    rows_hash,",
        note="origination_year is imported for the re-cut",
    )
    _msr_seam(
        variant,
        _PRE_POST_BODY.format(
            train_vintage=int(vintages[0]), test_from=int(start.replace("-", ""))
        ),
        note=f"train is the {vintages[0]} vintage through {through}; test is {start} onward",
    )
    variant.edit_package(
        lambda data: (
            _resplit(data, int(vintages[0]), through, start)
            or "the declared split rules are rewritten to say what the subject now does"
        )
    )


def _resplit(data: dict[str, Any], vintage: int, through: str, start: str) -> None:
    """Rewrite the two split rules `package.yaml` states, so the declaration matches the code."""
    data["splits"]["train"] = {
        "rule": f"every loan originated in {vintage}, periods through {through}"
    }
    data["splits"]["test"] = {
        "rule": (
            "every loan of the training vintages, periods from "
            f"{start} onward (the refinancing wave the training window never sees)"
        )
    }


# --------------------------------------------------------------------------------------------
# M1 -- multicollinearity
# --------------------------------------------------------------------------------------------

_REINTRODUCE_BODY = '''
REINTRODUCED = {features!r}
"""The features the VIF screen removed, put back into the design after it has run."""


def _reintroduce(retained, removed):
    """Return the screen's answer with the named features added back to it.

    The screen still runs and still reports what it removed; the fit ignores it for these
    columns. That is the instance: a screen whose result somebody overrode without recording it.
    """
    back = [entry for entry in removed if entry["feature"] in REINTRODUCED]
    names = set(retained) | {{str(entry["feature"]) for entry in back}}
    kept = [name for name in FEATURE_NAMES if name in names]
    return kept, [entry for entry in removed if entry not in back]
'''


def _recipe_reintroduce_collinear(variant: Variant, spec: DefectSpec) -> None:
    """Put the screened-out features back and add a near-duplicate of one of them."""
    features = list(spec.params.get("features") or ["bill_last", "utilisation_mean_6m"])
    source = str(spec.params.get("add_near_duplicate_of", "bill_last"))
    duplicate = str(spec.params.get("near_duplicate_name", "bill_last_adj"))
    variant.replace(
        "code/features.py",
        '    "bill_trend_6m",\n]',
        f'    "bill_trend_6m",\n    "{duplicate}",\n]',
        note=f"{duplicate} joins the declared feature list",
    )
    variant.replace(
        "code/features.py",
        '    "bill_trend_6m": "before_period_start",\n}',
        f'    "bill_trend_6m": "before_period_start",\n'
        f'    "{duplicate}": "before_period_start",\n}}',
        note=f"{duplicate} is declared before_period_start",
    )
    variant.replace(
        "code/features.py",
        '            "bill_trend_6m": _trend(bills),\n        }',
        f'            "bill_trend_6m": _trend(bills),\n'
        f'            "{duplicate}": _near_duplicate(engineered_source(bills)),\n        }}',
        note=f"{duplicate} is engineered as {source} plus a small multiplicative shock",
    )
    variant.append(
        "code/features.py",
        f'''
NEAR_DUPLICATE_SEED = {RECIPE_SEED}
NEAR_DUPLICATE_SD = 0.002
"""How far the near-duplicate is moved off its source, relatively: a rescaling, not a signal."""


def engineered_source(bills):
    """The column {duplicate} is a near-duplicate of: the most recent statement balance."""
    return bills[:, 0]


def _near_duplicate(values):
    """Return the source column with a small multiplicative shock, seeded for reproducibility.

    This is the same balance carried twice in different units -- the instance the study seeds --
    and it is not identical, because a column that is bit-for-bit another column is caught by
    reading the file rather than by measuring anything.
    """
    rng = np.random.default_rng(NEAR_DUPLICATE_SEED)
    return values * (1.0 + rng.normal(0.0, NEAR_DUPLICATE_SD, values.shape[0]))
''',
        note="the near-duplicate's own construction",
    )
    variant.replace(
        "code/run.py",
        "    retained, removed = vif_screen(matrix[train_mask], threshold=VIF_THRESHOLD)",
        "    retained, removed = vif_screen(matrix[train_mask], threshold=VIF_THRESHOLD)\n"
        "    retained, removed = _reintroduce(retained, removed)",
        note="the screen's removals are put back before the fit",
    )
    variant.append(
        "code/run.py",
        _REINTRODUCE_BODY.format(features=[*features, duplicate]),
        note="the override the screen's result is passed through",
    )
    variant.edit_package(
        lambda data: (
            _feature_entry(
                data,
                duplicate,
                "before_period_start",
                f"{source} in a second scaling, entered as a feature of its own",
            )
            or f"{duplicate} is declared as a feature"
        )
    )


# --------------------------------------------------------------------------------------------
# D1 -- data integrity
# --------------------------------------------------------------------------------------------

_MISSING_BODY = '''
MISSING_FEATURE = "{feature}"
MISSING_FRACTION = {fraction!r}
MISSING_IMPUTED_AS = {impute!r}
MISSING_SEED = {seed}
"""A vendor field that went dark for part of the scoring population.

The value is missing in the delivered `data_test.csv` -- which is what a validator is handed --
and the pipeline fills it with {impute!r} on its way into the fit and the score, so nothing fails
and no metric complains. The gap is visible only to whoever compares the two splits' missingness.
"""


def _seeded(frame, train_ids, test_ids):
    """Blank the feature on a share of the held-out rows, in the delivered file."""
    rng = np.random.default_rng(MISSING_SEED)
    positions = np.flatnonzero(np.isin(frame[ID_COLUMN].to_numpy(), test_ids.ids))
    n_blank = int(round(MISSING_FRACTION * positions.size))
    chosen = rng.choice(positions, size=n_blank, replace=False)
    blanked = frame.copy()
    blanked.loc[blanked.index[chosen], MISSING_FEATURE] = np.nan
    return blanked, train_ids, test_ids
'''


def _recipe_test_only_missing(variant: Variant, spec: DefectSpec) -> None:
    """Blank one feature on part of the held-out split; the subject imputes it silently."""
    feature = str(spec.params.get("feature", "pay_ratio_last"))
    fraction = float(spec.params.get("fraction", 0.30))
    impute = float(spec.params.get("impute_value", 0))
    variant.replace(
        "code/run.py",
        "    matrix = frame[FEATURE_NAMES]",
        f"    matrix = frame[FEATURE_NAMES]\n    design = matrix.fillna({impute!r})",
        note=f"the modelling matrix is imputed with {impute!r}; the delivered file is not",
    )
    variant.replace(
        "code/run.py",
        "    retained, removed = vif_screen(matrix[train_mask], threshold=VIF_THRESHOLD)",
        "    retained, removed = vif_screen(design[train_mask], threshold=VIF_THRESHOLD)",
        note="the screen reads the imputed matrix",
    )
    variant.replace(
        "code/run.py",
        "    ).fit(matrix.loc[train_mask, retained], frame.loc[train_mask, TARGET_COLUMN])",
        "    ).fit(design.loc[train_mask, retained], frame.loc[train_mask, TARGET_COLUMN])",
        note="the champion is fitted on the imputed matrix",
    )
    variant.replace(
        "code/run.py",
        "        scores = champion.predict_proba(matrix.loc[mask, retained])[:, 1]",
        "        scores = champion.predict_proba(design.loc[mask, retained])[:, 1]",
        note="every split is scored from the imputed matrix",
    )
    _credit_seam(
        variant,
        _MISSING_BODY.format(feature=feature, fraction=fraction, impute=impute, seed=RECIPE_SEED),
        note=f"{feature} is blank on {fraction:.0%} of the held-out rows",
    )


# --------------------------------------------------------------------------------------------
# T1 -- a false developer claim
# --------------------------------------------------------------------------------------------


def _recipe_false_declared_claim(variant: Variant, spec: DefectSpec) -> None:
    """Inflate one declared claim and put the declared bound just under the inflated number."""
    metric = str(spec.params.get("metric", "auc"))
    split = str(spec.params.get("split", "test"))
    inflate = float(spec.params.get("inflate_by", 0.05))

    def edit(data: dict[str, Any]) -> str:
        claims = data.get("claims") or []
        matches = [
            claim
            for claim in claims
            if claim.get("metric") == metric and claim.get("split") == split
        ]
        if not matches:
            raise ValueError(
                f"{spec.id}: package.yaml declares no claim about {metric} on {split}, so there "
                "is nothing to inflate; the recipe overstates a number the developer stated"
            )
        claim = matches[0]
        declared = float(claim["value"])
        inflated = round(declared + inflate, 6)
        floor = round(declared + inflate / 2.0, 6)
        claim["value"] = inflated
        claim["text"] = f"{metric.upper()} on the {split} split is {inflated:g}"
        rules = [
            rule
            for rule in data.get("thresholds") or []
            if rule.get("metric") == metric and rule.get("split") == split
        ]
        if not rules:
            raise ValueError(
                f"{spec.id}: package.yaml declares no {metric} threshold on {split} to move"
            )
        rules[0]["min"] = floor
        return (
            f"the declared {metric} on {split} is raised from {declared:g} to {inflated:g} and "
            f"the declared minimum is set to {floor:g}, between the claim and the truth"
        )

    variant.edit_package(edit)


# --------------------------------------------------------------------------------------------
# X1 -- a scenario entered with the wrong sign
# --------------------------------------------------------------------------------------------

_SIGN_ERROR_BODY = '''
FLIPPED_SHOCK_BP = {shock}
"""The one scenario whose shock is applied with the wrong sign.

The table still has a row for it and the row is still labelled {shock} bp; what was valued under
that label is the opposite shift. The value curve stops being monotone in the shock and the
convexity the projection reports changes sign, which is what the declared expectation is read
against.
"""


def _applied_shock(shock_bp):
    """Return the shift actually applied for one declared shock."""
    return -shock_bp if shock_bp == FLIPPED_SHOCK_BP else shock_bp
'''


def _recipe_projection_sign_error(variant: Variant, spec: DefectSpec) -> None:
    """Apply one declared rate shock with the wrong sign in the projection."""
    shock = int(spec.params.get("shock_bp", -300))
    variant.replace(
        "code/projection.py",
        "            hazard_of,\n            book,\n            path,\n            shock,",
        "            hazard_of,\n            book,\n            path,\n"
        "            _applied_shock(shock),",
        note=f"the {shock} bp scenario is valued under the opposite shift",
    )
    variant.append(
        "code/projection.py", _SIGN_ERROR_BODY.format(shock=shock), note="the sign error itself"
    )


# --------------------------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------------------------

_PERTURBATION_COMMON = '''
PERTURBATION_SEED = {seed}
FEATURE_PREFIX = "{prefix}"
"""The harmless control: the rows are shuffled and every feature column carries a prefix.

Neither changes a number. The split is drawn over sorted identifiers, so shuffling the rows does
not move it; the prefix is applied to the declaration and to every file the subject writes at
once, so a check that reads `package.yaml` and a check that reads `data_<split>.csv` still agree
about what a column is called. A finding here is a false alarm, by construction.
"""


def _prefixed(name):
    """Return a declared feature's new name; anything else keeps the name it had."""
    return FEATURE_PREFIX + name if name in FEATURE_TIMING else name


def _prefixed_removed(removed):
    """Rename the screen's removal list, which `model_summary.json` publishes by feature."""
    return [dict(entry, feature=_prefixed(str(entry["feature"]))) for entry in removed]
'''

_CREDIT_PERTURBATION = '''
def _seeded(frame, train_ids, test_ids):
    """Shuffle the rows. `stratified_split` draws over sorted client ids and does not move."""
    order = np.random.default_rng(PERTURBATION_SEED).permutation(len(frame))
    return frame.iloc[order].reset_index(drop=True), train_ids, test_ids
'''

_MSR_PERTURBATION = '''
def _seeded(panel, masks):
    """Shuffle the loan-months, carrying each split's mask with them."""
    order = np.random.default_rng(PERTURBATION_SEED).permutation(len(panel))
    reordered = panel.iloc[order].reset_index(drop=True)
    return reordered, {{name: mask[order] for name, mask in masks.items()}}
'''


def _recipe_harmless_perturbation(variant: Variant, spec: DefectSpec) -> None:
    """Shuffle the rows and prefix the feature columns, changing no number."""
    prefix = str(spec.params.get("feature_prefix", "f_"))
    shuffle = bool(spec.params.get("shuffle_rows", True))
    if not shuffle:
        raise ValueError(f"{spec.id}: the control shuffles rows; shuffle_rows: false is not it")
    common = _PERTURBATION_COMMON.format(seed=RECIPE_SEED, prefix=prefix)
    if spec.subject == "credit_default":
        _credit_seam(variant, common + _CREDIT_PERTURBATION, note="the shuffle and the prefix")
        variant.replace(
            "code/run.py",
            '        _write_csv(out_dir / f"data_{name}.csv", '
            "part[[ID_COLUMN, *retained, TARGET_COLUMN]])",
            "        _write_csv(\n"
            '            out_dir / f"data_{name}.csv",\n'
            "            part[[ID_COLUMN, *retained, TARGET_COLUMN]].rename(columns=_prefixed),\n"
            "        )",
            note="data_<split>.csv carries the prefixed column names",
        )
        variant.replace(
            "code/run.py",
            '            {"name": name, "dtype": str(frame[name].dtype), '
            '"timing": FEATURE_TIMING[name]}',
            "            {\n"
            '                "name": _prefixed(name),\n'
            '                "dtype": str(frame[name].dtype),\n'
            '                "timing": FEATURE_TIMING[name],\n'
            "            }",
            note="features.json carries the prefixed names",
        )
    else:
        _msr_seam(variant, common + _MSR_PERTURBATION.format(), note="the shuffle and the prefix")
        variant.replace(
            "code/run.py",
            "            part[[ID_COLUMN, TIME_COLUMN, *retained, REGIME_COLUMN, TARGET_COLUMN]],",
            "            part[\n"
            "                [ID_COLUMN, TIME_COLUMN, *retained, REGIME_COLUMN, TARGET_COLUMN]\n"
            "            ].rename(columns=_prefixed),",
            note="data_<split>.csv carries the prefixed column names",
        )
        variant.replace(
            "code/run.py",
            '            {"name": name, "dtype": str(panel[name].dtype), '
            '"timing": FEATURE_TIMING[name]}',
            "            {\n"
            '                "name": _prefixed(name),\n'
            '                "dtype": str(panel[name].dtype),\n'
            '                "timing": FEATURE_TIMING[name],\n'
            "            }",
            note="features.json carries the prefixed names",
        )
    variant.replace(
        "code/run.py",
        '                {"feature": name, "value": float(value)}',
        '                {"feature": _prefixed(name), "value": float(value)}',
        note="model_summary.json's coefficients carry the prefixed names",
    )
    variant.replace(
        "code/run.py",
        '            "removed": removed,',
        '            "removed": _prefixed_removed(removed),',
        note="model_summary.json's removal list carries the prefixed names",
    )
    variant.edit_package(
        lambda data: (
            _prefix_features(data, prefix)
            or f"every declared feature name gains the prefix {prefix!r}"
        )
    )


def _prefix_features(data: dict[str, Any], prefix: str) -> None:
    """Rename every declared feature in `package.yaml`, leaving everything else alone."""
    for feature in data["features"]:
        feature["name"] = prefix + str(feature["name"])


def _recipe_none(variant: Variant, spec: DefectSpec) -> None:
    """The clean control: a copy of the subject, and nothing done to it."""
    del spec
    variant.notes.append("no edit: this control is the subject as it ships")


RECIPES: Final[Mapping[str, Callable[[Variant, DefectSpec], None]]] = {
    "add_post_outcome_feature": _recipe_add_post_outcome_feature,
    "duplicate_test_into_train": _recipe_duplicate_test_into_train,
    "end_of_month_balance": _recipe_end_of_month_balance,
    "false_declared_claim": _recipe_false_declared_claim,
    "harmless_perturbation": _recipe_harmless_perturbation,
    "none": _recipe_none,
    "oversample_events": _recipe_oversample_events,
    "projection_sign_error": _recipe_projection_sign_error,
    "regime_sign_flip": _recipe_regime_sign_flip,
    "reintroduce_collinear": _recipe_reintroduce_collinear,
    "smote_no_recalibration": _recipe_smote_no_recalibration,
    "test_only_missing": _recipe_test_only_missing,
    "train_on_segment": _recipe_train_on_segment,
    "train_pre_test_post": _recipe_train_pre_test_post,
}
"""Every recipe `eval/taxonomy.yaml` may name, by the name it names it under."""


@dataclass(frozen=True)
class BuildResult:
    """One variant that was written, or one row that was not.

    Attributes:
        spec: The taxonomy row.
        root: Where the variant was written, or `None` when it was not built.
        notes: The `applied:` lines the recipe recorded, empty on a row that was not built.
        reason: Why the row was not built -- it is marked `status: dropped`, or its recipe is one
            of `SYNTHETIC_ONLY_RECIPES` and the build is a `--data` one. `None` on a built row.
    """

    spec: DefectSpec
    root: Path | None
    notes: list[str]
    reason: str | None = None

    @property
    def built(self) -> bool:
        """Whether a package was written for this row."""
        return self.root is not None


def seed(
    subject_pkg: Path | str,
    defect: DefectSpec,
    out_dir: Path | str,
    *,
    synthetic_n: int | None = None,
    taxonomy: Taxonomy | None = None,
    data_dir: Path | str | None = None,
) -> ModelPackage:
    """Copy a subject package, apply one recipe to the copy and write `SEED.yaml` beside it.

    Args:
        subject_pkg: The clean subject's package directory.
        defect: Which class, which recipe and which parameters.
        out_dir: The variant package's own directory. It is removed first if it exists, so that
            seeding twice writes the same bytes rather than layering one recipe on another.
        synthetic_n: The panel size the variant is meant to be validated at, recorded in
            `SEED.yaml`; it is a note to the operator and changes no file of the package.
        taxonomy: The taxonomy the row came from, so `SEED.yaml` can record its digest.
        data_dir: Where the subject's real data lives, for a variant that is meant to be validated
            under `--data`. It changes no byte of the recipe: the nine recipes that work in both
            modes hang off the seam *after* the subject has chosen its data mode, or they only
            edit `package.yaml`. What it changes is what `SEED.yaml` records and, through
            `load_package`, that the variant's declared manifest is verified against the data it
            will be run on -- so a variant that cannot be validated is discovered here rather than
            at the third hour of a paid sitting (D-137, amended).

    Returns:
        The variant, loaded through `quaestor.package.load_package` -- which is also the check
        that the recipe left a package that still parses.

    Raises:
        ValueError: The row is marked `status: dropped`, or its recipe is one of
            `SYNTHETIC_ONLY_RECIPES` and `data_dir` was given, or a recipe's anchor is not where
            it was.
        PackageError: `data_dir` was given and a digest of the package's manifest does not match.
    """
    source = Path(subject_pkg)
    target = Path(out_dir)
    if defect.is_dropped:
        raise ValueError(
            f"{defect.id} is marked status: dropped in the taxonomy ({defect.dropped_reason}); "
            "a dropped recipe is recorded and not built"
        )
    if data_dir is not None and defect.recipe in SYNTHETIC_ONLY_RECIPES:
        raise ValueError(f"{defect.id} is synthetic-only: {SYNTHETIC_ONLY_RECIPES[defect.recipe]}")
    if target.exists():
        shutil.rmtree(target)
    for path in _copyable(source):
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)

    variant = Variant(target, defect.id)
    RECIPES[defect.recipe](variant, defect)
    _write_seed_file(
        variant, defect, source, synthetic_n=synthetic_n, taxonomy=taxonomy, data_dir=data_dir
    )
    return load_package(target, data_dir=data_dir)


def _write_seed_file(
    variant: Variant,
    defect: DefectSpec,
    source: Path,
    *,
    synthetic_n: int | None,
    taxonomy: Taxonomy | None,
    data_dir: Path | str | None = None,
) -> None:
    """Write the variant's provenance: the answer key, in the file the pipeline never opens."""
    payload: dict[str, Any] = {
        "variant": defect.id,
        "subject": defect.subject,
        "status": defect.status,
        "seeded": {
            "class": defect.defect_class,
            "recipe": defect.recipe,
            "params": dict(defect.params),
            "seed": RECIPE_SEED,
        },
        "expected_signal": defect.expected_signal,
        "met_where": defect.met_where,
        "applied": list(variant.notes),
        "source": {
            "package": str(source),
            "files": len(list(_copyable(source))),
        },
        "mode": REAL_MODE if data_dir is not None else SYNTHETIC_MODE,
        "synthetic_n": None if data_dir is not None else synthetic_n,
        "data_dir": str(data_dir) if data_dir is not None else None,
        "generator": "eval/seed.py",
        "taxonomy": (
            {"path": str(taxonomy.path), "sha256": taxonomy.digest()} if taxonomy else None
        ),
    }
    header = (
        "# SEED.yaml -- the answer key for this variant. Written by eval/seed.py; read by\n"
        "# eval/score.py and by a human. No code path in quaestor opens this file, and a test\n"
        "# plants a value here and asserts it reaches no trace event, no artifact, no claim and\n"
        "# no line of report.md (02-SPEC.md section 5).\n"
    )
    variant.write(
        SEED_FILE,
        header + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
    )


def build_all(
    taxonomy: Taxonomy,
    out_dir: Path | str,
    *,
    subjects_dir: Path | str = SUBJECTS_DIR,
    synthetic_n: Mapping[str, int] | None = None,
    data_dir: Path | str | None = None,
) -> list[BuildResult]:
    """Build every variant the taxonomy declares, dropped and synthetic-only rows excepted.

    Args:
        taxonomy: The loaded taxonomy.
        out_dir: Where the variant packages go, one directory per variant id.
        subjects_dir: Where the clean subjects live.
        synthetic_n: Panel size per subject, recorded in each `SEED.yaml`.
        data_dir: Where the subjects' real data lives. When given, the four recipes of
            `SYNTHETIC_ONLY_RECIPES` are skipped with their reason rather than built into packages
            that cannot run (D-137, amended), and every variant that *is* built has its manifest
            verified against that directory.

    Returns:
        One result per row of the taxonomy, in file order; a row that was not built has no root
        and carries the reason.
    """
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    sizes = dict(synthetic_n or {})
    results: list[BuildResult] = []
    for spec in taxonomy.specs:
        if spec.is_dropped:
            reason = str(spec.dropped_reason)
            results.append(BuildResult(spec=spec, root=None, notes=[reason], reason=reason))
            continue
        if data_dir is not None and spec.recipe in SYNTHETIC_ONLY_RECIPES:
            reason = f"synthetic-only under --data: {SYNTHETIC_ONLY_RECIPES[spec.recipe]}"
            results.append(BuildResult(spec=spec, root=None, notes=[], reason=reason))
            continue
        target = root / spec.id
        package = seed(
            Path(subjects_dir) / spec.subject,
            spec,
            target,
            synthetic_n=sizes.get(spec.subject),
            taxonomy=taxonomy,
            data_dir=data_dir,
        )
        assert package.root == target
        results.append(BuildResult(spec=spec, root=target, notes=list(_notes_of(target))))
    return results


def _notes_of(root: Path) -> Sequence[str]:
    """Read back the `applied:` lines a variant's `SEED.yaml` recorded."""
    payload = yaml.safe_load((root / SEED_FILE).read_text(encoding="utf-8"))
    return list(payload.get("applied") or [])


def main(argv: Sequence[str] | None = None) -> int:
    """Build every variant of a taxonomy. Returns an exit code.

    This is what `quaestor study build` runs; it is a `main` of its own so that the generator can
    be driven from a checkout without the console script.
    """
    parser = argparse.ArgumentParser(
        prog="python eval/seed.py",
        description="Build the seeded-defect variants of eval/taxonomy.yaml.",
    )
    parser.add_argument("--taxonomy", type=Path, default=TAXONOMY_PATH)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--subjects", type=Path, default=SUBJECTS_DIR)
    parser.add_argument("--synthetic", type=int, nargs="?", const=-1, default=None)
    parser.add_argument("--data", type=Path, default=None)
    args = parser.parse_args(list(argv) if argv is not None else None)
    taxonomy = load_taxonomy(args.taxonomy)
    results = build_all(
        taxonomy,
        args.out,
        subjects_dir=args.subjects,
        synthetic_n=synthetic_sizes(taxonomy, args.synthetic),
        data_dir=args.data,
    )
    for result in results:
        where = str(result.root) if result.root else f"not built ({result.reason})"
        print(f"{result.spec.id}: {result.spec.recipe} -> {where}")
    built = [result for result in results if result.built]
    print(f"{len(built)} variant(s) built under {args.out}; {len(results) - len(built)} dropped")
    return 0


def synthetic_sizes(taxonomy: Taxonomy, requested: int | None) -> dict[str, int]:
    """Resolve `--synthetic [N]` to a panel size per subject.

    A number applies to every subject; a bare `--synthetic`, or none at all, takes each subject's
    documented default from `quaestor.configs`, which is what `quaestor validate --synthetic`
    with no number uses.
    """
    from quaestor.configs import synthetic_default_n

    sizes: dict[str, int] = {}
    for name in taxonomy.subjects:
        if requested is not None and requested > 0:
            sizes[name] = requested
            continue
        default = synthetic_default_n(name)
        if default is not None:
            sizes[name] = default
    return sizes


if __name__ == "__main__":  # pragma: no cover - the module's command-line entry point
    sys.exit(main())
