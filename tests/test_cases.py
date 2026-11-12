"""Tests whose cases are data files that a person can read and review.

The tables are in ``tests/cases``.
Each case states its expected result by hand; none of it is copied from the output
of the code.
"""

import csv
import re
import tomllib
from pathlib import Path

import pandas as pd
import pytest

from cytodxrx.design import (
    BarcodeColumns,
    DesignError,
    PlatemapColumns,
    Role,
    assign_role,
    build_design,
)

CASES = Path(__file__).parent / "cases"


def _role_cases() -> list[pytest.param]:
    with (CASES / "roles.csv").open(newline="") as file:
        return [pytest.param(row, id=row["case"]) for row in csv.DictReader(file)]


@pytest.mark.parametrize("row", _role_cases())
def test_role_of_a_well(row: dict[str, str]) -> None:
    control_values = tuple(v for v in row["control_values"].split("|") if v)
    role = assign_role(
        row["compound"] or None,
        row["solvent"] or None,
        row["explicit"] or None,
        control_values,
    )
    assert role is Role(row["role"])


def _error_cases() -> list[pytest.param]:
    with (CASES / "design_errors.toml").open("rb") as file:
        cases = tomllib.load(file)["case"]
    return [pytest.param(case, id=case["name"]) for case in cases]


@pytest.mark.parametrize("case", _error_cases())
def test_platemap_that_cannot_be_a_design(case: dict) -> None:
    platemap = pd.DataFrame(
        [[value or None for value in row] for row in case["rows"]],
        columns=["well", "compound", "solvent", "role"],
    )
    columns = PlatemapColumns("well", "compound", solvent="solvent", role="role")
    barcodes = pd.DataFrame({"plate": ["P1"], "map": ["m"]})
    with pytest.raises(DesignError) as error:
        build_design(
            barcodes,
            {"m": platemap},
            tuple(case["shape"]),
            BarcodeColumns("plate", "map"),
            columns,
        )
    assert re.search(case["error"], str(error.value)), str(error.value)
    if "not_in" in case:
        assert case["not_in"] not in str(error.value)
