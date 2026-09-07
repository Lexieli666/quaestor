"""`sample_freddie.py`: argument handling and the column map, and nothing else.

`CLAUDE.md` forbids a test that downloads data or trains on real data, and spec section 4 says the
real-sample scripts are covered for argument handling only. So `main` is never called here: what
is covered is which arguments the script takes, how it turns the weekly FRED series into the
month-close rate calendar, how it draws its stratified sample, and how it maps the two Freddie Mac
layouts onto the raw loan-month schema. The three-loan pipe-delimited frames the mapping tests use
are written by the tests themselves and are not the Freddie Mac dataset.

The mapping is covered rather than left to the one human run because it is the only place this
project ever interprets a zero-balance code. Code `01` is a voluntary payoff and is the event;
every other code is a competing exit and censors the loan. A subject that counted a repurchase or
an REO disposition as a prepayment would report a prepayment model that fitted beautifully for a
reason no reader of the report could see.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
import pytest

ORIGINATION_FIELDS = 32
PERFORMANCE_FIELDS = 32
"""The two layouts the script implements, checked against the constants it exports."""


def origination_row(
    msr_sample: ModuleType,
    sequence: str,
    *,
    credit_score: str = "740",
    first_payment: str = "201403",
    orig_upb: str = "200000",
    oltv: str = "80",
    note_rate: str = "4.250",
    term: str = "360",
) -> list[str]:
    """One origination record in the published field order, filled with placeholders."""
    row = [""] * len(msr_sample.ORIGINATION_LAYOUT)
    layout = list(msr_sample.ORIGINATION_LAYOUT)
    row[layout.index("credit_score")] = credit_score
    row[layout.index("first_payment_date")] = first_payment
    row[layout.index("maturity_date")] = "204402"
    row[layout.index("orig_upb")] = orig_upb
    row[layout.index("oltv")] = oltv
    row[layout.index("orig_interest_rate")] = note_rate
    row[layout.index("loan_sequence_number")] = sequence
    row[layout.index("orig_loan_term")] = term
    return row


def performance_row(
    msr_sample: ModuleType,
    sequence: str,
    *,
    period: str,
    balance: str,
    age: str,
    delinquency: str = "0",
    zero_balance: str = "",
    remaining_term: str = "300",
) -> list[str]:
    """One monthly performance record in the published field order."""
    row = [""] * len(msr_sample.PERFORMANCE_LAYOUT)
    layout = list(msr_sample.PERFORMANCE_LAYOUT)
    row[layout.index("loan_sequence_number")] = sequence
    row[layout.index("monthly_reporting_period")] = period
    row[layout.index("current_actual_upb")] = balance
    row[layout.index("current_loan_delinquency_status")] = delinquency
    row[layout.index("loan_age")] = age
    row[layout.index("remaining_months_to_legal_maturity")] = remaining_term
    row[layout.index("zero_balance_code")] = zero_balance
    return row


def write_pipe(path: Path, rows: list[list[str]]) -> None:
    """Write a pipe-delimited, header-less file, which is what Freddie Mac distributes."""
    path.write_text("\n".join("|".join(row) for row in rows) + "\n", encoding="utf-8")


def three_loan_files(msr_sample: ModuleType, raw_dir: Path, year: int = 2014) -> None:
    """Write one vintage's pair of files for three loans, each exiting a different way.

    * `F14Q1000001` pays off voluntarily in its fourth month (zero-balance code `01`);
    * `F14Q1000002` is repurchased in its third month (code `06`), so it is censored there;
    * `F14Q1000003` runs six months past due, so it is censored at the sixth.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    write_pipe(
        raw_dir / f"sample_orig_{year}.txt",
        [
            origination_row(msr_sample, "F14Q1000001"),
            origination_row(
                msr_sample, "F14Q1000002", credit_score="700", orig_upb="150000", oltv="90"
            ),
            origination_row(
                msr_sample, "F14Q1000003", credit_score="780", orig_upb="300000", oltv="65"
            ),
        ],
    )
    write_pipe(
        raw_dir / f"sample_svcg_{year}.txt",
        [
            performance_row(msr_sample, "F14Q1000001", period="201402", balance="199900", age="1"),
            performance_row(msr_sample, "F14Q1000001", period="201403", balance="199800", age="2"),
            performance_row(msr_sample, "F14Q1000001", period="201404", balance="199700", age="3"),
            performance_row(
                msr_sample,
                "F14Q1000001",
                period="201405",
                balance="0",
                age="4",
                zero_balance="01",
            ),
            performance_row(msr_sample, "F14Q1000002", period="201402", balance="149900", age="1"),
            performance_row(msr_sample, "F14Q1000002", period="201403", balance="149800", age="2"),
            performance_row(
                msr_sample,
                "F14Q1000002",
                period="201404",
                balance="0",
                age="3",
                zero_balance="06",
            ),
            performance_row(msr_sample, "F14Q1000003", period="201402", balance="299900", age="1"),
            performance_row(
                msr_sample,
                "F14Q1000003",
                period="201403",
                balance="299800",
                age="2",
                delinquency="1",
            ),
            performance_row(
                msr_sample,
                "F14Q1000003",
                period="201404",
                balance="299700",
                age="3",
                delinquency="6",
            ),
        ],
    )


