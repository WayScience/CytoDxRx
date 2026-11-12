"""The design table: what is in every well of every plate.

CytoDxRx builds the design table from the platemaps.
It has one row per well of every plate, and every well has exactly one role:
``compound``, ``control`` or ``empty``.
"""

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import pandas as pd

from cytodxrx.plate import PlateFormat, WellNameError, plate_format, row_label

PLATE = "Metadata_Plate"
WELL = "Metadata_Well"
ROW = "Metadata_Row"
COLUMN = "Metadata_Column"
ROLE = "Metadata_Role"
COMPOUND = "Metadata_Compound"
SOLVENT = "Metadata_Solvent"
PLATEMAP = "Metadata_Platemap"
DESIGN_COLUMNS = (PLATE, WELL, ROW, COLUMN, ROLE, COMPOUND, SOLVENT, PLATEMAP)

_MAX_REPORTED = 5


class DesignError(ValueError):
    """The platemaps cannot be turned into a valid design table."""


class Role(StrEnum):
    """What a well is for."""

    COMPOUND = "compound"
    CONTROL = "control"
    EMPTY = "empty"


@dataclass(frozen=True)
class PlatemapColumns:
    """The names of the columns of a platemap.

    Attributes
    ----------
    well : str
        The well name, such as ``A01``.
    compound : str
        The compound identifier.
        It is empty for wells without a compound.
    solvent : str or None
        The solvent, if the platemap has such a column.
    role : str or None
        A column that sets the role of each well (``compound``, ``control`` or
        ``empty``).
        If it is given, it decides; otherwise the role follows from the other
        columns.
    control_values : tuple of str
        Values of the compound column that mark a control well, such as ``DMSO``
        for platemaps that list the vehicle as a treatment.
    """

    well: str
    compound: str
    solvent: str | None = None
    role: str | None = None
    control_values: tuple[str, ...] = ()


@dataclass(frozen=True)
class BarcodeColumns:
    """The names of the columns of the barcode-to-platemap table.

    Attributes
    ----------
    plate : str
        The plate barcode.
    platemap : str
        The name of the platemap of the plate.
        The name may omit the ``.csv`` extension.
    """

    plate: str
    platemap: str


def assign_role(
    compound: str | None,
    solvent: str | None,
    explicit: str | None,
    control_values: Collection[str],
) -> Role:
    """Return the role of a well.

    Parameters
    ----------
    compound : str or None
        The compound identifier, or None if the well has none.
    solvent : str or None
        The solvent, or None if the well has none.
    explicit : str or None
        A role written in the platemap, or None.
        If it is given, it decides.
    control_values : collection of str
        Compound values that mark a control well.

    Returns
    -------
    Role
        The explicit role if there is one.
        Otherwise a well with no compound is a control if it has a solvent and
        empty if it has not, a well whose compound is a control value is a
        control, and any other well with a compound is a compound well.

    Raises
    ------
    DesignError
        If ``explicit`` is not a role.
    """
    if explicit is not None:
        try:
            return Role(explicit.strip().lower())
        except ValueError:
            roles = ", ".join(role.value for role in Role)
            msg = f"unknown role {explicit!r}; the roles are {roles}"
            raise DesignError(msg) from None
    if compound is None:
        return Role.CONTROL if solvent is not None else Role.EMPTY
    if compound in control_values:
        return Role.CONTROL
    return Role.COMPOUND


def role_problem(
    role: Role, compound: str | None, control_values: Collection[str]
) -> str | None:
    """Describe how a role contradicts the compound of a well.

    Parameters
    ----------
    role : Role
        The role of the well.
    compound : str or None
        The compound identifier, or None if the well has none.
    control_values : collection of str
        Compound values that mark a control well.

    Returns
    -------
    str or None
        A description of the contradiction, or None if the role fits.
    """
    if role is Role.COMPOUND:
        if compound is None:
            return "a compound well has no compound"
        if compound in control_values:
            return f"a compound well holds the control value {compound!r}"
    if role is Role.CONTROL and compound is not None and compound not in control_values:
        return f"a control well holds the compound {compound!r}"
    if role is Role.EMPTY and compound is not None:
        return f"an empty well holds {compound!r}"
    return None


def _clean(value: object) -> str | None:
    """Return a stripped string, or None for a missing or blank value."""
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _require_columns(
    table: pd.DataFrame, names: Collection[str | None], what: str
) -> None:
    missing = [name for name in names if name is not None and name not in table.columns]
    if missing:
        msg = f"{what} has no column {missing}; it has {list(table.columns)}"
        raise DesignError(msg)


