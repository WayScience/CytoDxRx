"""Sphinx configuration for the CytoDxRx documentation."""

from datetime import date

import cytodxrx

project = "CytoDxRx"
author = "Gregory P. Way"
project_copyright = f"{date.today().year}, Way Science"
version = cytodxrx.__version__
release = version

extensions = [
    # builds the API reference from docstrings
    "sphinx.ext.autodoc",
    # generates one page per module at build time, so new modules need no docs edit
    "sphinx.ext.autosummary",
    # reads numpy-style docstrings
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_copybutton",
]
autosummary_generate = True
napoleon_numpy_docstring = True
napoleon_google_docstring = False
myst_enable_extensions = ["colon_fence"]

exclude_patterns = ["_build", "_autosummary/.gitignore"]
html_theme = "furo"
