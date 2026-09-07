"""The subject: `python -m code.run --out DIR [--data DIR | --synthetic N] [--seed S]`.

What a model developer hands over. It engineers the twelve features of `package.yaml`, screens
them for multicollinearity, fits a logistic-regression champion on a stratified 70/30 split of
clients, and writes the standard artifact contract of spec section 3.3 into `--out`. Quaestor
reads only those files, which is what lets the same checks run against this subject, against the
hazard subject and against every seeded variant.

Two data modes, one pipeline:

* `--synthetic N` draws N clients from `code/synthetic.py` and engineers them here, so the whole
  pipeline -- engineering, screen, split, fit -- is exercised offline and deterministically.
* `--data DIR` reads `train.csv` and `test.csv`, which `sample.py` built from the UCI file with
  the same `engineer` and the same split rule and whose digests `package.yaml` pins. The split is
  not re-drawn in this mode: the sample *is* the split, and its two digests are what make the real
  fit reproducible from the manifest (DECISIONS D-030).

Nothing here imports `quaestor`, and nothing here reaches the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .features import (
    DECLARED_SEED,
    FEATURE_NAMES,
    FEATURE_TIMING,
    ID_COLUMN,
    TARGET_COLUMN,
    VIF_THRESHOLD,
    Split,
    engineer,
    rows_hash,
    stratified_split,
    vif_screen,
)
from .synthetic import SyntheticProcess, generate

MODEL_NAME = "logistic_regression"
SPLIT_NAMES = ("train", "test")
FLOAT_FORMAT = "%.10g"
"""The same ten significant digits the artifact store rounds to, so a CSV round-trips exactly."""


def main(argv: list[str] | None = None) -> int:
    """Run the subject end to end and write the spec section 3.3 files. Returns an exit code."""
    args = parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.synthetic is not None:
        frame = engineer(generate(SyntheticProcess(n_clients=args.synthetic, seed=args.seed)))
        train_ids, test_ids = stratified_split(
            frame[ID_COLUMN].to_numpy(), frame[TARGET_COLUMN].to_numpy(), seed=args.seed
        )
        mode = f"synthetic n={args.synthetic}"
    else:
        frame, train_ids, test_ids = _read_sample(Path(args.data))
        mode = f"data {args.data}"

    splits = {"train": train_ids, "test": test_ids}
    train_mask = np.isin(frame[ID_COLUMN].to_numpy(), train_ids.ids)
    matrix = frame[FEATURE_NAMES]
    retained, removed = vif_screen(matrix[train_mask], threshold=VIF_THRESHOLD)

    champion = Pipeline(
        [
            ("scale", StandardScaler()),
            ("logit", LogisticRegression(class_weight=None, max_iter=1000)),
        ]
    ).fit(matrix.loc[train_mask, retained], frame.loc[train_mask, TARGET_COLUMN])

    metrics: dict[str, dict[str, float]] = {}
    for name, split in splits.items():
        mask = np.isin(frame[ID_COLUMN].to_numpy(), split.ids)
        part = frame[mask]
        scores = champion.predict_proba(matrix.loc[mask, retained])[:, 1]
        truth = part[TARGET_COLUMN].to_numpy(dtype=int)
        _write_csv(
            out_dir / f"predictions_{name}.csv",
            pd.DataFrame(
                {ID_COLUMN: part[ID_COLUMN].to_numpy(), "y_true": truth, "y_score": scores}
            ),
        )
        _write_csv(out_dir / f"data_{name}.csv", part[[ID_COLUMN, *retained, TARGET_COLUMN]])
        metrics[name] = _metrics(truth, scores)

    _write_json(
        out_dir / "splits.json",
        {
            name: {
                "n": split.n,
                "event_rate": float(
                    frame.loc[np.isin(frame[ID_COLUMN].to_numpy(), split.ids), TARGET_COLUMN].mean()
                ),
                "rows_hash": rows_hash(split.ids),
            }
            for name, split in splits.items()
        },
    )
    _write_json(
        out_dir / "features.json",
        [
            {"name": name, "dtype": str(frame[name].dtype), "timing": FEATURE_TIMING[name]}
            for name in FEATURE_NAMES
        ],
    )
    _write_json(out_dir / "metrics.json", metrics)
    _write_json(
        out_dir / "model_summary.json",
        {
            "model": MODEL_NAME,
            "standardised": True,
            "class_weight": None,
            "n_train": int(train_mask.sum()),
            "vif_threshold": VIF_THRESHOLD,
            "intercept": float(champion.named_steps["logit"].intercept_[0]),
            "coefficients": [
                {"feature": name, "value": float(value)}
                for name, value in zip(
                    retained, champion.named_steps["logit"].coef_[0], strict=True
                )
            ],
            "removed": removed,
        },
    )

    print(
        f"credit_default: {mode}, seed {args.seed}; "
        f"{len(retained)} of {len(FEATURE_NAMES)} features retained, "
        f"removed {[entry['feature'] for entry in removed]}; "
        f"train n={splits['train'].n}, test n={splits['test'].n}; "
        f"test auc={metrics['test']['auc']:.4f} brier={metrics['test']['brier']:.4f}"
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the entrypoint's arguments. Exactly one of `--data` and `--synthetic` is required."""
    parser = argparse.ArgumentParser(
        prog="python -m code.run", description="Fit the credit_default champion."
    )
    parser.add_argument("--out", required=True, help="where to write the spec 3.3 files")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--data", help="a directory holding train.csv and test.csv")
    source.add_argument(
        "--synthetic", type=int, metavar="N", help="draw N clients from the known process"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DECLARED_SEED,
        help=f"the seed for the draw and the split (default {DECLARED_SEED}, as package.yaml says)",
    )
    return parser.parse_args(argv)


