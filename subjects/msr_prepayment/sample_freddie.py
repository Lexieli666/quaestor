"""Build the real panel: `python sample_freddie.py --raw DIR --fred CSV --out DIR`.

Never run by a test and never run in CI: `CLAUDE.md` forbids downloading data and forbids training
on real data inside `pytest`, so the suite covers this file for argument handling and for the
column map only, on a three-loan frame the test writes itself. A human downloads the files once,
runs this script, pastes the printed manifest into `package.yaml`, and from then on
`quaestor validate subjects/msr_prepayment --data <dir>` verifies those digests before anything
runs.

**What it expects under `--raw`.** The Freddie Mac Single-Family Loan-Level Dataset *sample*
files, one pair per origination year, unzipped in place, **with the names the distribution gives
them** -- this script never renames a downloaded file. The performance member has been called two
things across distributions, and either is accepted, per vintage:

| from | origination file | performance file, either name |
| --- | --- | --- |
| `sample_2014.zip` | `sample_orig_2014.txt` | `sample_svcg_2014.txt`, `sample_perf_2014.txt` |
| `sample_2017.zip` | `sample_orig_2017.txt` | `sample_svcg_2017.txt`, `sample_perf_2017.txt` |
| `sample_2019.zip` | `sample_orig_2019.txt` | `sample_svcg_2019.txt`, `sample_perf_2019.txt` |

`sample_svcg_YYYY.txt` is looked for first, because that is what the archived distributions of
these three vintages carry; `sample_perf_YYYY.txt` is what the July 2026 distribution writes
(DECISIONS D-159).

Both files are pipe-delimited with no header row, so the layouts are positional and **two
publications of each are written out below**: the *2024 user guide*'s (32 origination fields, 32
performance fields) and *Release 47, July 2026*'s (31 and 35). The reader picks the layout by the
field count it counts, prints the release it read the file as, and refuses any other count rather
than silently mapping the wrong column -- which is D-048's rule, unchanged, now with a second
layout to choose between. The Release 47 sources are the July 2026 general user guide, its
disclosure-changes summary and its file-layout workbook, all under
<https://www.freddiemac.com/fmac-resources/research/>.

**What it expects at `--fred`.** The FRED series `MORTGAGE30US` exported as CSV -- by default
`~/code/data-raw/fred/MORTGAGE30US.csv`. It is weekly, so the **first observation of each month**
is that month's month-start rate, and the month-start rate of month `m` is stored as the close of
month `m - 1`: no time passes between them, and the subject's one lagging rule is that every raw
value is a closing value of the month it is labelled with (`code/features.py`, DECISIONS D-038).

**The licence.** Freddie Mac's terms of use permit analysis but not redistribution of the
loan-level records, so nothing built here is committed: not a row, not a per-loan digest. What
`package.yaml`'s `data.manifest` records is the SHA-256 of the five files this script writes, and
`subjects/msr_prepayment/artifacts/real/` holds the aggregates of the real run -- coefficients,
metrics, split sizes and digests -- and nothing else. `README.md` says so too.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd


def _load_features() -> ModuleType:
    """Import `code/features.py` from its path, under a name that is not `code`.

    The sandbox runs the subject as `python -m code.run`, where the package really is called
    `code`; outside the sandbox that name would shadow the standard library module for the whole
    of this process. `code/features.py` imports nothing of its own, so it loads standalone.
    """
    alias = "msr_prepayment_features"
    if alias in sys.modules:
        return sys.modules[alias]
    path = Path(__file__).resolve().parent / "code" / "features.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:  # pragma: no cover - a missing code/ is a defect
        raise SystemExit(f"{path} is not importable; the subject is incomplete")
    module = importlib.util.module_from_spec(spec)
    # Registered before it is executed, because a dataclass defined under
    # `from __future__ import annotations` resolves its own module out of `sys.modules`.
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


_features = _load_features()

ORIGINATION_YEARS = (2014, 2017, 2019)
"""The three vintages `package.yaml` declares, one sample file pair each."""

DEFAULT_N_LOANS = 20_000
DEFAULT_SEED = 20260901
"""`package.yaml`: 20,000 loans in total, seed 20260901, stratified by origination year."""

DEFAULT_FRED_PATH = "~/code/data-raw/fred/MORTGAGE30US.csv"
"""Where the operator keeps the FRED export; `--fred` overrides it."""

ORIGINATION_LAYOUT_2024 = (
    "credit_score",
    "first_payment_date",
    "first_time_homebuyer_flag",
    "maturity_date",
    "msa",
    "mi_percent",
    "number_of_units",
    "occupancy_status",
    "ocltv",
    "dti",
    "orig_upb",
    "oltv",
    "orig_interest_rate",
    "channel",
    "ppm_flag",
    "amortization_type",
    "property_state",
    "property_type",
    "postal_code",
    "loan_sequence_number",
    "loan_purpose",
    "orig_loan_term",
    "number_of_borrowers",
    "seller_name",
    "servicer_name",
    "super_conforming_flag",
    "pre_relief_refinance_loan_sequence_number",
    "program_indicator",
    "relief_refinance_indicator",
    "property_valuation_method",
    "interest_only_indicator",
    "mi_cancellation_indicator",
)
"""`sample_orig_YYYY.txt` as the **2024 user guide** orders it: 32 fields, pipe-delimited,
no header. `servicer_name` (25) and `mi_cancellation_indicator` (32) are origination fields here
and performance fields in Release 47."""

PERFORMANCE_LAYOUT_2024 = (
    "loan_sequence_number",
    "monthly_reporting_period",
    "current_actual_upb",
    "current_loan_delinquency_status",
    "loan_age",
    "remaining_months_to_legal_maturity",
    "defect_settlement_date",
    "modification_flag",
    "zero_balance_code",
    "zero_balance_effective_date",
    "current_interest_rate",
    "current_deferred_upb",
    "ddlpi",
    "mi_recoveries",
    "net_sale_proceeds",
    "non_mi_recoveries",
    "expenses",
    "legal_costs",
    "maintenance_and_preservation_costs",
    "taxes_and_insurance",
    "miscellaneous_expenses",
    "actual_loss_calculation",
    "cumulative_modification_cost",
    "step_modification_flag",
    "payment_deferral",
    "estimated_loan_to_value",
    "zero_balance_removal_upb",
    "delinquent_accrued_interest",
    "delinquency_due_to_disaster",
    "borrower_assistance_status_code",
    "current_month_modification_cost",
    "interest_bearing_upb",
)
"""`sample_svcg_YYYY.txt` as the **2024 user guide** orders it: 32 fields, pipe-delimited,
no header."""

ORIGINATION_LAYOUT_2026 = (
    "credit_score",
    "first_payment_date",
    "first_time_homebuyer_flag",
    "maturity_date",
    "msa",
    "mi_percent",
    "number_of_units",
    "occupancy_status",
    "ocltv",
    "dti",
    "orig_upb",
    "oltv",
    "orig_interest_rate",
    "channel",
    "ppm_flag",
    "amortization_type",
    "property_state",
    "property_type",
    "postal_code",
    "loan_sequence_number",
    "loan_purpose",
    "orig_loan_term",
    "number_of_borrowers",
    "seller_name",
    "super_conforming_flag",
    "pre_relief_refinance_loan_sequence_number",
    "program_indicator",
    "relief_refinance_indicator",
    "property_valuation_method",
    "interest_only_indicator",
    "vantagescore_4",
)
"""`sample_orig_YYYY.txt` as **Release 47, July 2026** orders it: 31 fields.

