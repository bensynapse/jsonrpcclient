"""The examples in the docstrings, which the API reference shows, must run."""

import doctest
from types import ModuleType

import pytest

from jsonrpcclient import id_generators, requests, responses, utils


@pytest.mark.parametrize(
    "module", [requests, responses, id_generators, utils], ids=lambda m: m.__name__
)
def test_docstring_examples(module: ModuleType) -> None:
    result = doctest.testmod(module, optionflags=doctest.ELLIPSIS)
    assert result.attempted > 0
    assert result.failed == 0
