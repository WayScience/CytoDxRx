"""Tests for the design table."""

from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from cytodxrx.design import (
    COLUMN,
    COMPOUND,
    DESIGN_COLUMNS,
    PLATE,
    ROLE,
    WELL,
    BarcodeColumns,
    DesignError,
    PlatemapColumns,
    Role,
    assign_role,
    build_design,
    read_design,
    role_problem,
)
from cytodxrx.plate import PLATE_96, PLATE_384

DATA = Path(__file__).parent / "data"
CHP134 = (
    DATA / "chp134",
    BarcodeColumns("Plate Barcode", "File Name"),
    PlatemapColumns("Well_Position", "Batch_Id", solvent="Solvent"),
)
SKNAS = (
    DATA / "sknas",
    BarcodeColumns("Plate_Barcode", "File_Name"),
    PlatemapColumns("Well_Position", "Batch_Id", solvent="Solvent"),
)
CARDIAC = (
    DATA / "cardiac",
    BarcodeColumns("plate_barcode", "platemap_file"),
    PlatemapColumns("well_position", "treatment", control_values=("DMSO",)),
)


@pytest.mark.parametrize(
    ("compound", "solvent", "explicit", "control_values", "role"),
    [
        ("BRD-1", "DMSO", None, (), Role.COMPOUND),
        ("BRD-1", None, None, (), Role.COMPOUND),
        (None, "DMSO", None, (), Role.CONTROL),
        (None, None, None, (), Role.EMPTY),
        ("DMSO", None, None, ("DMSO",), Role.CONTROL),
        ("DMSO", None, None, (), Role.COMPOUND),
        ("BRD-1", "DMSO", "control", (), Role.CONTROL),
        (None, None, " Compound ", (), Role.COMPOUND),
    ],
)
def test_assign_role(
    compound: str | None,
    solvent: str | None,
    explicit: str | None,
    control_values: tuple[str, ...],
    role: Role,
) -> None:
    assert assign_role(compound, solvent, explicit, control_values) is role


def test_assign_role_rejects_an_unknown_explicit_role() -> None:
    with pytest.raises(DesignError, match="unknown role 'blank'"):
        assign_role(None, None, "blank", ())


@given(
    compound=st.none() | st.text(min_size=1, max_size=8),
    solvent=st.none() | st.text(min_size=1, max_size=8),
    control_values=st.lists(st.text(min_size=1, max_size=8), max_size=3),
)
def test_a_derived_role_never_contradicts_its_well(
    compound: str | None, solvent: str | None, control_values: list[str]
) -> None:
    role = assign_role(compound, solvent, None, control_values)
    assert role_problem(role, compound, control_values) is None


@pytest.mark.parametrize(
    ("role", "compound", "message"),
    [
        (Role.COMPOUND, None, "has no compound"),
        (Role.COMPOUND, "DMSO", "holds the control value"),
        (Role.CONTROL, "BRD-1", "holds the compound"),
        (Role.EMPTY, "BRD-1", "an empty well holds"),
    ],
)
def test_role_problem(role: Role, compound: str | None, message: str) -> None:
    assert message in str(role_problem(role, compound, ("DMSO",)))


