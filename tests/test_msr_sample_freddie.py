"""`sample_freddie.py`: argument handling and the column map, and nothing else.

`CLAUDE.md` forbids a test that downloads data or trains on real data, and spec section 4 says the
real-sample scripts are covered for argument handling only. So `main` is never called here: what
is covered is which arguments the script takes, how it turns the weekly FRED series into the
month-close rate calendar, how it draws its stratified sample, and how it maps the origination and
performance files onto the raw loan-month schema. The three-loan pipe-delimited frames the mapping
tests use are written by the tests themselves and are not the Freddie Mac dataset.

**Every mapping assertion is made against both publications.** The script implements the 2024 user
guide's layouts (32 origination fields, 32 performance fields) and Release 47 of July 2026's (31
and 35), and the `mapped_panel` fixture is parameterised over the two, so each test below runs once
on each. Three checks are about the pair rather than about either: that every column the sampler
reads downstream sits at the same position in both, that the same three loans map to the same panel
through either, and that a width neither release has is refused rather than mapped by position.

The mapping is covered rather than left to the one human run because it is the only place this
project ever interprets a zero-balance code. Code `01` is a voluntary payoff and is the event;
every other code is a competing exit and censors the loan. A subject that counted a repurchase, a
reperforming-loan sale or an REO disposition as a prepayment would report a prepayment model that
fitted beautifully for a reason no reader of the report could see.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
import pytest

RELEASES = ("2024", "2026")
"""The two publications `sample_freddie.py` implements, by the suffix of its layout constants."""

FIELD_COUNTS = {"2024": (32, 32), "2026": (31, 35)}
"""(origination, performance) field counts per release; the only discriminator a header-less file
offers. The 2024 user guide has 32 and 32; Release 47 of July 2026 has 31 and 35."""

DOWNSTREAM_ORIGINATION = (
    "credit_score",
    "first_payment_date",
    "orig_upb",
    "oltv",
    "orig_interest_rate",
    "loan_sequence_number",
    "orig_loan_term",
)
DOWNSTREAM_PERFORMANCE = (
    "loan_sequence_number",
    "monthly_reporting_period",
    "current_actual_upb",
    "current_loan_delinquency_status",
    "loan_age",
    "remaining_months_to_legal_maturity",
    "zero_balance_code",
    "zero_balance_effective_date",
    "current_interest_rate",
)
"""Every column the sampler reads downstream of `read_raw`, by name.

`zero_balance_effective_date` and `current_interest_rate` are not read by `to_raw_panel` today and
are listed all the same: they are the two fields a servicing-value model reaches for next, and the
whole value of a position check is that it is made before the column is needed."""


def origination_layout(msr_sample: ModuleType, release: str) -> tuple[str, ...]:
    """The origination field order of one release, as the script writes it out."""
    layout: tuple[str, ...] = getattr(msr_sample, f"ORIGINATION_LAYOUT_{release}")
    return layout


def performance_layout(msr_sample: ModuleType, release: str) -> tuple[str, ...]:
    """The performance field order of one release, as the script writes it out."""
    layout: tuple[str, ...] = getattr(msr_sample, f"PERFORMANCE_LAYOUT_{release}")
    return layout


def origination_row(
    msr_sample: ModuleType,
    sequence: str,
    *,
    release: str = "2024",
    credit_score: str = "740",
    first_payment: str = "201403",
    orig_upb: str = "200000",
    oltv: str = "80",
    note_rate: str = "4.250",
    term: str = "360",
) -> list[str]:
    """One origination record in one release's published field order, filled with placeholders."""
    layout = list(origination_layout(msr_sample, release))
    row = [""] * len(layout)
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
    release: str = "2024",
    delinquency: str = "0",
    zero_balance: str = "",
    remaining_term: str = "300",
) -> list[str]:
    """One monthly performance record in one release's published field order."""
    layout = list(performance_layout(msr_sample, release))
    row = [""] * len(layout)
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


