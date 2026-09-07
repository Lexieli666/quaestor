"""`sample.py`: argument handling and the UCI column map, and nothing else.

`CLAUDE.md` forbids a test that downloads data or trains on real data, and spec section 4 says the
real-sample scripts are covered for argument handling only. So `main` is never called here: what
is covered is which input file the script chooses, what it says when there is none, and how it
renames the UCI columns into the canonical raw schema. The three-row frame the mapping tests use
is written by the test itself and is not the UCI dataset.

The mapping is covered rather than left to the one human run because it is the only place the
project ever interprets `PAY_0`: a repayment status of -2, -1 or 0 is not a month past due, and a
subject whose delinquency features counted those would look excellent on the real sample for a
reason no reader could see.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pandas as pd
import pytest

UCI_HEADER = [
    "ID",
    "LIMIT_BAL",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
    *[f"BILL_AMT{index}" for index in range(1, 7)],
    *[f"PAY_AMT{index}" for index in range(1, 7)],
    "default payment next month",
]


UCI_ROWS = (
    # ID, LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE, then PAY_0 and PAY_2..PAY_6,
    # then BILL_AMT1..6, then PAY_AMT1..6, then the target.
    (1, 20000, 2, 2, 1, 24)
    + (2, 2, -1, -1, -2, -2)
    + (3913, 3102, 689, 0, 0, 0)
    + (0, 689, 0, 0, 0, 0)
    + (1,),
    (2, 120000, 2, 2, 2, 26)
    + (-1, 2, 0, 0, 0, 2)
    + (2682, 1725, 2682, 3272, 3455, 3261)
    + (0, 1000, 1000, 1000, 0, 2000)
    + (1,),
    (3, 90000, 2, 2, 2, 34)
    + (0, 0, 0, 0, 0, 0)
    + (29239, 14027, 13559, 14331, 14948, 15549)
    + (1518, 1500, 1000, 1000, 1000, 5000)
    + (0,),
)


def uci_shaped_frame() -> pd.DataFrame:
    """Three rows in the UCI layout, written here; not the UCI dataset."""
    return pd.DataFrame(list(UCI_ROWS), columns=UCI_HEADER)


# --- which file the script reads -----------------------------------------------------------------


def test_a_missing_raw_directory_says_so(credit_sample: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="is not a directory"):
        credit_sample.resolve_source(tmp_path / "nowhere")


def test_an_empty_raw_directory_names_both_input_forms(
    credit_sample: ModuleType, tmp_path: Path
) -> None:
    with pytest.raises(SystemExit) as raised:
        credit_sample.resolve_source(tmp_path)
    message = str(raised.value)
    assert credit_sample.CSV_NAME in message
    assert credit_sample.XLS_NAME in message
    assert "350" in message


def test_the_csv_export_is_preferred_over_the_legacy_xls(
    credit_sample: ModuleType, tmp_path: Path
) -> None:
    (tmp_path / credit_sample.CSV_NAME).write_text("ID\n1\n")
    (tmp_path / credit_sample.XLS_NAME).write_bytes(b"\xd0\xcf\x11\xe0not really an xls")
    assert credit_sample.resolve_source(tmp_path).name == credit_sample.CSV_NAME


def test_an_xls_without_xlrd_tells_the_operator_to_export_a_csv_once(
    credit_sample: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / credit_sample.XLS_NAME).write_bytes(b"\xd0\xcf\x11\xe0not really an xls")
    monkeypatch.setattr(credit_sample, "xlrd_available", lambda: False)
    with pytest.raises(SystemExit) as raised:
        credit_sample.resolve_source(tmp_path)
    assert "xlrd" in str(raised.value)
    assert credit_sample.CSV_NAME in str(raised.value)


def test_an_xls_with_xlrd_is_read_directly(
    credit_sample: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / credit_sample.XLS_NAME).write_bytes(b"\xd0\xcf\x11\xe0not really an xls")
    monkeypatch.setattr(credit_sample, "xlrd_available", lambda: True)
    assert credit_sample.resolve_source(tmp_path).name == credit_sample.XLS_NAME


def test_whether_xlrd_is_importable_is_a_plain_question(credit_sample: ModuleType) -> None:
    assert credit_sample.xlrd_available() in (True, False)


# --- the arguments -------------------------------------------------------------------------------


def test_the_defaults_are_the_declared_seed_and_the_whole_dataset(
    credit_sample: ModuleType,
) -> None:
    args = credit_sample.parse_args(["--raw", "in", "--out", "out"])
    assert args.seed == 20260901
    assert args.max_clients is None
    assert (args.raw, args.out) == ("in", "out")


def test_both_directories_are_required(credit_sample: ModuleType) -> None:
    with pytest.raises(SystemExit):
        credit_sample.parse_args(["--raw", "in"])
    with pytest.raises(SystemExit):
        credit_sample.parse_args([])


def test_a_smaller_sample_and_another_seed_can_be_asked_for(credit_sample: ModuleType) -> None:
    args = credit_sample.parse_args(
        ["--raw", "in", "--out", "out", "--seed", "7", "--max-clients", "500"]
    )
    assert (args.seed, args.max_clients) == (7, 500)


# --- the UCI column map --------------------------------------------------------------------------


def test_the_uci_columns_become_the_canonical_raw_schema(credit_sample: ModuleType) -> None:
    canonical = credit_sample.to_canonical(uci_shaped_frame())
    features = credit_sample._features
    assert list(canonical.columns) == [*features.RAW_COLUMNS, features.TARGET_COLUMN]
    assert canonical["client_id"].tolist() == [1, 2, 3]
    assert canonical["limit_bal"].tolist() == [20000.0, 120000.0, 90000.0]
    assert canonical["bill_amt_1"].tolist() == [3913.0, 2682.0, 29239.0]
    assert canonical["pay_amt_6"].tolist() == [0.0, 2000.0, 5000.0]
    assert canonical[features.TARGET_COLUMN].tolist() == [1, 1, 0]


def test_a_repayment_status_below_one_is_not_a_month_past_due(
    credit_sample: ModuleType,
) -> None:
    canonical = credit_sample.to_canonical(uci_shaped_frame())
    # Row 1 is PAY_0..PAY_6 = 2, 2, -1, -1, -2, -2: two months past due, then paid or unused.
    assert canonical.loc[0, ["delinq_1", "delinq_2", "delinq_3"]].tolist() == [2, 2, 0]
    assert canonical.loc[0, ["delinq_4", "delinq_5", "delinq_6"]].tolist() == [0, 0, 0]
    # Row 2 is -1, 2, 0, 0, 0, 2.
    assert canonical.loc[1, [f"delinq_{index}" for index in range(1, 7)]].tolist() == [
        0,
        2,
        0,
        0,
        0,
        2,
    ]


def test_the_repayment_status_columns_keep_their_uci_order(credit_sample: ModuleType) -> None:
    frame = uci_shaped_frame()
    frame[["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]] = [
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
    ]
    canonical = credit_sample.to_canonical(frame)
    assert canonical.loc[0, [f"delinq_{index}" for index in range(1, 7)]].tolist() == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_a_file_with_no_target_column_says_which_names_it_looked_for(
    credit_sample: ModuleType,
) -> None:
    frame = uci_shaped_frame().drop(columns=["default payment next month"])
    with pytest.raises(SystemExit, match="no target column"):
        credit_sample.to_canonical(frame)


def test_the_other_two_spellings_of_the_target_are_accepted(credit_sample: ModuleType) -> None:
    for spelling in ("default.payment.next.month", "Y"):
        frame = uci_shaped_frame().rename(columns={"default payment next month": spelling})
        assert credit_sample.to_canonical(frame).shape[0] == 3


def test_a_file_missing_a_uci_column_names_it(credit_sample: ModuleType) -> None:
    frame = uci_shaped_frame().drop(columns=["BILL_AMT4", "PAY_5"])
    with pytest.raises(SystemExit, match="BILL_AMT4"):
        credit_sample.to_canonical(frame)


def test_a_header_row_of_placeholders_is_read_past(
    credit_sample: ModuleType, tmp_path: Path
) -> None:
    path = tmp_path / credit_sample.CSV_NAME
    placeholders = ",".join(["X" + str(index) for index in range(1, len(UCI_HEADER) + 1)])
    row = "1,2000,2,2,1,24" + ",0" * 18
    path.write_text(placeholders + "\n" + ",".join(UCI_HEADER) + "\n" + row + "\n")
    frame = credit_sample.read_raw(path)
    assert "LIMIT_BAL" in frame.columns


def test_a_csv_with_the_real_header_is_read_as_it_is(
    credit_sample: ModuleType, tmp_path: Path
) -> None:
    path = tmp_path / credit_sample.CSV_NAME
    uci_shaped_frame().to_csv(path, index=False)
    frame = credit_sample.read_raw(path)
    assert list(frame.columns) == UCI_HEADER
    assert len(frame) == 3