def fred_csv(path: Path, *, column: str = "observation_date") -> None:
    """Write a weekly MORTGAGE30US export covering 2012 to 2015, four observations a month."""
    dates, values = [], []
    rate = 4.0
    for year in range(2012, 2016):
        for month in range(1, 13):
            for day in (2, 9, 16, 23):
                dates.append(f"{year}-{month:02d}-{day:02d}")
                values.append(round(rate, 3))
                rate += 0.01
    pd.DataFrame({column: dates, "MORTGAGE30US": values}).to_csv(path, index=False)


# --- the arguments --------------------------------------------------------------------------------


def test_the_defaults_are_the_declared_sample_rule(msr_sample: ModuleType) -> None:
    args = msr_sample.parse_args(["--raw", "in", "--out", "out"])
    assert args.n_loans == 20_000
    assert args.seed == 20260901
    assert args.years == [2014, 2017, 2019]
    assert args.fred == msr_sample.DEFAULT_FRED_PATH
    assert args.fred.endswith("MORTGAGE30US.csv")


def test_both_directories_are_required(msr_sample: ModuleType) -> None:
    with pytest.raises(SystemExit):
        msr_sample.parse_args(["--raw", "in"])
    with pytest.raises(SystemExit):
        msr_sample.parse_args(["--out", "out"])
    with pytest.raises(SystemExit):
        msr_sample.parse_args([])


def test_a_smaller_sample_another_seed_and_other_years_can_be_asked_for(
    msr_sample: ModuleType,
) -> None:
    args = msr_sample.parse_args(
        [
            "--raw",
            "in",
            "--out",
            "out",
            "--fred",
            "/tmp/m.csv",
            "--years",
            "2014",
            "2019",
            "--n-loans",
            "500",
            "--seed",
            "7",
        ]
    )
    assert (args.n_loans, args.seed, args.years, args.fred) == (500, 7, [2014, 2019], "/tmp/m.csv")


def test_the_declared_sample_rule_is_the_one_package_yaml_states(msr_sample: ModuleType) -> None:
    assert msr_sample.ORIGINATION_YEARS == (2014, 2017, 2019)
    assert msr_sample.DEFAULT_N_LOANS == 20_000
    assert msr_sample.DEFAULT_SEED == 20260901
    assert msr_sample.VOLUNTARY_PAYOFF_CODE == "01"
    assert "01" not in msr_sample.CENSORING_CODES
    assert len(msr_sample.ORIGINATION_LAYOUT) == ORIGINATION_FIELDS
    assert len(msr_sample.PERFORMANCE_LAYOUT) == PERFORMANCE_FIELDS


