"""Test id_generators.py"""

import re
from uuid import UUID

from jsonrpcclient import id_generators


def test_hexadecimal() -> None:
    i = id_generators.hexadecimal()
    assert next(i) == "1"
    i = id_generators.hexadecimal(9)
    assert next(i) == "9"
    assert next(i) == "a"


def test_random() -> None:
    i = id_generators.random()
    assert re.match("^[0-9,a-z]{8}$", next(i))


def test_uuid() -> None:
    i = id_generators.uuid()
    # Raise ValueError if badly formed hexadecimal UUID string
    UUID(next(i), version=4)
