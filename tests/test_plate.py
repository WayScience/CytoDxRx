"""Tests for plate formats and well names."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cytodxrx.plate import (
    PLATE_96,
    PLATE_384,
    PLATE_1536,
    PlateFormat,
    WellNameError,
    plate_format,
    row_index,
    row_label,
)


@pytest.mark.parametrize(
    ("index", "label"),
    [(0, "A"), (7, "H"), (15, "P"), (25, "Z"), (26, "AA"), (31, "AF"), (701, "ZZ")],
)
def test_row_labels(index: int, label: str) -> None:
    assert row_label(index) == label
    assert row_index(label) == index


@given(st.integers(min_value=0, max_value=100_000))
def test_row_label_and_index_are_inverses(index: int) -> None:
    assert row_index(row_label(index)) == index


@pytest.mark.parametrize("label", ["", "1", "A1", "a-b", "é"])
def test_row_index_rejects_non_letters(label: str) -> None:
    with pytest.raises(ValueError, match="one or more letters"):
        row_index(label)


def test_row_label_rejects_negative_index() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        row_label(-1)


@pytest.mark.parametrize(
    ("format_", "n_wells", "last_well"),
    [(PLATE_96, 96, "H12"), (PLATE_384, 384, "P24"), (PLATE_1536, 1536, "AF48")],
)
def test_standard_plates(format_: PlateFormat, n_wells: int, last_well: str) -> None:
    wells = format_.wells()
    assert len(wells) == n_wells == format_.n_wells
    assert len(set(wells)) == n_wells
    assert wells[0] == "A01"
    assert wells[-1] == last_well


def test_parse_accepts_unpadded_and_lowercase_names() -> None:
    assert PLATE_384.parse("A01") == (0, 0)
    assert PLATE_384.parse("a1") == (0, 0)
    assert PLATE_384.parse(" P24 ") == (15, 23)
    assert PLATE_384.normalize("b2") == "B02"


@pytest.mark.parametrize("well", ["", "A", "01", "A-1", "A01B", 5, None])
def test_parse_rejects_malformed_names(well: object) -> None:
    with pytest.raises(WellNameError, match="not a well name"):
        PLATE_384.parse(well)  # type: ignore[arg-type]


@pytest.mark.parametrize("well", ["I01", "A0", "A13", "A99"])
def test_the_96_well_plate_rejects_wells_outside_it(well: str) -> None:
    with pytest.raises(WellNameError, match="outside a 8 x 12 plate"):
        PLATE_96.parse(well)


@given(
    n_rows=st.integers(min_value=1, max_value=40),
    n_columns=st.integers(min_value=1, max_value=60),
    data=st.data(),
)
def test_name_and_parse_are_inverses(
    n_rows: int, n_columns: int, data: st.DataObject
) -> None:
    format_ = PlateFormat(n_rows, n_columns)
    row = data.draw(st.integers(min_value=0, max_value=n_rows - 1))
    column = data.draw(st.integers(min_value=0, max_value=n_columns - 1))
    assert format_.parse(format_.name(row, column)) == (row, column)


@pytest.mark.parametrize("format_", [PLATE_96, PLATE_384, PLATE_1536])
def test_name_accepts_the_last_well_and_rejects_the_ones_just_past_it(
    format_: PlateFormat,
) -> None:
    last_row, last_column = format_.n_rows - 1, format_.n_columns - 1
    assert format_.parse(format_.name(last_row, last_column)) == (last_row, last_column)
    for row, column in [
        (format_.n_rows, 0),
        (0, format_.n_columns),
        (-1, 0),
        (0, -1),
        (format_.n_rows, format_.n_columns),
    ]:
        with pytest.raises(WellNameError, match="outside"):
            format_.name(row, column)


def test_the_96_well_names_match_an_independent_list() -> None:
    expected = [f"{row}{column:02d}" for row in "ABCDEFGH" for column in range(1, 13)]
    assert PLATE_96.wells() == expected


def test_a_plate_needs_rows_and_columns() -> None:
    with pytest.raises(ValueError, match="needs rows and columns"):
        PlateFormat(0, 12)


def test_plate_format_from_a_well_count_or_dimensions() -> None:
    assert plate_format(96) == PLATE_96
    assert plate_format(384) == PLATE_384
    assert plate_format((4, 6)) == PlateFormat(4, 6)
    assert plate_format(PLATE_96) is PLATE_96
    with pytest.raises(ValueError, match="not a standard plate"):
        plate_format(100)
