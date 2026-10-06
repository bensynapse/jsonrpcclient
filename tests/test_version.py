"""__version__ must match the installed package metadata."""

from importlib.metadata import version

import jsonrpcclient


def test_version() -> None:
    assert jsonrpcclient.__version__ == version("jsonrpcclient")