# --- the files it looks for -----------------------------------------------------------------------


def test_a_missing_raw_directory_says_so(msr_sample: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="is not a directory"):
        msr_sample.read_raw(tmp_path / "nowhere", [2014])


def test_a_missing_sample_file_is_named_with_its_published_name(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    with pytest.raises(SystemExit, match="sample_orig_2014.txt is missing"):
        msr_sample.read_raw(tmp_path, [2014])


def test_a_revised_layout_is_refused_rather_than_mapped_by_position(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    write_pipe(tmp_path / "sample_orig_2014.txt", [["a", "b", "c"]])
    with pytest.raises(SystemExit, match="revised the file layout"):
        msr_sample.read_raw(tmp_path, [2014])


def test_the_origination_year_comes_from_the_file_name(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    three_loan_files(msr_sample, tmp_path)
    origination, performance = msr_sample.read_raw(tmp_path, [2014])
    assert set(origination["origination_year"]) == {2014}
    assert list(origination.columns)[:-1] == list(msr_sample.ORIGINATION_LAYOUT)
    assert list(performance.columns) == list(msr_sample.PERFORMANCE_LAYOUT)
    assert len(origination) == 3
    assert len(performance) == 10


# --- the FRED calendar ----------------------------------------------------------------------------


@pytest.mark.parametrize("column", ["observation_date", "DATE"])
def test_the_first_observation_of_a_month_becomes_the_previous_months_close(
    msr_sample: ModuleType, msr_features: ModuleType, tmp_path: Path, column: str
) -> None:
    path = tmp_path / "MORTGAGE30US.csv"
    fred_csv(path, column=column)
    calendar = msr_sample.read_fred(path)
    weekly = pd.read_csv(path)
    first_of_march = float(weekly.loc[weekly[column] == "2013-03-02", "MORTGAGE30US"].iloc[0])
    february = calendar[calendar[msr_features.TIME_COLUMN] == 201302]
    close_of_february = float(february[msr_features.RATE_COLUMN].iloc[0])
    assert close_of_february == pytest.approx(first_of_march)
    # No gap and no repeat, which is what `rate_lookup` insists on.
    assert msr_features.rate_lookup(calendar)[0].size == len(calendar)


def test_the_calendar_is_extended_flat_far_enough_for_the_projection(
    msr_sample: ModuleType, msr_features: ModuleType, tmp_path: Path
) -> None:
    path = tmp_path / "MORTGAGE30US.csv"
    fred_csv(path)
    calendar = msr_sample.read_fred(path)
    assert msr_sample.PROJECTION_TAIL_MONTHS == 180 + msr_features.RATE_CHANGE_LAG
    tail = calendar.tail(msr_sample.PROJECTION_TAIL_MONTHS)
    assert tail[msr_features.RATE_COLUMN].nunique() == 1
    # The last observed month is 2015-12, whose close is the first print of 2016 -- which the
    # export does not have -- so the calendar ends at 2015-11 plus the flat tail.
    assert int(calendar[msr_features.TIME_COLUMN].iloc[-1]) == msr_features.add_months(
        201511, msr_sample.PROJECTION_TAIL_MONTHS
    )


def test_a_missing_or_unrecognised_fred_export_says_what_it_wanted(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    with pytest.raises(SystemExit, match="MORTGAGE30US"):
        msr_sample.read_fred(tmp_path / "nowhere.csv")
    wrong = tmp_path / "wrong.csv"
    pd.DataFrame({"when": ["2014-01-02"], "value": [4.0]}).to_csv(wrong, index=False)
    with pytest.raises(SystemExit, match="a FRED export carries"):
        msr_sample.read_fred(wrong)


# --- the stratified draw --------------------------------------------------------------------------


def test_the_draw_is_stratified_by_origination_year_and_seeded(msr_sample: ModuleType) -> None:
    origination = pd.DataFrame(
        {
            "loan_sequence_number": [
                f"F{year}Q{index:06d}" for year in (14, 17, 19) for index in range(100)
            ],
            "origination_year": [2000 + year for year in (14, 17, 19) for _ in range(100)],
        }
    )
    kept = msr_sample.sample_loans(origination, n_loans=30, seed=20260901)
    assert kept.size == 30
    picked = origination[origination["loan_sequence_number"].isin(kept)]
    assert picked["origination_year"].value_counts().to_dict() == {2014: 10, 2017: 10, 2019: 10}
    again = msr_sample.sample_loans(origination, n_loans=30, seed=20260901)
    assert list(kept) == list(again)
    other = msr_sample.sample_loans(origination, n_loans=30, seed=11)
    assert list(kept) != list(other)


def test_asking_for_more_loans_than_a_vintage_has_keeps_all_of_it(
    msr_sample: ModuleType,
) -> None:
    origination = pd.DataFrame(
        {
            "loan_sequence_number": ["a", "b", "c", "d"],
            "origination_year": [2014, 2014, 2019, 2019],
        }
    )
    assert list(msr_sample.sample_loans(origination, n_loans=100, seed=1)) == ["a", "b", "c", "d"]


def test_the_draw_ignores_the_order_the_files_happen_to_be_in(msr_sample: ModuleType) -> None:
    origination = pd.DataFrame(
        {
            "loan_sequence_number": [f"F14Q{index:06d}" for index in range(50)],
            "origination_year": [2014] * 50,
        }
    )
    shuffled = origination.iloc[np.random.default_rng(9).permutation(50)].reset_index(drop=True)
    assert list(msr_sample.sample_loans(origination, n_loans=10, seed=3)) == list(
        msr_sample.sample_loans(shuffled, n_loans=10, seed=3)
    )


# --- the column map -------------------------------------------------------------------------------


@pytest.fixture
def mapped_panel(msr_sample: ModuleType, tmp_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The raw loan-month panel and the rate calendar the three-loan frames map onto."""
    fred = tmp_path / "MORTGAGE30US.csv"
    fred_csv(fred)
    rates = msr_sample.read_fred(fred)
    three_loan_files(msr_sample, tmp_path / "raw")
    origination, performance = msr_sample.read_raw(tmp_path / "raw", [2014])
    return msr_sample.to_raw_panel(origination, performance, rates), rates


def test_the_freddie_columns_become_the_raw_loan_month_schema(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    panel, _ = mapped_panel
    assert list(panel.columns) == msr_features.RAW_PANEL_COLUMNS
    assert set(panel[msr_features.ID_COLUMN]) == {1, 2, 3}
    first = panel[panel[msr_features.ID_COLUMN] == 1].sort_values(msr_features.TIME_COLUMN)
    assert first["note_rate"].unique().tolist() == [4.25]
    assert first["orig_ltv"].unique().tolist() == [80.0]
    assert first["credit_score"].unique().tolist() == [740.0]
    assert first["orig_upb"].unique().tolist() == [200000.0]


def test_the_origination_month_is_the_reporting_period_minus_the_loan_age(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    panel, _ = mapped_panel
    assert set(panel["orig_period"]) == {201401}
    # The performance file starts at loan age 1; the origination row is prepended, so every loan
    # has a month whose closing age is zero and whose closing balance is the original balance.
    origination = panel[panel["eom_age"] == 0.0]
    assert set(origination[msr_features.TIME_COLUMN]) == {201401}
    assert origination["eom_balance"].tolist() == [200000.0, 150000.0, 300000.0]


def test_only_zero_balance_code_01_is_the_event(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    panel, _ = mapped_panel
    events = panel[panel[msr_features.TARGET_COLUMN] == 1]
    assert events[msr_features.ID_COLUMN].tolist() == [1]
    assert events[msr_features.TIME_COLUMN].tolist() == [201405]
    assert events["eom_balance"].tolist() == [0.0]


def test_a_repurchase_censors_the_loan_at_that_month(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    panel, _ = mapped_panel
    second = panel[panel[msr_features.ID_COLUMN] == 2]
    # Its origination month plus the two months before the repurchase, and not the repurchase.
    assert second[msr_features.TIME_COLUMN].tolist() == [201401, 201402, 201403]
    assert second[msr_features.TARGET_COLUMN].sum() == 0


def test_six_months_past_due_censors_the_loan_at_that_month(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    panel, _ = mapped_panel
    third = panel[panel[msr_features.ID_COLUMN] == 3]
    assert third[msr_features.TIME_COLUMN].tolist() == [201401, 201402, 201403]
    assert third[msr_features.TARGET_COLUMN].sum() == 0


def test_a_non_numeric_delinquency_status_is_not_a_default(msr_sample: ModuleType) -> None:
    status = pd.Series(["0", "1", "RA", "XX", "", "6"])
    counted = msr_sample._months_past_due(status)
    assert counted.tolist() == [0.0, 1.0, 0.0, 0.0, 0.0, 6.0]
    assert msr_sample.DEFAULT_DELINQUENCY_MONTHS == 6


def test_sato_is_the_note_rate_minus_the_rate_at_origination(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    panel, rates = mapped_panel
    # The first payment is 2014-03, so origination is 2014-01 and the market rate at its start is
    # the close of 2013-12, which is the first print of 2014-01.
    market = float(
        rates.loc[rates[msr_features.TIME_COLUMN] == 201312, msr_features.RATE_COLUMN].iloc[0]
    )
    sato = panel["sato"].unique()
    assert sato.tolist() == [pytest.approx(4.25 - market)]


def test_the_mapped_panel_feeds_the_subjects_own_panel_builder(
    mapped_panel: tuple[pd.DataFrame, pd.DataFrame], msr_features: ModuleType
) -> None:
    # The point of the map: what it produces is what `code/features.py` consumes, in both modes.
    panel, rates = mapped_panel
    built = msr_features.build_panel(panel, rates)
    assert list(built.columns) == [
        msr_features.ID_COLUMN,
        msr_features.TIME_COLUMN,
        "orig_period",
        *msr_features.FEATURE_NAMES,
        msr_features.REGIME_COLUMN,
        msr_features.TARGET_COLUMN,
    ]
    assert built[msr_features.TARGET_COLUMN].sum() == 1
    assert not built.isna().to_numpy().any()


def test_loans_in_only_one_of_the_two_files_are_dropped_with_a_message(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    fred = tmp_path / "MORTGAGE30US.csv"
    fred_csv(fred)
    rates = msr_sample.read_fred(fred)
    three_loan_files(msr_sample, tmp_path / "raw")
    origination, performance = msr_sample.read_raw(tmp_path / "raw", [2014])
    orphaned = origination.copy()
    orphaned["loan_sequence_number"] = "F99Q1000001"
    with pytest.raises(SystemExit, match="no loan appears in both"):
        msr_sample.to_raw_panel(orphaned, performance, rates)


def test_a_fred_calendar_that_does_not_reach_the_origination_month_says_so(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    fred = tmp_path / "MORTGAGE30US.csv"
    fred_csv(fred)
    rates = msr_sample.read_fred(fred)
    three_loan_files(msr_sample, tmp_path / "raw")
    origination, _ = msr_sample.read_raw(tmp_path / "raw", [2014])
    short = rates[rates["period"] >= 201406]
    with pytest.raises(SystemExit, match="has no rate for"):
        msr_sample._origination_statics(origination, short)


def test_the_digest_is_the_sha256_of_the_file(msr_sample: ModuleType, tmp_path: Path) -> None:
    import hashlib

    path = tmp_path / "train.csv"
    path.write_bytes(b"loan_id,period\n1,201402\n")
    assert msr_sample.sha256_file(path) == hashlib.sha256(path.read_bytes()).hexdigest()