Against the 2024 layout: **positions 1 to 24 are identical**, `servicer_name` (25) and
`mi_cancellation_indicator` (32) have moved to the performance file, and `VantageScore 4.0` is new
at 31. The guide renames field 20 to *Loan Identifier* and field 1 to *Classic FICO*; this tuple
keeps `loan_sequence_number` and `credit_score`, because the quantity is unchanged and renaming
them here would rename them in `to_raw_panel`, in `code/features.py` and in `package.yaml` for no
reason a reader of the report could see (DECISIONS D-048, amended).
"""

PERFORMANCE_LAYOUT_2026 = (
    "loan_sequence_number",
    "monthly_reporting_period",
    "current_actual_upb",
    "current_loan_delinquency_status",
    "loan_age",
    "remaining_months_to_legal_maturity",
    "defect_settlement_date",
    "modification_flag",
    "zero_balance_code",
    "zero_balance_effective_date",
    "current_interest_rate",
    "current_deferred_upb",
    "ddlpi",
    "mi_recoveries",
    "net_sale_proceeds",
    "non_mi_recoveries",
    "expenses",
    "legal_costs",
    "maintenance_and_preservation_costs",
    "taxes_and_insurance",
    "miscellaneous_expenses",
    "actual_loss_calculation",
    "cumulative_modification_cost",
    "step_modification_flag",
    "payment_deferral",
    "estimated_loan_to_value",
    "zero_balance_removal_upb",
    "delinquent_accrued_interest",
    "delinquency_due_to_disaster",
    "borrower_assistance_status_code",
    "current_month_modification_cost",
    "interest_bearing_upb",
    "mi_cancellation_indicator",
    "servicer_name",
    "bankruptcy_cramdown_costs",
)
"""`sample_perf_YYYY.txt` as **Release 47, July 2026** orders it: 35 fields.