def _read_sample(data_dir: Path) -> tuple[pd.DataFrame, Split, Split]:
    """Read `train.csv` and `test.csv`, already engineered and split by `sample.py`."""
    parts = []
    ids: dict[str, np.ndarray] = {}
    for name in SPLIT_NAMES:
        path = data_dir / f"{name}.csv"
        if not path.is_file():
            raise SystemExit(f"{path} is missing; build the sample with `python sample.py --raw D`")
        part = pd.read_csv(path)
        expected = [ID_COLUMN, *FEATURE_NAMES, TARGET_COLUMN]
        missing = [column for column in expected if column not in part.columns]
        if missing:
            raise SystemExit(f"{path} is missing the columns {missing}")
        parts.append(part[expected])
        ids[name] = part[ID_COLUMN].to_numpy()
    overlap = np.intersect1d(ids["train"], ids["test"])
    if overlap.size:
        raise SystemExit(
            f"{overlap.size} client identifiers appear in both train.csv and test.csv "
            f"(for example {overlap[:5].tolist()}); rebuild the sample"
        )
    frame = pd.concat(parts, ignore_index=True)
    return frame, Split("train", ids["train"]), Split("test", ids["test"])


def _metrics(truth: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """The developer's own metrics. Quaestor recomputes every one of them and trusts none."""
    order = np.argsort(scores)
    sorted_truth = truth[order]
    positives = max(int(truth.sum()), 1)
    negatives = max(int(truth.size - truth.sum()), 1)
    cumulative_positive = np.cumsum(sorted_truth) / positives
    cumulative_negative = np.cumsum(1 - sorted_truth) / negatives
    auc = float(roc_auc_score(truth, scores))
    return {
        "n": int(truth.size),
        "event_rate": float(truth.mean()),
        "auc": auc,
        "gini": 2.0 * auc - 1.0,
        "ks": float(np.max(np.abs(cumulative_positive - cumulative_negative))),
        "brier": float(np.mean((scores - truth) ** 2)),
        "logloss": float(log_loss(truth, scores)),
        "mean_predicted": float(scores.mean()),
    }


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    """Write a CSV with the fixed float format, so two runs of one seed are byte-identical."""
    frame.to_csv(path, index=False, float_format=FLOAT_FORMAT, lineterminator="\n")


def _write_json(path: Path, payload: object) -> None:
    """Write JSON with sorted keys and a trailing newline."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
