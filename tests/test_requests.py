"""Test requests.py"""

import json
from typing import Any, Callable, Dict

import pytest

from jsonrpcclient.requests import (
    notification,
    notification_json,
    request,
    request_hex,
    request_json,
    request_json_hex,
    request_json_random,
    request_json_uuid,
    request_natural,
    request_random,
    request_uuid,
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
            {"jsonrpc": "2.0", "method": "sqrt", "params": [1]},
        ),
        (
            notification("sqrt", params=(1, 2, 3)),
            {"jsonrpc": "2.0", "method": "sqrt", "params": [1, 2, 3]},
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


def test_request_list_and_tuple_params() -> None:
    assert request("sqrt", [1, 2], id=1)["params"] == [1, 2]
    assert request("sqrt", (1, 2), id=1)["params"] == [1, 2]


@pytest.mark.parametrize("func", [request_hex, request_random, request_uuid])
def test_other_id_types(func: Callable[..., Dict[str, Any]]) -> None:
    req = func("foo", [1])
    assert req["params"] == [1]
    assert isinstance(req["id"], str)
    assert func("foo", id=5)["id"] == 5


@pytest.mark.parametrize(
    "func",
    [request_json, request_json_hex, request_json_random, request_json_uuid],
)
def test_request_json_variants(func: Callable[..., str]) -> None:
    assert json.loads(func("foo", {"a": 1}, id=7)) == {
        "jsonrpc": "2.0",
        "method": "foo",
        "params": {"a": 1},
        "id": 7,
    }


def test_notification_json_params() -> None:
    assert json.loads(notification_json("foo", [1])) == {
        "jsonrpc": "2.0",
        "method": "foo",
        "params": [1],
    }


def test_request_natural_is_request() -> None:
    assert request_natural is request