def _platemap_design(
    platemap: pd.DataFrame,
    name: str,
    format_: PlateFormat,
    columns: PlatemapColumns,
) -> pd.DataFrame:
    """Build the design of one platemap, one row per well of the plate format."""
    _require_columns(
        platemap,
        [columns.well, columns.compound, columns.solvent, columns.role],
        f"platemap {name!r}",
    )
    problems: list[str] = []
    by_well: dict[str, tuple[Role, str | None, str | None]] = {}
    for _, row in platemap.iterrows():
        try:
            well = format_.normalize(str(row[columns.well]))
        except WellNameError as error:
            problems.append(str(error))
            continue
        compound = _clean(row[columns.compound])
        solvent = _clean(row[columns.solvent]) if columns.solvent else None
        explicit = _clean(row[columns.role]) if columns.role else None
        try:
            role = assign_role(compound, solvent, explicit, columns.control_values)
        except DesignError as error:
            problems.append(f"well {well}: {error}")
            continue
        problem = role_problem(role, compound, columns.control_values)
        if problem is not None:
            problems.append(f"well {well}: {problem}")
        if well in by_well:
            problems.append(f"well {well} is listed more than once")
        by_well[well] = (role, compound, solvent)
    if problems:
        shown = "; ".join(problems[:_MAX_REPORTED])
        more = len(problems) - _MAX_REPORTED
        suffix = f" (and {more} more)" if more > 0 else ""
        msg = f"platemap {name!r}: {shown}{suffix}"
        raise DesignError(msg)

    rows = []
    for well in format_.wells():
        role, compound, solvent = by_well.get(well, (Role.EMPTY, None, None))
        row_idx, column_idx = format_.parse(well)
        rows.append(
            {
                WELL: well,
                ROW: row_label(row_idx),
                COLUMN: column_idx + 1,
                ROLE: role.value,
                COMPOUND: compound,
                SOLVENT: solvent,
                PLATEMAP: name,
            }
        )
    return pd.DataFrame(rows)


def build_design(
    barcodes: pd.DataFrame,
    platemaps: Mapping[str, pd.DataFrame],
    format_spec: "int | tuple[int, int] | PlateFormat",
    barcode_columns: BarcodeColumns,
    columns: PlatemapColumns,
) -> pd.DataFrame:
    """Build the design table of an experiment.

    Parameters
    ----------
    barcodes : pandas.DataFrame
        The barcode-to-platemap table, one row per plate.
    platemaps : mapping of str to pandas.DataFrame
        The platemaps by name, as they are named in ``barcodes``.
    format_spec : int or tuple of int or PlateFormat
        The plate format; see `cytodxrx.plate.plate_format`.
    barcode_columns : BarcodeColumns
        The column names of ``barcodes``.
    columns : PlatemapColumns
        The column names of the platemaps.

    Returns
    -------
    pandas.DataFrame
        The design table: one row per well of every plate, with the columns in
        `DESIGN_COLUMNS`.
        Wells that a platemap does not list are empty.

    Raises
    ------
    DesignError
        If a plate is listed twice, a platemap is missing, or a platemap
        contradicts itself or has a well outside the plate.
    """
    format_ = plate_format(format_spec)
    _require_columns(
        barcodes, [barcode_columns.plate, barcode_columns.platemap], "the barcode table"
    )
    plates = barcodes[barcode_columns.plate].map(_clean)
    names = barcodes[barcode_columns.platemap].map(_clean)
    if plates.isna().any() or names.isna().any():
        msg = "the barcode table has a plate or a platemap name that is blank"
        raise DesignError(msg)
    repeated = sorted(plates[plates.duplicated()].unique())
    if repeated:
        msg = f"plates listed more than once in the barcode table: {repeated}"
        raise DesignError(msg)
    unknown = sorted(set(names) - set(platemaps))
    if unknown:
        msg = f"platemaps named in the barcode table but not given: {unknown}"
        raise DesignError(msg)

    designs = {
        name: _platemap_design(platemaps[name], name, format_, columns)
        for name in dict.fromkeys(names)
    }
    parts = [
        designs[name].assign(**{PLATE: plate})
        for plate, name in zip(plates, names, strict=True)
    ]
    return pd.concat(parts, ignore_index=True)[list(DESIGN_COLUMNS)]


def _find_platemap(directory: Path, name: str) -> Path:
    """Return the file of a platemap, with or without its ``.csv`` extension."""
    for candidate in (directory / name, directory / f"{name}.csv"):
        if candidate.is_file():
            return candidate
    msg = f"no platemap file {name!r} or {name + '.csv'!r} in {directory}"
    raise DesignError(msg)


def read_design(
    barcode_file: str | Path,
    platemap_dir: str | Path,
    format_spec: "int | tuple[int, int] | PlateFormat",
    barcode_columns: BarcodeColumns,
    columns: PlatemapColumns,
) -> pd.DataFrame:
    """Read the platemaps of an experiment and build its design table.

    Parameters
    ----------
    barcode_file : str or pathlib.Path
        The barcode-to-platemap table, a CSV file.
    platemap_dir : str or pathlib.Path
        The folder with the platemap CSV files.
    format_spec : int or tuple of int or PlateFormat
        The plate format; see `cytodxrx.plate.plate_format`.
    barcode_columns : BarcodeColumns
        The column names of the barcode table.
    columns : PlatemapColumns
        The column names of the platemaps.

    Returns
    -------
    pandas.DataFrame
        The design table; see `build_design`.

    Raises
    ------
    DesignError
        If a platemap file is missing or the platemaps are not valid.
    """
    barcodes = pd.read_csv(barcode_file, dtype=str)
    _require_columns(
        barcodes, [barcode_columns.plate, barcode_columns.platemap], "the barcode table"
    )
    directory = Path(platemap_dir)
    platemaps = {
        name: pd.read_csv(_find_platemap(directory, name), dtype=str)
        for name in barcodes[barcode_columns.platemap].dropna().map(str.strip).unique()
    }
    return build_design(barcodes, platemaps, format_spec, barcode_columns, columns)
