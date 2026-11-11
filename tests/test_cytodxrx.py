"""Tests for the top-level package."""

import re

import cytodxrx


def test_version_is_a_version_string() -> None:
    assert re.match(r"^\d+\.\d+", cytodxrx.__version__)