Against the 2024 layout: **positions 1 to 32 are the same quantities in the same order**, and nine
of them are renamed by the guide without changing what they hold -- *Loan Identifier* (1), *Period*
(2), *Underwriting Defect and Major Servicing Defect Settlement Date* (7), *Current Non-Interest
Bearing UPB* (12), *Interest Rate Step Indicator* (24), *Payment Deferral Flag* (25), *Borrower
Assistance Plan* (30), *Current Period Modification Costs* (31) and *Current Interest Bearing UPB*
(32). This tuple keeps the sampler's own names for all nine, for the reason
:data:`ORIGINATION_LAYOUT_2026` gives. Three fields are appended: *Mortgage Insurance Cancellation
Indicator* (33) and *Servicer Name* (34), both of which were origination fields in 2024, and
*Bankruptcy Cramdown Costs* (35), which is new.
"""

RELEASE_2024 = "the 2024 user guide"
RELEASE_2026 = "Release 47, July 2026"
"""What the reader prints when it says which publication it read a file as."""

ORIGINATION_LAYOUTS = {
    len(ORIGINATION_LAYOUT_2024): (RELEASE_2024, ORIGINATION_LAYOUT_2024),
    len(ORIGINATION_LAYOUT_2026): (RELEASE_2026, ORIGINATION_LAYOUT_2026),
}
PERFORMANCE_LAYOUTS = {
    len(PERFORMANCE_LAYOUT_2024): (RELEASE_2024, PERFORMANCE_LAYOUT_2024),
    len(PERFORMANCE_LAYOUT_2026): (RELEASE_2026, PERFORMANCE_LAYOUT_2026),
}
"""Field count to (publication, layout). The count is the only discriminator a header-less file
offers, and it separates these two publications cleanly: 32 against 31 for the origination file and
32 against 35 for the performance one. Any other count is refused (D-048)."""

PERFORMANCE_FILE_STEMS = ("sample_svcg_{year}.txt", "sample_perf_{year}.txt")
"""The two names the performance member has been distributed under, in the order they are tried.

`svcg` first: the archived distributions of the 2014, 2017 and 2019 vintages are what an operator
building this panel actually has, and a directory holding both should be read as the archive it is.
The file is never renamed on disk (DECISIONS D-159)."""

VOLUNTARY_PAYOFF_CODE = "01"
"""The only zero-balance code that is the event: "Prepaid or Matured (Voluntary Payoff)"."""

CENSORING_CODES = ("02", "03", "06", "09", "15", "16", "96", "97", "98")
"""Every other zero-balance code: a third-party sale, a short sale, a repurchase, an REO
disposition, a note sale, a reperforming-loan sale or a non-credit removal. None of them is a
voluntary payoff, so the loan is censored at that month rather than counted as a survivor of it.

