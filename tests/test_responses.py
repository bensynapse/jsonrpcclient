"""Test responses.py"""

from typing import Dict

import pytest

from jsonrpcclient.responses import Error, Ok, Response, parse, parse_json, to_response


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
        parse('{"jsonrpc": "2.0", "result": "pong", "id": 1}')  # type: ignore
    assert str(exc.value) == "Use parse_json on strings"


def test_parse_json() -> None:
    assert parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}') == Ok("pong", 1)
