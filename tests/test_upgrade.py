"""Code written for 4.x that 5.0 promises to keep running (plans/5.0.md, Acceptance).

Each test is 4.x code, unchanged. If one fails, 5.0 broke a promise to 4.x
users, or the migration guide needs a new entry.
"""

import json
from typing import Any

from jsonrpcclient import (
    Error,
    InvalidResponse,
    Ok,
    notification,
    notification_json,
    parse,
    parse_json,
    request,
    request_json,
    request_uuid,
)
from jsonrpcclient.id_generators import decimal
from jsonrpcclient.requests import request_natural
from jsonrpcclient.utils import compose


def test_build_send_and_read_one_response() -> None:
    sent = json.dumps(request("add", [2, 3], id=1))
    assert json.loads(sent) == {
        "jsonrpc": "2.0",
        "method": "add",
        "params": [2, 3],
        "id": 1,
    }
    parsed = parse({"jsonrpc": "2.0", "result": 5, "id": 1})
    if isinstance(parsed, Ok):
        assert parsed.result == 5
    else:
        raise AssertionError(parsed)
    ok = parse({"jsonrpc": "2.0", "result": 5, "id": 1})
    assert isinstance(ok, Ok)
    result, id = ok
    assert (result, id) == (5, 1)


def test_named_params_tuples_and_the_json_variants() -> None:
    assert request("greet", {"name": "Ada"}, id="a")["id"] == "a"
    assert request("sqrt", (16,), id=1) == request("sqrt", [16], id=1)
    assert json.loads(request_json("ping", id=1)) == request("ping", id=1)
    assert json.loads(notification_json("log", ["hi"])) == notification("log", ["hi"])
    assert isinstance(request_uuid("ping")["id"], str)
    assert request_natural is request
    ids = decimal(10)
    assert request("ping", id=next(ids))["id"] == 10


def test_error_responses() -> None:
    error = {"code": -32601, "message": "Method not found"}
    parsed = parse_json(json.dumps({"jsonrpc": "2.0", "error": error, "id": 1}))
    assert parsed == Error(-32601, "Method not found", None, 1)
    # JSON-RPC 1.0 style servers send "result": null with an error.
    assert parse({"result": None, "error": error, "id": 1}) == parsed


def test_lenient_parsing_is_unchanged() -> None:
    assert parse({"result": "pong", "id": 1}) == Ok("pong", 1)
    assert parse({"jsonrpc": "1.0", "result": "pong", "id": True}) == Ok("pong", True)


def test_catching_invalid_response() -> None:
    try:
        parse({"jsonrpc": "2.0", "result": "pong"})
    except InvalidResponse as exc:
        assert str(exc) == "Invalid JSON-RPC response: missing 'id'"
    else:
        raise AssertionError("no InvalidResponse")


def test_looping_over_a_batch() -> None:
    reply: list[dict[str, Any]] = [
        {"jsonrpc": "2.0", "result": "pong", "id": 1},
        {"jsonrpc": "2.0", "result": 5, "id": 2},
    ]
    assert {parsed.id: parsed for parsed in parse(reply)} == {
        1: Ok("pong", 1),
        2: Ok(5, 2),
    }
    assert list(parse(reply)) == [Ok("pong", 1), Ok(5, 2)]


def test_compose_with_another_json_library() -> None:
    to_json = compose(json.dumps, request)
    assert to_json("ping", id=1) == '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
