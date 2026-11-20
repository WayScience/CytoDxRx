"""Plate formats and well names.

A plate has rows labelled ``A``, ``B``, ... (then ``AA``, ``AB``, ... for plates
with more than 26 rows) and columns numbered from 1.
A well name is a row label followed by a column number, as in ``A01`` or ``P24``.
Row and column indexes in this module are zero-based.
"""

import re
from dataclasses import dataclass

_WELL_NAME = re.compile(r"^([A-Za-z]+)(\d+)$")
_LETTERS = 26


class WellNameError(ValueError):
    """A well name is malformed or lies outside the plate format."""


def row_label(index: int) -> str:
    """Return the label of a plate row.

    Parameters
    ----------
    index : int
        The zero-based row index.

    Returns
    -------
    str
        The label: ``A`` for 0, ``Z`` for 25, ``AA`` for 26.

    Raises
    ------
    ValueError
        If ``index`` is negative.
    """
    if index < 0:
        msg = f"a row index cannot be negative, got {index}"
        raise ValueError(msg)
    label = ""
    remaining = index + 1
    while remaining > 0:
        remaining, letter = divmod(remaining - 1, _LETTERS)
        label = chr(ord("A") + letter) + label
    return label


def row_index(label: str) -> int:
    """Return the zero-based index of a plate row.

    Parameters
    ----------
    label : str
        The row label, such as ``A`` or ``AA``, in either case.

    Returns
    -------
    int
        The zero-based row index; the inverse of `row_label`.

    Raises
    ------
    ValueError
        If ``label`` is empty or has a character that is not a letter.
    """
    if not label or not label.isascii() or not label.isalpha():
        msg = f"a row label is one or more letters, got {label!r}"
        raise ValueError(msg)
    total = 0
    for character in label.upper():
        total = total * _LETTERS + (ord(character) - ord("A") + 1)
    return total - 1


@dataclass(frozen=True)
class PlateFormat:
    """The number of rows and columns of a plate.

    Attributes
    ----------
    n_rows : int
        The number of rows.
    n_columns : int
        The number of columns.
    """

    n_rows: int
    n_columns: int

    def __post_init__(self) -> None:
        """Check that the plate has at least one row and one column."""
        if self.n_rows < 1 or self.n_columns < 1:
            msg = (
                f"a plate needs rows and columns, got {self.n_rows} x {self.n_columns}"
            )
            raise ValueError(msg)

    @property
    def n_wells(self) -> int:
        """The number of wells on the plate."""
        return self.n_rows * self.n_columns

    def name(self, row: int, column: int) -> str:
        """Return the name of a well.

        Parameters
        ----------
        row : int
            The zero-based row index.
        column : int
            The zero-based column index.

        Returns
        -------
        str
            The well name with a two-digit column, such as ``A01``.

        Raises
        ------
        WellNameError
            If the well lies outside the plate.
        """
        if not (0 <= row < self.n_rows and 0 <= column < self.n_columns):
            msg = f"well at row {row}, column {column} is outside a {self}"
            raise WellNameError(msg)
        return f"{row_label(row)}{column + 1:02d}"

    def parse(self, well: str) -> tuple[int, int]:
        """Return the row and column indexes of a well name.

        Parameters
        ----------
        well : str
            A well name such as ``A01`` or ``A1``, in either case.

        Returns
        -------
        tuple of int
            The zero-based row and column indexes.

        Raises
        ------
        WellNameError
            If the name is malformed or the well lies outside the plate.
        """
        match = _WELL_NAME.match(well.strip()) if isinstance(well, str) else None
        if match is None:
            msg = f"{well!r} is not a well name such as A01"
            raise WellNameError(msg)
        row = row_index(match.group(1))
        column = int(match.group(2)) - 1
        if not (0 <= row < self.n_rows and 0 <= column < self.n_columns):
            msg = f"well {well!r} is outside a {self}"
            raise WellNameError(msg)
        return row, column

    def normalize(self, well: str) -> str:
        """Return the canonical name of a well, so ``a1`` becomes ``A01``.

        Parameters
        ----------
        well : str
            A well name in any form that `parse` accepts.

        Returns
        -------
        str
            The canonical well name.
        """
        return self.name(*self.parse(well))

    def wells(self) -> list[str]:
        """Return every well name, row by row.

        Returns
        -------
        list of str
            The canonical names of all wells, from ``A01`` across the first row.
        """
        return [
            self.name(row, column)
            for row in range(self.n_rows)
            for column in range(self.n_columns)
        ]

    def __str__(self) -> str:
        """Describe the format, for messages."""
        return f"{self.n_rows} x {self.n_columns} plate"


PLATE_96 = PlateFormat(n_rows=8, n_columns=12)
PLATE_384 = PlateFormat(n_rows=16, n_columns=24)
PLATE_1536 = PlateFormat(n_rows=32, n_columns=48)

_BY_WELLS = {format_.n_wells: format_ for format_ in (PLATE_96, PLATE_384, PLATE_1536)}


def plate_format(spec: "int | tuple[int, int] | PlateFormat") -> PlateFormat:
    """Return a plate format from a well count or a pair of dimensions.

    Parameters
    ----------
    spec : int or tuple of int or PlateFormat
        ``96``, ``384`` or ``1536``; a ``(n_rows, n_columns)`` pair; or a plate
        format, which is returned as it is.

    Returns
    -------
    PlateFormat
        The plate format.

    Raises
    ------
    ValueError
        If ``spec`` is a well count that is not a standard plate.
    """
    if isinstance(spec, PlateFormat):
        return spec
    if isinstance(spec, int):
        if spec not in _BY_WELLS:
            msg = (
                f"{spec} wells is not a standard plate; use one of {sorted(_BY_WELLS)}"
            )
            raise ValueError(msg)
        return _BY_WELLS[spec]
    n_rows, n_columns = spec
    return PlateFormat(n_rows=n_rows, n_columns=n_columns)
