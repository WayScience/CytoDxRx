"""The experiment: a plate format and the design of its plates."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype

from cytodxrx.design import (
    PLATE,
    WELL,
    BarcodeColumns,
    PlatemapColumns,
    read_design,
)
from cytodxrx.plate import PlateFormat, WellNameError, plate_format

_METADATA_PREFIX = "Metadata_"
_MAX_REPORTED = 5


class ExperimentError(ValueError):
    """Profiles do not match the experiment they are meant to describe."""


@dataclass(frozen=True)
class Experiment:
    """The plate format and the design table of an experiment.

    Attributes
    ----------
    plate_format : PlateFormat
        The format of every plate.
    design : pandas.DataFrame
        The design table; see `cytodxrx.design.build_design`.
    """

    plate_format: PlateFormat
    design: pd.DataFrame

    @classmethod
    def from_files(
        cls,
        barcode_file: str | Path,
        platemap_dir: str | Path,
        format_spec: "int | tuple[int, int] | PlateFormat",
        barcode_columns: BarcodeColumns,
        columns: PlatemapColumns,
    ) -> "Experiment":
        """Read the platemaps of an experiment.

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
        Experiment
            The experiment, with its design table.
        """
        design = read_design(
            barcode_file, platemap_dir, format_spec, barcode_columns, columns
        )
        return cls(plate_format=plate_format(format_spec), design=design)

    @property
    def plates(self) -> list[str]:
        """The plates of the experiment, in the order of the barcode table."""
        return list(dict.fromkeys(self.design[PLATE]))

    def check_profiles(self, profiles: pd.DataFrame) -> list[str]:
        """Check that well-level profiles belong to this experiment.

        Parameters
        ----------
        profiles : pandas.DataFrame
            Well-level profiles with ``Metadata_Plate`` and ``Metadata_Well``
            columns, other ``Metadata_`` columns, and numeric feature columns.

        Returns
        -------
        list of str
            The feature columns: every column that does not start with
            ``Metadata_``.

        Raises
        ------
        ExperimentError
            If a column is missing, a well name is not a well of the plate
            format, a well appears twice on a plate, a plate is not in the
            design, or a feature is not numeric.
        """
        missing = [name for name in (PLATE, WELL) if name not in profiles.columns]
        if missing:
            msg = f"the profiles have no column {missing}"
            raise ExperimentError(msg)

        wells = []
        bad = []
        for well in profiles[WELL]:
            try:
                wells.append(self.plate_format.normalize(well))
            except WellNameError as error:
                bad.append(str(error))
        if bad:
            msg = f"wells that are not on a {self.plate_format}: {bad[:_MAX_REPORTED]}"
            raise ExperimentError(msg)

        unknown = sorted(set(profiles[PLATE]) - set(self.plates))
        if unknown:
            msg = f"plates in the profiles but not in the design: {unknown}"
            raise ExperimentError(msg)

        keys = pd.DataFrame({PLATE: profiles[PLATE].to_numpy(), WELL: wells})
        repeated = keys[keys.duplicated(keep=False)]
        if len(repeated):
            shown = repeated.drop_duplicates().head(_MAX_REPORTED)
            msg = f"wells listed more than once on a plate: {shown.to_dict('records')}"
            raise ExperimentError(msg)

        features = [c for c in profiles.columns if not c.startswith(_METADATA_PREFIX)]
        if not features:
            msg = "the profiles have no feature columns"
            raise ExperimentError(msg)
        not_numeric = [c for c in features if not is_numeric_dtype(profiles[c])]
        if not_numeric:
            msg = f"feature columns that are not numeric: {not_numeric[:_MAX_REPORTED]}"
            raise ExperimentError(msg)
        return features
