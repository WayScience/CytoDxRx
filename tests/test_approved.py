"""The role grids of the three real screens, as a person approved them.

Each file in ``tests/approved`` is a drawing of one plate: ``c`` is a compound well,
``d`` a control well and ``.`` an empty well.
A person looked at the drawing and agreed that it is the plate of that screen.
If a change to the code changes a drawing, the test fails and the change is either a
bug or a deliberate change that a person must approve again.
Lines that start with ``#`` are notes and are not compared.
"""

from pathlib import Path

import pytest

from cytodxrx.design import BarcodeColumns, PlatemapColumns, read_design, render_roles

DATA = Path(__file__).parent / "data"
APPROVED = Path(__file__).parent / "approved"

SCREENS = {
    "chp134": (
        384,
        BarcodeColumns("Plate Barcode", "File Name"),
        PlatemapColumns("Well_Position", "Batch_Id", solvent="Solvent"),
    ),
    "sknas": (
        384,
        BarcodeColumns("Plate_Barcode", "File_Name"),
        PlatemapColumns("Well_Position", "Batch_Id", solvent="Solvent"),
    ),
    "cardiac": (
        96,
        BarcodeColumns("plate_barcode", "platemap_file"),
        PlatemapColumns("well_position", "treatment", control_values=("DMSO",)),
    ),
}


@pytest.mark.parametrize("screen", sorted(SCREENS))
def test_the_drawing_of_the_first_plate_is_the_approved_one(screen: str) -> None:
    format_spec, barcode_columns, columns = SCREENS[screen]
    directory = DATA / screen
    design = read_design(
        directory / "barcode_platemap.csv",
        directory,
        format_spec,
        barcode_columns,
        columns,
    )
    drawing = render_roles(design, design["Metadata_Plate"].iloc[0])
    approved = "".join(
        line
        for line in (APPROVED / f"{screen}.txt").read_text().splitlines(keepends=True)
        if not line.startswith("#")
    )
    assert drawing == approved