@pytest.mark.parametrize(
    ("screen", "format_spec", "n_plates"),
    [(CHP134, 384, 2), (SKNAS, 384, 1), (CARDIAC, 96, 2)],
    ids=["CHP-134", "SK-N-AS", "cardiac fibrosis"],
)
def test_design_of_each_screen_matches_its_platemaps(
    screen: tuple, format_spec: int, n_plates: int
) -> None:
    directory, barcode_columns, columns = screen
    design = read_design(
        directory / "barcode_platemap.csv",
        directory,
        format_spec,
        barcode_columns,
        columns,
    )
    wells_per_plate = format_spec
    assert list(design.columns) == list(DESIGN_COLUMNS)
    assert len(design) == n_plates * wells_per_plate
    assert design[PLATE].nunique() == n_plates
    assert not design.duplicated([PLATE, WELL]).any()

    # the counts come from the platemap files, not from the code under test
    name = pd.read_csv(directory / "barcode_platemap.csv", dtype=str).iloc[0, 1]
    platemap = (
        pd.read_csv(directory / name, dtype=str)
        if (directory / name).is_file()
        else (pd.read_csv(directory / f"{name}.csv", dtype=str))
    )
    compounds = platemap[columns.compound].notna()
    if columns.control_values:
        controls = platemap[columns.compound].isin(columns.control_values)
        compounds &= ~controls
    else:
        controls = ~compounds & platemap[columns.solvent].notna()
    first = design[design[PLATE] == design[PLATE].iloc[0]]
    counts = first[ROLE].value_counts().to_dict()
    assert counts.get("compound", 0) == compounds.sum()
    assert counts.get("control", 0) == controls.sum()
    assert counts.get("empty", 0) == wells_per_plate - compounds.sum() - controls.sum()
    assert first.loc[first[ROLE] == "compound", COMPOUND].notna().all()


def test_the_384_well_screens_keep_controls_in_two_columns_apart_from_compounds() -> (
    None
):
    for directory, barcode_columns, columns in (CHP134, SKNAS):
        design = read_design(
            directory / "barcode_platemap.csv", directory, 384, barcode_columns, columns
        )
        controls = set(design.loc[design[ROLE] == "control", COLUMN])
        compounds = set(design.loc[design[ROLE] == "compound", COLUMN])
        assert controls == {2, 24}
        assert compounds == set(range(3, 23))


def test_the_cardiac_fibrosis_design_lists_only_interior_wells() -> None:
    directory, barcode_columns, columns = CARDIAC
    design = read_design(
        directory / "barcode_platemap.csv",
        directory,
        PLATE_96,
        barcode_columns,
        columns,
    )
    listed = design[design[ROLE] != "empty"]
    assert set(listed[COLUMN]) == set(range(2, 12))
    assert set(listed[WELL].str[0]) == set("BCDEFG")