Read against the **July 2026** guide's enumeration -- 01, 02, 03, 09, 15, 16, 96 -- this list is a
superset by three and a subset by none. `16` is **added**: a reperforming-loan sale is a
disposition, the loan leaves the dataset without paying off, and counting that month as one the
loan survived would put a competing exit in the hazard's denominator. `06`, `97` and `98` are
**kept** although the current guide no longer lists them: this script reads the *archived*
distributions of the 2014, 2017 and 2019 vintages, which were published under earlier guides and
still carry them, and a retired code that never appears costs nothing while a code that appears and
is not listed here is silently treated as a month survived (DECISIONS D-048, amended)."""

DEFAULT_DELINQUENCY_MONTHS = 6
"""Six months past due is the default definition used here; the loan is censored from then on."""

FRED_DATE_COLUMNS = ("observation_date", "DATE")
FRED_VALUE_COLUMN = "MORTGAGE30US"
"""The two spellings FRED has used for the date column, and the series column."""

PROJECTION_TAIL_MONTHS = 180 + _features.RATE_CHANGE_LAG
"""How far past the last observed rate the calendar is extended flat, so the projection can run."""


def main(argv: list[str] | None = None) -> int:
    """Build the four split panels and the rate calendar, and print the manifest. Exit code."""
    args = parse_args(argv)
    raw_dir, out_dir = Path(args.raw), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rates = read_fred(Path(args.fred).expanduser())
    origination, performance = read_raw(raw_dir, args.years)
    kept = sample_loans(origination, n_loans=args.n_loans, seed=args.seed)
    origination = origination[origination["loan_sequence_number"].isin(kept)]
    performance = performance[performance["loan_sequence_number"].isin(kept)]

    raw_panel = to_raw_panel(origination, performance, rates)
    panel = _features.build_panel(raw_panel, rates)
    masks = _features.split_panel(panel, seed=args.seed)

    manifest = {}
    for name in _features.SPLIT_NAMES:
        part = panel[masks[name]]
        path = out_dir / f"{name}.csv"
        part.to_csv(path, index=False, float_format="%.10g", lineterminator="\n")
        manifest[path.name] = sha256_file(path)
        print(
            f"wrote {path} ({len(part)} loan-months, "
            f"{part[_features.ID_COLUMN].nunique()} loans, event rate "
            f"{part[_features.TARGET_COLUMN].mean():.5f})"
        )
    rates_path = out_dir / "rates.csv"
    rates.to_csv(rates_path, index=False, float_format="%.10g", lineterminator="\n")
    manifest[rates_path.name] = sha256_file(rates_path)
    print(f"wrote {rates_path} ({len(rates)} months)")

    print("\npaste into package.yaml under data:\n")
    print("  manifest:")
    for name, digest in manifest.items():
        print(f'    {name}: "{digest}"')
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the arguments. `--raw` and `--out` are required; nothing is downloaded."""
    parser = argparse.ArgumentParser(
        prog="python sample_freddie.py",
        description=(
            "Build the msr_prepayment panel from the Freddie Mac sample files and the FRED "
            "MORTGAGE30US series. Downloads nothing: point --raw at the directory you unzipped "
            "into and --fred at the exported CSV."
        ),
    )
    parser.add_argument(
        "--raw",
        required=True,
        help=(
            "a directory holding sample_orig_YYYY.txt and sample_svcg_YYYY.txt (or "
            "sample_perf_YYYY.txt) for each vintage"
        ),
    )
    parser.add_argument("--out", required=True, help="where to write the four splits and rates.csv")
    parser.add_argument(
        "--fred",
        default=DEFAULT_FRED_PATH,
        help=f"the FRED MORTGAGE30US CSV (default {DEFAULT_FRED_PATH})",
    )
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        default=list(ORIGINATION_YEARS),
        help=f"the origination years to read (default {' '.join(map(str, ORIGINATION_YEARS))})",
    )
    parser.add_argument(
        "--n-loans",
        type=int,
        default=DEFAULT_N_LOANS,
        help=f"how many loans to keep in total (default {DEFAULT_N_LOANS})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"the sampling and split seed (default {DEFAULT_SEED}, as package.yaml declares)",
    )
    return parser.parse_args(argv)


