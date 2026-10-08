"""Test responses.py"""

from decimal import Decimal
from typing import Any, Dict, Type, Union

import pytest

from jsonrpcclient.responses import (
    Error,
    InvalidResponse,
    Ok,
    Response,
    parse,
    parse_json,
    to_response,
)


def test_ok() -> None:
    assert repr(Ok("foo", 1)) == "Ok(result='foo', id=1)"


def test_error() -> None:
    assert (
        repr(Error(1, "foo", "bar", 2))
        == "Error(code=1, message='foo', data='bar', id=2)"
    )


@pytest.mark.parametrize(
    "argument,expected",
    [
        (
            {"jsonrpc": "2.0", "result": "foo", "id": 1},
            Ok("foo", 1),
        ),
        (
            {"jsonrpc": "2.0", "error": {"code": 1, "message": "foo"}, "id": 1},
            Error(1, "foo", None, 1),
        ),
    ],
)
def test_to_response(argument: Dict[str, str], expected: Response) -> None:
    assert to_response(argument) == expected


def test_parse() -> None:
    assert parse({"jsonrpc": "2.0", "result": "pong", "id": 1}) == Ok("pong", 1)


def test_parse_string() -> None:
    with pytest.raises(TypeError) as exc:
        parse('{"jsonrpc": "2.0", "result": "pong", "id": 1}')  # type: ignore[call-overload]  # pyright: ignore[reportCallIssue, reportArgumentType]
    assert str(exc.value) == "Use parse_json on strings"


def test_parse_json() -> None:
    assert parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}') == Ok("pong", 1)


def test_parse_json_bytes() -> None:
    assert parse_json(b'{"jsonrpc": "2.0", "result": "pong", "id": 1}') == Ok("pong", 1)


def test_parse_json_passes_kwargs_to_json_loads() -> None:
    parsed = parse_json(
        '{"jsonrpc": "2.0", "result": 1.5, "id": 1}', parse_float=Decimal
    )
    assert parsed == Ok(Decimal("1.5"), 1)


def test_parse_batch() -> None:
    parsed = parse(
        [
            {"jsonrpc": "2.0", "result": "pong", "id": 1},
            {"jsonrpc": "2.0", "error": {"code": 1, "message": "foo"}, "id": 2},
        ]
    )
    assert list(parsed) == [Ok("pong", 1), Error(1, "foo", None, 2)]


def test_parse_empty_batch() -> None:
    with pytest.raises(InvalidResponse) as exc:
        parse([])
    assert str(exc.value) == "Invalid JSON-RPC response: batch must not be empty"


@pytest.mark.parametrize("response", ["[]", b"[]", bytearray(b"[]")])
def test_parse_json_empty_batch(response: Union[str, bytes, bytearray]) -> None:
    with pytest.raises(InvalidResponse) as exc:
        parse_json(response)
    assert str(exc.value) == "Invalid JSON-RPC response: batch must not be empty"


def test_error_wins_over_result() -> None:
    # JSON-RPC 1.0 servers send "result": null with an error.
    response = {
        "jsonrpc": "2.0",
        "result": None,
        "error": {"code": -32601, "message": "Method not found"},
        "id": 1,
    }
    assert parse(response) == Error(-32601, "Method not found", None, 1)


def test_null_error_with_result_is_ok() -> None:
    assert parse({"result": 5, "error": None, "id": 1}) == Ok(5, 1)


@pytest.mark.parametrize(
    "response,message",
    [
        ({}, "missing 'id'"),
        ({"jsonrpc": "2.0", "result": 1}, "missing 'id'"),
        ({"jsonrpc": "2.0", "id": 1}, "needs a 'result' or a non-null 'error'"),
        ({"error": None, "id": 1}, "needs a 'result' or a non-null 'error'"),
        ({"error": "boom", "id": 1}, "'error' must be an object, got str"),
        ({"error": [1], "id": 1}, "'error' must be an object, got list"),
        ({"error": {"message": "x"}, "id": 1}, "'error' is missing 'code'"),
        ({"error": {"code": 1}, "id": 1}, "'error' is missing 'message'"),
        (None, "expected an object, got null"),
        (123, "expected an object, got int"),
    ],
)
def test_invalid_response(response: Any, message: str) -> None:
    with pytest.raises(InvalidResponse) as exc:
        parse(response)
    assert str(exc.value) == f"Invalid JSON-RPC response: {message}"


@pytest.mark.parametrize("old_exception", [KeyError, TypeError])
def test_invalid_response_is_caught_by_old_handlers(
    old_exception: Type[Exception],
) -> None:
    with pytest.raises(old_exception):
        parse({"jsonrpc": "2.0", "result": 1})


def test_parse_json_non_object_message() -> None:
    # This used to say "Use parse_json on strings", to someone using parse_json.
    with pytest.raises(InvalidResponse) as exc:
        parse_json('"pong"')
    assert str(exc.value) == "Invalid JSON-RPC response: expected an object, got str"


def test_parse_bytes() -> None:
    with pytest.raises(TypeError) as exc:
        parse(b"{}")  # type: ignore[call-overload]  # pyright: ignore[reportCallIssue, reportArgumentType]
    assert str(exc.value) == "Use parse_json on strings"


def test_parse_batch_is_one_pass() -> None:
    batch = parse([{"result": 1, "id": 1}, {"result": 2, "id": 2}])
    assert list(batch) == [Ok(1, 1), Ok(2, 2)]
    assert list(batch) == []


def test_parse_batch_invalid_item_raises_when_reached() -> None:
    batch = parse([{"result": 1, "id": 1}, {"bogus": 1}])
    assert next(batch) == Ok(1, 1)
    with pytest.raises(InvalidResponse):
        next(batch)