def three_loan_files(
    msr_sample: ModuleType,
    raw_dir: Path,
    year: int = 2014,
    *,
    release: str = "2024",
    performance_name: str = "sample_svcg_{year}.txt",
) -> None:
    """Write one vintage's pair of files for three loans, each exiting a different way.

    * `F14Q1000001` pays off voluntarily in its fourth month (zero-balance code `01`);
    * `F14Q1000002` is repurchased in its third month (code `06`), so it is censored there;
    * `F14Q1000003` runs six months past due, so it is censored at the sixth.

    Delinquency statuses are written with the leading zeros Release 47 prints -- `00` for current,
    `01` for one month past due -- because that is the form the real files carry and a status read
    as a string is the one thing `_months_past_due` has to get right.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    write_pipe(
        raw_dir / f"sample_orig_{year}.txt",
        [
            origination_row(msr_sample, "F14Q1000001", release=release),
            origination_row(
                msr_sample,
                "F14Q1000002",
                release=release,
                credit_score="700",
                orig_upb="150000",
                oltv="90",
            ),
            origination_row(
                msr_sample,
                "F14Q1000003",
                release=release,
                credit_score="780",
                orig_upb="300000",
                oltv="65",
            ),
        ],
    )
    write_pipe(
        raw_dir / performance_name.format(year=year),
        [
            performance_row(
                msr_sample,
                "F14Q1000001",
                period="201402",
                balance="199900",
                age="1",
                release=release,
                delinquency="00",
            ),
            performance_row(
                msr_sample,
                "F14Q1000001",
                period="201403",
                balance="199800",
                age="2",
                release=release,
                delinquency="00",
            ),
            performance_row(
                msr_sample,
                "F14Q1000001",
                period="201404",
                balance="199700",
                age="3",
                release=release,
                delinquency="00",
            ),
            performance_row(
                msr_sample,
                "F14Q1000001",
                period="201405",
                balance="0",
                age="4",
                release=release,
                delinquency="00",
                zero_balance="01",
            ),
            performance_row(
                msr_sample,
                "F14Q1000002",
                period="201402",
                balance="149900",
                age="1",
                release=release,
                delinquency="00",
            ),
            performance_row(
                msr_sample,
                "F14Q1000002",
                period="201403",
                balance="149800",
                age="2",
                release=release,
                delinquency="00",
            ),
            performance_row(
                msr_sample,
                "F14Q1000002",
                period="201404",
                balance="0",
                age="3",
                release=release,
                delinquency="00",
                zero_balance="06",
            ),
            performance_row(
                msr_sample,
                "F14Q1000003",
                period="201402",
                balance="299900",
                age="1",
                release=release,
                delinquency="00",
            ),
            performance_row(
                msr_sample,
                "F14Q1000003",
                period="201403",
                balance="299800",
                age="2",
                release=release,
                delinquency="01",
            ),
            performance_row(
                msr_sample,
                "F14Q1000003",
                period="201404",
                balance="299700",
                age="3",
                release=release,
                delinquency="06",
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
    for release in RELEASES:
        origination, performance = FIELD_COUNTS[release]
        assert len(origination_layout(msr_sample, release)) == origination
        assert len(performance_layout(msr_sample, release)) == performance


# --- the files it looks for -----------------------------------------------------------------------


def test_a_missing_raw_directory_says_so(msr_sample: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="is not a directory"):
        msr_sample.read_raw(tmp_path / "nowhere", [2014])


def test_a_missing_sample_file_is_named_with_its_published_name(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    with pytest.raises(SystemExit, match="sample_orig_2014.txt is missing"):
        msr_sample.read_raw(tmp_path, [2014])


@pytest.mark.parametrize("fields", [3, 30, 33, 34, 36])
def test_a_layout_of_an_unknown_width_is_refused_rather_than_mapped_by_position(
    msr_sample: ModuleType, tmp_path: Path, fields: int
) -> None:
    """D-048's refusal, unchanged by the second layout: a count neither release has is an exit."""
    write_pipe(tmp_path / "sample_orig_2014.txt", [[str(n) for n in range(fields)]])
    with pytest.raises(SystemExit, match="revised the file layout") as raised:
        msr_sample.read_raw(tmp_path, [2014])
    message = str(raised.value)
    assert "ORIGINATION_LAYOUT_2024 and ORIGINATION_LAYOUT_2026" in message
    assert "31 = Release 47, July 2026" in message and "32 = the 2024 user guide" in message