def _read_pipe_delimited(
    path: Path, layouts: dict[int, tuple[str, tuple[str, ...]]], constants: str
) -> pd.DataFrame:
    """Read one pipe-delimited Freddie Mac file, picking its layout by the field count it has.

    Args:
        path: The file to read.
        layouts: Field count to `(publication, layout)`; :data:`ORIGINATION_LAYOUTS` or
            :data:`PERFORMANCE_LAYOUTS`.
        constants: The names of the tuples to check against, for the refusal message.

    Returns:
        The frame, with the chosen layout's names as its columns.

    Raises:
        SystemExit: The file is missing, or its field count is neither publication's.
    """
    if not path.is_file():
        raise SystemExit(
            f"{path} is missing; unzip the Freddie Mac sample files into --raw keeping their "
            "published names"
        )
    frame = pd.read_csv(path, sep="|", header=None, dtype=str, keep_default_na=False)
    chosen = layouts.get(frame.shape[1])
    if chosen is None:
        known = ", ".join(f"{count} = {release}" for count, (release, _) in sorted(layouts.items()))
        raise SystemExit(
            f"{path} has {frame.shape[1]} fields where the layouts this script implements have "
            f"{known}; Freddie Mac has revised the file layout, so check the current user guide "
            f"against {constants}"
        )
    release, layout = chosen
    print(f"read {path.name} as {release} ({frame.shape[1]} fields)")
    frame.columns = pd.Index(layout)
    return frame


def _performance_path(raw_dir: Path, year: int) -> Path:
    """Return the vintage's performance file under whichever published name is present.

    `sample_svcg_YYYY.txt` is tried first and `sample_perf_YYYY.txt` second. Neither file is
    renamed: a downloaded artefact keeps the name its distribution gave it, so that the digest an
    operator records and the file a reader looks for are the same thing (DECISIONS D-159).

    Args:
        raw_dir: The unzip directory.
        year: The origination year.

    Returns:
        The first of the two names that exists, or the first name when neither does, so that the
        missing-file message in :func:`_read_pipe_delimited` names the one to look for.
    """
    candidates = [raw_dir / stem.format(year=year) for stem in PERFORMANCE_FILE_STEMS]
    return next((path for path in candidates if path.is_file()), candidates[0])


