"""CytoDxRx: diagnose and correct technical artifacts in image-based profiles."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cytodxrx")
except PackageNotFoundError:  # pragma: no cover
    # the package is not installed (for example, when run from a source checkout)
    __version__ = "0.0.0"

__all__ = ["__version__"]
