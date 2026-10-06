"""Test sentinels.py"""

from jsonrpcclient.sentinels import Sentinel


def test_sentinel() -> None:
    assert repr(Sentinel("foo")) == "<foo>"