@pytest.mark.parametrize("release", RELEASES)
def test_the_reader_picks_the_layout_by_field_count_and_names_the_release(
    msr_sample: ModuleType, tmp_path: Path, release: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A header-less file offers one discriminator, and the reader says which one it read."""
    three_loan_files(msr_sample, tmp_path, release=release)
    origination, performance = msr_sample.read_raw(tmp_path, [2014])
    assert list(origination.columns)[:-1] == list(origination_layout(msr_sample, release))
    assert list(performance.columns) == list(performance_layout(msr_sample, release))
    named = {"2024": "the 2024 user guide", "2026": "Release 47, July 2026"}[release]
    printed = capsys.readouterr().out
    assert f"read sample_orig_2014.txt as {named}" in printed
    assert f"read sample_svcg_2014.txt as {named}" in printed


@pytest.mark.parametrize("name", ["sample_svcg_{year}.txt", "sample_perf_{year}.txt"])
def test_either_published_name_of_the_performance_file_is_read(
    msr_sample: ModuleType, tmp_path: Path, name: str
) -> None:
    """D-159: the file is found under whichever name its distribution gave it, never renamed."""
    three_loan_files(msr_sample, tmp_path, performance_name=name)
    _, performance = msr_sample.read_raw(tmp_path, [2014])
    assert len(performance) == 10
    assert (tmp_path / name.format(year=2014)).is_file()
    other = {"sample_svcg_{year}.txt", "sample_perf_{year}.txt"} - {name}
    assert not (tmp_path / other.pop().format(year=2014)).is_file()


def test_the_archived_name_wins_when_a_directory_holds_both(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    """`svcg` is tried first, because that is what the archived vintages carry."""
    three_loan_files(msr_sample, tmp_path, performance_name="sample_svcg_{year}.txt")
    write_pipe(tmp_path / "sample_perf_2014.txt", [["not", "read"]])
    _, performance = msr_sample.read_raw(tmp_path, [2014])
    assert len(performance) == 10
    assert msr_sample._performance_path(tmp_path, 2014).name == "sample_svcg_2014.txt"


def test_a_missing_performance_file_names_the_archived_spelling(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    write_pipe(tmp_path / "sample_orig_2014.txt", [origination_row(msr_sample, "F14Q1000001")])
    with pytest.raises(SystemExit, match="sample_svcg_2014.txt is missing"):
        msr_sample.read_raw(tmp_path, [2014])


@pytest.mark.parametrize("names", [DOWNSTREAM_ORIGINATION, DOWNSTREAM_PERFORMANCE])
def test_every_column_read_downstream_sits_at_the_same_position_in_both_layouts(
    msr_sample: ModuleType, names: tuple[str, ...]
) -> None:
    """The load-bearing check: a layout change that moved one of these would be a silent defect.

    `oltv` and `ocltv` are adjacent and both are plausible loan-to-value numbers (D-048), so the
    question a field count cannot answer is whether the fields this script actually reads are where
    it left them. For these two releases they all are, and this is where that is asserted rather
    than believed.
    """
    which = "origination" if names is DOWNSTREAM_ORIGINATION else "performance"
    layout_for = origination_layout if which == "origination" else performance_layout
    for name in names:
        positions = {
            release: list(layout_for(msr_sample, release)).index(name) for release in RELEASES
        }
        assert len(set(positions.values())) == 1, f"{name} moved between releases: {positions}"


def test_the_origination_year_comes_from_the_file_name(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    three_loan_files(msr_sample, tmp_path)
    origination, performance = msr_sample.read_raw(tmp_path, [2014])
    assert set(origination["origination_year"]) == {2014}
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


@pytest.fixture(params=RELEASES)
def mapped_panel(
    msr_sample: ModuleType, tmp_path: Path, request: pytest.FixtureRequest
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The raw loan-month panel and the rate calendar the three-loan frames map onto.

    Parameterised over both releases, so every assertion below about the column map is made twice:
    once on a 32/32 file pair and once on a 31/35 one. That is what turns the position-invariance
    check into a claim about the mapping and not only about two tuples.
    """
    fred = tmp_path / "MORTGAGE30US.csv"
    fred_csv(fred)
    rates = msr_sample.read_fred(fred)
    name = "sample_svcg_{year}.txt" if request.param == "2024" else "sample_perf_{year}.txt"
    three_loan_files(msr_sample, tmp_path / "raw", release=request.param, performance_name=name)
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


def test_a_leading_zero_delinquency_status_counts_as_the_months_it_names(
    msr_sample: ModuleType,
) -> None:
    """Release 47 prints the status two characters wide: `00`, `01`, ..., with `RA` and `XX`.

    A status read as a string and compared as one would make `"06"` not equal `"6"` and censor
    nothing; `_months_past_due` converts before it compares, so the two forms agree, and this
    asserts that they do on the exact tokens the July 2026 files carry.
    """
    padded = pd.Series(["00", "01", "02", "03", "06", "12", "RA", "XX", ""])
    counted = msr_sample._months_past_due(padded)
    assert counted.tolist() == [0.0, 1.0, 2.0, 3.0, 6.0, 12.0, 0.0, 0.0, 0.0]
    assert (counted >= msr_sample.DEFAULT_DELINQUENCY_MONTHS).tolist() == [
        False,
        False,
        False,
        False,
        True,
        True,
        False,
        False,
        False,
    ]
    unpadded = pd.Series(["0", "1", "2", "3", "6", "12", "RA", "XX", ""])
    assert counted.tolist() == msr_sample._months_past_due(unpadded).tolist()


def test_the_censoring_codes_read_against_the_july_2026_enumeration(
    msr_sample: ModuleType,
) -> None:
    """D-048, amended. The guide lists 01, 02, 03, 09, 15, 16, 96; this list is a superset by three.

    `16`, a reperforming-loan sale, is a disposition and is now censored. `06`, `97` and `98` are
    kept although the current guide no longer lists them, because the archived distributions of the
    2014, 2017 and 2019 vintages still carry them and an unlisted code would silently be read as a
    month the loan survived.
    """
    listed = {"01", "02", "03", "09", "15", "16", "96"}
    censoring = set(msr_sample.CENSORING_CODES)
    assert msr_sample.VOLUNTARY_PAYOFF_CODE == "01"
    assert listed - {msr_sample.VOLUNTARY_PAYOFF_CODE} <= censoring
    assert censoring - listed == {"06", "97", "98"}
    assert "16" in censoring
    assert len(msr_sample.CENSORING_CODES) == len(censoring) == 9


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


def test_the_two_layouts_produce_the_same_panel_from_the_same_loans(
    msr_sample: ModuleType, tmp_path: Path
) -> None:
    """The whole point of the second layout: the same three loans map to the same panel.

    The files differ in width (32/32 against 31/35), in field names and in which member carries
    `servicer_name` and `mi_cancellation_indicator`. Nothing the sampler reads moved, so the raw
    loan-month panel is byte-for-byte the same frame -- which is the claim the position check makes
    about names, made here about values.
    """
    fred = tmp_path / "MORTGAGE30US.csv"
    fred_csv(fred)
    rates = msr_sample.read_fred(fred)
    panels = []
    for release, name in (("2024", "sample_svcg_{year}.txt"), ("2026", "sample_perf_{year}.txt")):
        raw = tmp_path / release
        three_loan_files(msr_sample, raw, release=release, performance_name=name)
        origination, performance = msr_sample.read_raw(raw, [2014])
        panels.append(msr_sample.to_raw_panel(origination, performance, rates))
    pd.testing.assert_frame_equal(panels[0], panels[1])


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
