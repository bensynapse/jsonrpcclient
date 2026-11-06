"""parse(..., strict=True) checks the JSON-RPC 2.0 rules (plans/5.0.md, D6)."""

import json
from decimal import Decimal
from typing import Any

import pytest

from jsonrpcclient import Error, InvalidResponse, Ok, parse, parse_json

OK = {"jsonrpc": "2.0", "result": "pong", "id": 1}
ERROR = {"jsonrpc": "2.0", "error": {"code": -32601, "message": "No"}, "id": 1}


@pytest.mark.parametrize(
    "response,expected",
    [
        (OK, Ok("pong", 1)),
        (ERROR, Error(-32601, "No", None, 1)),
        ({**OK, "result": None}, Ok(None, 1)),
        ({**OK, "id": None}, Ok("pong", None)),
        ({**OK, "id": "abc"}, Ok("pong", "abc")),
        ({**OK, "id": 1.5}, Ok("pong", 1.5)),
        (
            {
                "jsonrpc": "2.0",
                "error": {"code": 1, "message": "x", "data": [1]},
                "id": 2,
            },
            Error(1, "x", [1], 2),
        ),
    ],
)
def test_valid_responses_pass(response: dict[str, Any], expected: Any) -> None:
    assert parse(response, strict=True) == expected


@pytest.mark.parametrize(
    "response,message",
    [
        ({"result": 1, "id": 1}, "missing 'jsonrpc'"),
        ({**OK, "jsonrpc": "1.0"}, "'jsonrpc' must be \"2.0\", got '1.0'"),
        ({**OK, "jsonrpc": 2.0}, "'jsonrpc' must be \"2.0\", got 2.0"),
        ({"jsonrpc": "2.0", "result": 1}, "missing 'id'"),
        ({**OK, "id": True}, "'id' must be a string, a number or null, got bool"),
        ({**OK, "id": [1]}, "'id' must be a string, a number or null, got list"),
        ({**OK, "id": {}}, "'id' must be a string, a number or null, got dict"),
        ({**ERROR, "result": None}, "has both 'result' and 'error'"),
        ({**OK, "error": None}, "has both 'result' and 'error'"),
        ({"jsonrpc": "2.0", "id": 1}, "needs a 'result' or an 'error'"),
        (
            {"jsonrpc": "2.0", "error": None, "id": 1},
            "'error' must be an object, got null",
        ),
        ({**ERROR, "error": "boom"}, "'error' must be an object, got str"),
        ({**ERROR, "error": {"message": "x"}}, "'error' is missing 'code'"),
        ({**ERROR, "error": {"code": 1}}, "'error' is missing 'message'"),
        (
            {**ERROR, "error": {"code": "1", "message": "x"}},
            "'error.code' must be an int, got str",
        ),
        (
            {**ERROR, "error": {"code": 1.0, "message": "x"}},
            "'error.code' must be an int, got float",
        ),
        (
            {**ERROR, "error": {"code": True, "message": "x"}},
            "'error.code' must be an int, got bool",
        ),
        (
            {**ERROR, "error": {"code": 1, "message": None}},
            "'error.message' must be a str, got null",
        ),
        ([], "batch must not be empty"),
        (None, "expected an object, got null"),
    ],
)
def test_invalid_responses_raise(response: Any, message: str) -> None:
    with pytest.raises(InvalidResponse) as exc:
        parse(response, strict=True)
    assert str(exc.value) == f"Invalid JSON-RPC response: {message}"


@pytest.mark.parametrize(
    "response",
    [
        {"result": 1, "id": 1},
        {**OK, "jsonrpc": "1.0"},
        {**ERROR, "result": None},
        {**OK, "id": True},
        {**ERROR, "error": {"code": "1", "message": None}},
    ],
)
def test_the_default_stays_lenient(response: dict[str, Any]) -> None:
    parse(response)
    parse(response, strict=False)


def test_strict_batch_gives_the_index() -> None:
    with pytest.raises(InvalidResponse) as exc:
        parse([OK, {**OK, "jsonrpc": "1.0"}], strict=True)
    assert str(exc.value) == (
        "Invalid JSON-RPC response at index 1 of the batch: "
        "'jsonrpc' must be \"2.0\", got '1.0'"
    )
    assert parse([OK, ERROR], strict=True) == [
        Ok("pong", 1),
        Error(-32601, "No", None, 1),
    ]


def test_parse_json_strict() -> None:
    assert parse_json(json.dumps(OK), strict=True) == Ok("pong", 1)
    with pytest.raises(InvalidResponse):
        parse_json('{"result": 1, "id": 1}', strict=True)


def test_parse_json_strict_is_not_passed_to_json_loads() -> None:
    # In 4.x, strict went to json.loads, where strict=False allows control
    # characters in strings. Now it's parse_json's own option.
    with pytest.raises(json.JSONDecodeError):
        parse_json('{"jsonrpc": "2.0", "result": "a\tb", "id": 1}', strict=False)
    assert parse(json.loads('{"result": "a\tb", "id": 1}', strict=False)) == Ok(
        "a\tb", 1
    )


def test_parse_json_still_passes_other_kwargs() -> None:
    parsed = parse_json(
        '{"jsonrpc": "2.0", "result": 1.5, "id": 1}', strict=True, parse_float=Decimal
    )
    assert parsed == Ok(Decimal("1.5"), 1)


def test_strict_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        parse(OK, True)  # type: ignore[call-overload]  # pyright: ignore[reportCallIssue]
