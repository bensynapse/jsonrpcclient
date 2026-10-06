"""Test requests.py"""

from typing import Any, Dict

import pytest

from jsonrpcclient.requests import (
    notification,
    notification_json,
    request,
    request_json,
)


@pytest.mark.parametrize(
    "argument,expected",
    [
        (
            notification("get"),
            {"jsonrpc": "2.0", "method": "get"},
        ),
        (
            notification("sqrt", params=(1,)),
            {"jsonrpc": "2.0", "method": "sqrt", "params": (1,)},
        ),
        (
            notification("sqrt", params=(1, 2, 3)),
            {"jsonrpc": "2.0", "method": "sqrt", "params": (1, 2, 3)},
        ),
        (
            notification("sqrt", params={"name": "Foo"}),
            {"jsonrpc": "2.0", "method": "sqrt", "params": {"name": "Foo"}},
        ),
    ],
)
def test_notification(argument: Dict[str, Any], expected: Dict[str, Any]) -> None:
    assert argument == expected


def test_notification_json() -> None:
    assert notification_json("foo") == '{"jsonrpc": "2.0", "method": "foo"}'


@pytest.mark.parametrize(
    "argument,expected",
    [
        (
            request("foo", id=1),
            {"jsonrpc": "2.0", "method": "foo", "id": 1},
        ),
        (
            request("sqrt", params=[1], id=1),
            {"jsonrpc": "2.0", "method": "sqrt", "params": [1], "id": 1},
        ),
        (
            request("sqrt", params=[1, 2, 3], id=2),
            {
                "jsonrpc": "2.0",
                "method": "sqrt",
                "params": [1, 2, 3],
                "id": 2,
            },
        ),
        (
            request("sqrt", params={"name": "Foo"}, id=3),
            {
                "jsonrpc": "2.0",
                "method": "sqrt",
                "params": {"name": "Foo"},
                "id": 3,
            },
        ),
        (
            request("foo", {"name": "bar"}, id=1),
            {"jsonrpc": "2.0", "method": "foo", "params": {"name": "bar"}, "id": 1},
        ),
    ],
)
def test_request(argument: Dict[str, Any], expected: Dict[str, Any]) -> None:
    assert argument == expected


def test_request_auto_iterating_id() -> None:
    assert request("foo") == {"jsonrpc": "2.0", "method": "foo", "id": 1}
    assert request("foo") == {"jsonrpc": "2.0", "method": "foo", "id": 2}


def test_request_json() -> None:
    assert request_json("foo", id=1) == '{"jsonrpc": "2.0", "method": "foo", "id": 1}'
