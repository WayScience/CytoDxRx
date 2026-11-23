"""Tests for the experiment model."""

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cytodxrx.design import PLATE, WELL, BarcodeColumns, PlatemapColumns
from cytodxrx.experiment import Experiment, ExperimentError
from cytodxrx.plate import PLATE_384

DATA = Path(__file__).parent / "data" / "sknas"


@pytest.fixture
def experiment() -> Experiment:
    return Experiment.from_files(
        DATA / "barcode_platemap.csv",
        DATA,
        384,
        BarcodeColumns("Plate_Barcode", "File_Name"),
        PlatemapColumns("Well_Position", "Batch_Id", solvent="Solvent"),
    )


def _profiles(experiment: Experiment, n_features: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    design = experiment.design
    table = pd.DataFrame({PLATE: design[PLATE], WELL: design[WELL]})
    for i in range(n_features):
        table[f"Cells_Feature_{i}"] = rng.standard_normal(len(table))
    return table


def test_from_files(experiment: Experiment) -> None:
    assert experiment.plate_format == PLATE_384
    assert experiment.plates == ["BR00148919"]
    assert len(experiment.design) == 384


def test_check_profiles_returns_the_features(experiment: Experiment) -> None:
    profiles = _profiles(experiment)
    profiles["Metadata_Batch"] = "b1"
    assert experiment.check_profiles(profiles) == [
        "Cells_Feature_0",
        "Cells_Feature_1",
        "Cells_Feature_2",
    ]


def test_check_profiles_accepts_unpadded_well_names_and_a_subset_of_wells(
    experiment: Experiment,
) -> None:
    profiles = _profiles(experiment).iloc[:10].copy()
    profiles[WELL] = profiles[WELL].str.replace(r"^([A-Z]+)0(\d)$", r"\1\2", regex=True)
    assert "A1" in set(profiles[WELL])
    assert experiment.check_profiles(profiles)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda t: t.drop(columns=[WELL]), "no column"),
        (lambda t: t.assign(**{WELL: "Z99"}), "not on a 16 x 24 plate"),
        (lambda t: t.assign(**{PLATE: "unknown"}), "not in the design"),
        (lambda t: pd.concat([t, t.iloc[:1]]), "more than once"),
        (lambda t: t[[PLATE, WELL]], "no feature columns"),
        (lambda t: t.assign(Cells_Feature_0="text"), "not numeric"),
    ],
    ids=[
        "no well column",
        "bad well",
        "unknown plate",
        "duplicate",
        "no features",
        "text",
    ],
)
def test_check_profiles_names_the_problem(
    experiment: Experiment,
    change: Callable[[pd.DataFrame], pd.DataFrame],
    message: str,
) -> None:
    with pytest.raises(ExperimentError, match=message):
        experiment.check_profiles(change(_profiles(experiment)))


def test_long_lists_of_problems_are_cut_off(experiment: Experiment) -> None:
    bad_wells = _profiles(experiment).iloc[:8].copy()
    bad_wells[WELL] = [f"Z{i}" for i in range(8)]
    with pytest.raises(ExperimentError) as error:
        experiment.check_profiles(bad_wells)
    assert "Z4" in str(error.value)
    assert "Z5" not in str(error.value)

    repeated = pd.concat([_profiles(experiment).iloc[:7]] * 2)
    with pytest.raises(ExperimentError) as error:
        experiment.check_profiles(repeated)
    assert str(error.value).count("Metadata_Well") == 5