def read_raw(raw_dir: Path, years: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read every vintage's origination and performance file and concatenate each.

    The origination frame gains `origination_year`, taken from the file name rather than from a
    field: a sample file *is* one origination year, which is what makes the stratified draw over
    the three files exactly the stratification `package.yaml` declares.
    """
    if not raw_dir.is_dir():
        raise SystemExit(f"{raw_dir} is not a directory; pass --raw <the unzip directory>")
    originations, performances = [], []
    for year in years:
        origination = _read_pipe_delimited(
            raw_dir / f"sample_orig_{year}.txt",
            ORIGINATION_LAYOUTS,
            "ORIGINATION_LAYOUT_2024 and ORIGINATION_LAYOUT_2026",
        )
        origination["origination_year"] = year
        originations.append(origination)
        performances.append(
            _read_pipe_delimited(
                _performance_path(raw_dir, year),
                PERFORMANCE_LAYOUTS,
                "PERFORMANCE_LAYOUT_2024 and PERFORMANCE_LAYOUT_2026",
            )
        )
    return (
        pd.concat(originations, ignore_index=True),
        pd.concat(performances, ignore_index=True),
    )


def read_fred(path: Path) -> pd.DataFrame:
    """Turn the weekly FRED `MORTGAGE30US` export into the month-close rate calendar.

    The first weekly observation of each month is that month's month-start rate, and is recorded
    as the close of the month before it. The calendar is then extended flat by
    :data:`PROJECTION_TAIL_MONTHS`, because the projection rolls the hazard 180 months past the
    last observed month and a rate path has to exist for it to shock.

    Raises:
        SystemExit: The file is missing, or has neither of the two date column spellings.
    """
    if not path.is_file():
        raise SystemExit(
            f"{path} is missing; export the FRED series {FRED_VALUE_COLUMN} to CSV "
            f"(default location {DEFAULT_FRED_PATH})"
        )
    frame = pd.read_csv(path)
    date_column = next((name for name in FRED_DATE_COLUMNS if name in frame.columns), None)
    if date_column is None or FRED_VALUE_COLUMN not in frame.columns:
        raise SystemExit(
            f"{path} has columns {list(frame.columns)}; a FRED export carries one of "
            f"{list(FRED_DATE_COLUMNS)} and {FRED_VALUE_COLUMN!r}"
        )
    observed = pd.DataFrame(
        {
            "observed": pd.to_datetime(frame[date_column]),
            "rate": pd.to_numeric(frame[FRED_VALUE_COLUMN], errors="coerce"),
        }
    ).dropna()
    observed = observed.sort_values("observed")
    observed["month"] = observed["observed"].dt.year * 100 + observed["observed"].dt.month
    month_start = observed.groupby("month", as_index=False).first()

    periods = [
        _features.add_months(int(month), -1) for month in month_start["month"].to_numpy(dtype=int)
    ]
    calendar = pd.DataFrame(
        {_features.TIME_COLUMN: periods, _features.RATE_COLUMN: month_start["rate"].to_numpy()}
    )
    return _extend_flat(calendar, PROJECTION_TAIL_MONTHS)


def _extend_flat(calendar: pd.DataFrame, months: int) -> pd.DataFrame:
    """Hold the last observed close flat for a further `months`, the flat-forward assumption."""
    last_period = int(calendar[_features.TIME_COLUMN].iloc[-1])
    last_rate = float(calendar[_features.RATE_COLUMN].iloc[-1])
    tail = pd.DataFrame(
        {
            _features.TIME_COLUMN: [
                _features.add_months(last_period, step) for step in range(1, months + 1)
            ],
            _features.RATE_COLUMN: np.full(months, last_rate),
        }
    )
    return pd.concat([calendar, tail], ignore_index=True)


def sample_loans(origination: pd.DataFrame, *, n_loans: int, seed: int) -> np.ndarray:
    """Draw the documented sample: `n_loans` in total, stratified by origination year.

    The draw is over each year's sorted loan sequence numbers, so it depends on the identifiers
    and the seed and not on the order the files happen to be in.
    """
    years = sorted(origination["origination_year"].unique())
    shares = np.full(len(years), n_loans // len(years), dtype=int)
    shares[: n_loans % len(years)] += 1
    rng = np.random.default_rng(seed)
    kept = []
    for year, share in zip(years, shares, strict=True):
        available = np.sort(
            origination.loc[origination["origination_year"] == year, "loan_sequence_number"]
            .unique()
            .astype(str)
        )
        if available.size <= share:
            kept.append(available)
            continue
        kept.append(available[rng.permutation(available.size)[:share]])
    return np.sort(np.concatenate(kept))


def to_raw_panel(
    origination: pd.DataFrame, performance: pd.DataFrame, rates: pd.DataFrame
) -> pd.DataFrame:
    """Map the two Freddie Mac frames into the raw loan-month schema of `code/features.py`.

    The origination month is `monthly_reporting_period` minus `loan_age`, which is Freddie Mac's
    own definition of loan age and is exact; the origination row itself is not in the performance
    file, so it is prepended from the origination record with a closing balance of the original
    unpaid balance and a closing age of zero, which is what gives a loan's first performance month
    a predecessor to lag.

    `prepaid` is 1 in the month whose `zero_balance_code` is
    :data:`VOLUNTARY_PAYOFF_CODE` and 0 everywhere else. A loan is censored -- its months from
    then on dropped -- at a zero-balance code in :data:`CENSORING_CODES`, at a delinquency status
    of :data:`DEFAULT_DELINQUENCY_MONTHS` months or more, and at legal maturity.
    """
    loans = _origination_statics(origination, rates)
    monthly = _performance_months(performance)
    merged = monthly.merge(loans, on="loan_sequence_number", how="inner")
    if merged.empty:
        raise SystemExit(
            "no loan appears in both the origination and the performance files; check that "
            "--raw holds the matching sample_orig_YYYY.txt and sample_svcg_YYYY.txt (or "
            "sample_perf_YYYY.txt) pair"
        )
    merged["orig_period"] = np.array(
        [
            _features.add_months(int(period), -int(age))
            for period, age in zip(
                merged["monthly_reporting_period"].to_numpy(dtype=int),
                merged["loan_age"].to_numpy(dtype=int),
                strict=True,
            )
        ],
        dtype=np.int64,
    )
    kept = _censor(merged)
    origin_rows = _origination_rows(kept, loans)

    body = pd.DataFrame(
        {
            _features.ID_COLUMN: kept["loan_id"].to_numpy(),
            _features.TIME_COLUMN: kept["monthly_reporting_period"].to_numpy(dtype=np.int64),
            "eom_balance": np.where(
                kept["prepaid"].to_numpy() == 1, 0.0, kept["current_actual_upb"].to_numpy()
            ),
            "eom_age": kept["loan_age"].to_numpy(dtype=float),
            _features.TARGET_COLUMN: kept["prepaid"].to_numpy(dtype=int),
            "orig_period": kept["orig_period"].to_numpy(dtype=np.int64),
            "note_rate": kept["note_rate"].to_numpy(dtype=float),
            "sato": kept["sato"].to_numpy(dtype=float),
            "orig_ltv": kept["orig_ltv"].to_numpy(dtype=float),
            "credit_score": kept["credit_score"].to_numpy(dtype=float),
            "orig_upb": kept["orig_upb"].to_numpy(dtype=float),
        }
    )
    panel = pd.concat([origin_rows, body], ignore_index=True)
    return panel.sort_values([_features.ID_COLUMN, _features.TIME_COLUMN], kind="stable")[
        _features.RAW_PANEL_COLUMNS
    ].reset_index(drop=True)


def _origination_statics(origination: pd.DataFrame, rates: pd.DataFrame) -> pd.DataFrame:
    """Map the origination record onto the five `at_origination` quantities plus `orig_upb`.

    `sato` is the note rate minus the market rate at the start of the origination month, which is
    the close of the month before it. `loan_id` is a dense integer, because `splits.json`'s row
    hash and the contract's identifier column are numeric; the mapping is order-independent
    because it is taken over the sorted loan sequence numbers.
    """
    frame = origination.copy()
    frame["loan_sequence_number"] = frame["loan_sequence_number"].astype(str)
    first_payment = pd.to_numeric(frame["first_payment_date"], errors="coerce").to_numpy()
    # The origination month is recovered exactly from the performance file's loan age, and is
    # used everywhere else. Here the first payment date does instead, because SATO is a property
    # of the origination record and this frame has no performance months yet: a loan's first
    # payment falls two months after origination by convention, so the market rate at the start
    # of the origination month is the close of the third month before the first payment.
    close_of_prior = np.array(
        [_features.add_months(int(month), -3) for month in first_payment], dtype=np.int64
    )
    rate_by_period = dict(
        zip(
            rates[_features.TIME_COLUMN].to_numpy(dtype=np.int64),
            rates[_features.RATE_COLUMN].to_numpy(dtype=float),
            strict=True,
        )
    )
    missing = sorted({int(month) for month in close_of_prior if int(month) not in rate_by_period})
    if missing:
        raise SystemExit(
            f"the FRED calendar has no rate for {missing[:5]}, which the SATO of a loan "
            "originated then needs; export a longer MORTGAGE30US history"
        )
    market = np.array([rate_by_period[int(month)] for month in close_of_prior], dtype=float)
    note_rate = pd.to_numeric(frame["orig_interest_rate"], errors="coerce").to_numpy(dtype=float)

    identifiers = {
        sequence: index
        for index, sequence in enumerate(sorted(frame["loan_sequence_number"].unique()), start=1)
    }
    return pd.DataFrame(
        {
            "loan_sequence_number": frame["loan_sequence_number"].to_numpy(),
            "loan_id": frame["loan_sequence_number"].map(identifiers).to_numpy(dtype=np.int64),
            "note_rate": note_rate,
            "sato": note_rate - market,
            "orig_ltv": pd.to_numeric(frame["oltv"], errors="coerce").to_numpy(dtype=float),
            "credit_score": pd.to_numeric(frame["credit_score"], errors="coerce").to_numpy(
                dtype=float
            ),
            "orig_upb": pd.to_numeric(frame["orig_upb"], errors="coerce").to_numpy(dtype=float),
            "orig_loan_term": pd.to_numeric(frame["orig_loan_term"], errors="coerce").to_numpy(
                dtype=float
            ),
        }
    ).dropna()


def _performance_months(performance: pd.DataFrame) -> pd.DataFrame:
    """Keep the performance fields the panel needs, typed, with `prepaid` and the exit flags."""
    frame = pd.DataFrame(
        {
            "loan_sequence_number": performance["loan_sequence_number"].astype(str),
            "monthly_reporting_period": pd.to_numeric(
                performance["monthly_reporting_period"], errors="coerce"
            ),
            "current_actual_upb": pd.to_numeric(performance["current_actual_upb"], errors="coerce"),
            "loan_age": pd.to_numeric(performance["loan_age"], errors="coerce"),
            "remaining_months_to_legal_maturity": pd.to_numeric(
                performance["remaining_months_to_legal_maturity"], errors="coerce"
            ),
            "delinquency": performance["current_loan_delinquency_status"].astype(str).str.strip(),
            "zero_balance_code": performance["zero_balance_code"].astype(str).str.strip(),
        }
    ).dropna(subset=["monthly_reporting_period", "loan_age"])
    frame = frame[frame["loan_age"] >= 1]
    frame["current_actual_upb"] = frame["current_actual_upb"].fillna(0.0)
    frame["prepaid"] = (frame["zero_balance_code"] == VOLUNTARY_PAYOFF_CODE).astype(int)
    frame["defaulted"] = _months_past_due(frame["delinquency"]) >= DEFAULT_DELINQUENCY_MONTHS
    frame["removed"] = frame["zero_balance_code"].isin(CENSORING_CODES)
    frame["matured"] = frame["remaining_months_to_legal_maturity"].fillna(1.0) <= 0.0
    return frame.sort_values(["loan_sequence_number", "monthly_reporting_period"], kind="stable")


def _months_past_due(status: pd.Series) -> pd.Series:
    """Turn Freddie Mac's delinquency status into a month count; `RA` and blanks are not numeric.

    `0` is current, `1` to `n` are months past due, `RA` is a loan in a payment plan and `XX` is
    unknown. Anything that is not a number is treated as not past due, because the only thing the
    count is used for here is the censoring rule, and censoring a loan on an unknown status would
    silently drop the months a servicer could not report on.
    """
    return pd.to_numeric(status, errors="coerce").fillna(0.0)


def _censor(merged: pd.DataFrame) -> pd.DataFrame:
    """Keep each loan's months up to and including its voluntary payoff, and no further.

    A loan that exits for any other reason -- a third-party sale, a repurchase, six months past
    due, legal maturity -- is censored at that month: the month itself is dropped, because what
    happened in it was a competing exit and not a month the loan survived as a prepayment risk.
    """
    exits = merged["removed"] | merged["defaulted"] | merged["matured"]
    first_exit = (
        merged.loc[exits]
        .groupby("loan_sequence_number")["monthly_reporting_period"]
        .min()
        .rename("first_exit")
    )
    first_payoff = (
        merged.loc[merged["prepaid"] == 1]
        .groupby("loan_sequence_number")["monthly_reporting_period"]
        .min()
        .rename("first_payoff")
    )
    frame = merged.merge(first_exit, on="loan_sequence_number", how="left").merge(
        first_payoff, on="loan_sequence_number", how="left"
    )
    before_exit = frame["first_exit"].isna() | (
        frame["monthly_reporting_period"] < frame["first_exit"]
    )
    upto_payoff = frame["first_payoff"].isna() | (
        frame["monthly_reporting_period"] <= frame["first_payoff"]
    )
    return frame[before_exit & upto_payoff].reset_index(drop=True)


def _origination_rows(kept: pd.DataFrame, loans: pd.DataFrame) -> pd.DataFrame:
    """Build the one origination row per loan the performance file does not carry."""
    first = kept.groupby("loan_sequence_number", as_index=False)["orig_period"].min()
    frame = first.merge(loans, on="loan_sequence_number", how="inner")
    return pd.DataFrame(
        {
            _features.ID_COLUMN: frame["loan_id"].to_numpy(dtype=np.int64),
            _features.TIME_COLUMN: frame["orig_period"].to_numpy(dtype=np.int64),
            "eom_balance": frame["orig_upb"].to_numpy(dtype=float),
            "eom_age": np.zeros(len(frame), dtype=float),
            _features.TARGET_COLUMN: np.zeros(len(frame), dtype=int),
            "orig_period": frame["orig_period"].to_numpy(dtype=np.int64),
            "note_rate": frame["note_rate"].to_numpy(dtype=float),
            "sato": frame["sato"].to_numpy(dtype=float),
            "orig_ltv": frame["orig_ltv"].to_numpy(dtype=float),
            "credit_score": frame["credit_score"].to_numpy(dtype=float),
            "orig_upb": frame["orig_upb"].to_numpy(dtype=float),
        }
    )


def sha256_file(path: Path, chunk_bytes: int = 1 << 20) -> str:
    """Return a file's SHA-256 hex digest, the form `package.yaml`'s manifest records."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
