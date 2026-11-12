"""Tests for the top-level package."""

import re
from importlib.metadata import version

import cytodxrx


def test_version_is_a_version_string() -> None:
    assert re.match(r"^\d+\.\d+", cytodxrx.__version__)


def test_version_is_the_installed_distribution_version() -> None:
    assert cytodxrx.__version__ == version("cytodxrx")