def _platemap(rows: list[tuple[str, str | None, str | None]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["well", "compound", "solvent"])


PLAIN = PlatemapColumns("well", "compound", solvent="solvent")
BARCODES = BarcodeColumns("plate", "map")


def _barcodes(*pairs: tuple[str, str]) -> pd.DataFrame:
    return pd.DataFrame(pairs, columns=["plate", "map"])


def test_wells_that_a_platemap_does_not_list_are_empty() -> None:
    platemap = _platemap([("A01", "BRD-1", "DMSO"), ("A02", None, "DMSO")])
    design = build_design(
        _barcodes(("P1", "m")), {"m": platemap}, (2, 3), BARCODES, PLAIN
    )
    assert list(design[ROLE]) == [
        "compound",
        "control",
        "empty",
        "empty",
        "empty",
        "empty",
    ]
    assert list(design[WELL]) == ["A01", "A02", "A03", "B01", "B02", "B03"]


def test_plates_sharing_a_platemap_get_the_same_design() -> None:
    platemap = _platemap([("A01", "BRD-1", None)])
    design = build_design(
        _barcodes(("P1", "m"), ("P2", "m")), {"m": platemap}, (1, 2), BARCODES, PLAIN
    )
    assert list(design[PLATE]) == ["P1", "P1", "P2", "P2"]
    assert list(design[ROLE]) == ["compound", "empty"] * 2


def test_an_explicit_role_column_decides() -> None:
    platemap = pd.DataFrame(
        {"well": ["A01", "A02"], "compound": [None, None], "role": ["empty", "control"]}
    )
    columns = PlatemapColumns("well", "compound", role="role")
    design = build_design(
        _barcodes(("P1", "m")), {"m": platemap}, (1, 2), BARCODES, columns
    )
    assert list(design[ROLE]) == ["empty", "control"]


@pytest.mark.parametrize(
    ("platemap", "message"),
    [
        (
            _platemap([("A01", None, None), ("A01", None, None)]),
            "listed more than once",
        ),
        (_platemap([("A09", None, None)]), "outside a 2 x 3 plate"),
        (_platemap([("nonsense", None, None)]), "not a well name"),
    ],
)
def test_a_platemap_that_does_not_fit_the_plate_is_an_error(
    platemap: pd.DataFrame, message: str
) -> None:
    with pytest.raises(DesignError, match=message):
        build_design(_barcodes(("P1", "m")), {"m": platemap}, (2, 3), BARCODES, PLAIN)


def test_contradicting_roles_name_the_wells() -> None:
    platemap = pd.DataFrame(
        {
            "well": ["A01", "A02"],
            "compound": ["BRD-1", "BRD-2"],
            "role": ["control", "empty"],
        }
    )
    columns = PlatemapColumns("well", "compound", role="role")
    with pytest.raises(DesignError, match=r"well A01: a control well holds.*well A02"):
        build_design(_barcodes(("P1", "m")), {"m": platemap}, (1, 2), BARCODES, columns)


def test_barcode_table_problems_are_errors() -> None:
    platemap = {"m": _platemap([("A01", None, None)])}
    with pytest.raises(DesignError, match="more than once"):
        build_design(
            _barcodes(("P1", "m"), ("P1", "m")), platemap, (1, 2), BARCODES, PLAIN
        )
    with pytest.raises(DesignError, match="not given"):
        build_design(_barcodes(("P1", "other")), platemap, (1, 2), BARCODES, PLAIN)
    with pytest.raises(DesignError, match="blank"):
        build_design(_barcodes(("P1", "")), platemap, (1, 2), BARCODES, PLAIN)
    with pytest.raises(DesignError, match="has no column"):
        build_design(
            _barcodes(("P1", "m")), platemap, (1, 2), BarcodeColumns("x", "map"), PLAIN
        )
    with pytest.raises(DesignError, match="has no column"):
        build_design(
            _barcodes(("P1", "m")),
            platemap,
            (1, 2),
            BARCODES,
            PlatemapColumns("nope", "compound"),
        )


def test_a_missing_platemap_file_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "barcode.csv").write_text("plate,map\nP1,absent\n")
    with pytest.raises(DesignError, match="no platemap file 'absent'"):
        read_design(tmp_path / "barcode.csv", tmp_path, PLATE_384, BARCODES, PLAIN)


@st.composite
def _experiments(draw: st.DrawFn) -> tuple[int, pd.DataFrame, pd.DataFrame]:
    n_rows, n_columns = draw(st.integers(1, 4)), draw(st.integers(1, 5))
    n_plates = draw(st.integers(1, 3))
    wells = [
        f"{chr(65 + r)}{c + 1:02d}" for r in range(n_rows) for c in range(n_columns)
    ]
    listed = draw(st.lists(st.sampled_from(wells), unique=True, max_size=len(wells)))
    kinds = draw(
        st.lists(
            st.sampled_from(["compound", "control", "blank"]),
            min_size=len(listed),
            max_size=len(listed),
        )
    )
    rows = [
        (
            well,
            f"BRD-{i}" if kind == "compound" else None,
            "DMSO" if kind == "control" else None,
        )
        for i, (well, kind) in enumerate(zip(listed, kinds, strict=True))
    ]
    barcodes = pd.DataFrame(
        {"plate": [f"P{i}" for i in range(n_plates)], "map": ["m"] * n_plates}
    )
    return (n_rows, n_columns), barcodes, _platemap(rows)


@settings(max_examples=25, deadline=None)
@given(_experiments())
def test_every_well_of_every_plate_has_exactly_one_role(experiment: tuple) -> None:
    shape, barcodes, platemap = experiment
    design = build_design(barcodes, {"m": platemap}, shape, BARCODES, PLAIN)
    n_wells = shape[0] * shape[1]
    assert len(design) == len(barcodes) * n_wells
    assert not design.duplicated([PLATE, WELL]).any()
    assert set(design[ROLE]) <= {role.value for role in Role}
    compounds = design.loc[design[ROLE] == "compound", COMPOUND]
    assert compounds.notna().all()
    assert design.loc[design[ROLE] != "compound", COMPOUND].isna().all()
