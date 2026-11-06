"""match_responses pairs a batch's responses with its requests (plans/5.0.md, D3)."""

from typing import Any

import pytest

from jsonrpcclient import (
    Error,
    InvalidResponse,
    Ok,
    match_responses,
    notification,
    parse,
    request,
    request_json,
)
from jsonrpcclient.responses import Response

UNREAD = Error(-32600, "Invalid Request", None, None)


def test_matches_by_id_in_request_order() -> None:
    batch = [request("a", id=1), notification("log"), request("b", id="x")]
    responses: list[Response] = [
        Error(-32601, "Method not found", None, "x"),
        Ok("pong", 1),
    ]
    matched = match_responses(batch, responses)
    assert matched == {
        1: Ok("pong", 1),
        "x": Error(-32601, "Method not found", None, "x"),
    }
    assert list(matched) == [1, "x"]


def test_works_on_what_parse_returns() -> None:
    batch = [request("ping", id=1), request("add", [2, 3], id=2)]
    reply = [
        {"jsonrpc": "2.0", "result": 5, "id": 2},
        {"jsonrpc": "2.0", "result": "pong", "id": 1},
    ]
    assert match_responses(batch, parse(reply)) == {1: Ok("pong", 1), 2: Ok(5, 2)}


def test_a_rejected_batch_is_an_error_for_every_request() -> None:
    batch = [request("a", id=1), notification("log"), request("b", id=2)]
    assert match_responses(batch, UNREAD) == {1: UNREAD, 2: UNREAD}


def test_one_ok_for_a_batch_is_invalid() -> None:
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1)], Ok("pong", 1))
    assert str(exc.value) == (
        "Invalid JSON-RPC response: a batch gets a list of responses, or one Error "
        "if the server rejected it, not Ok(result='pong', id=1)"
    )


def test_a_null_id_error_fills_a_request_without_a_response() -> None:
    batch = [request("a", id=1), request("b", id=2), request("c", id=3)]
    responses: list[Response] = [Ok("a", 1), UNREAD, Ok("c", 3)]
    assert match_responses(batch, responses) == {
        1: Ok("a", 1),
        2: UNREAD,
        3: Ok("c", 3),
    }


def test_null_id_errors_fill_in_order() -> None:
    first = Error(-32600, "first", None, None)
    second = Error(-32600, "second", None, None)
    batch = [request("a", id=1), request("b", id=2)]
    assert match_responses(batch, [first, second]) == {1: first, 2: second}


def test_a_null_id_error_for_a_notification_is_dropped() -> None:
    # A notification the server can't read gets an error with a null id.
    batch = [request("a", id=1), notification("log")]
    assert match_responses(batch, [Ok("a", 1), UNREAD]) == {1: Ok("a", 1)}


def test_a_request_with_a_null_id_matches_directly() -> None:
    batch = [request("a", id=None), request("b", id=2)]
    responses = [Ok("b", 2), Ok("a", None)]
    assert match_responses(batch, responses) == {None: Ok("a", None), 2: Ok("b", 2)}


def test_a_missing_response_raises() -> None:
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1), request("b", id=2)], [Ok("a", 1)])
    assert str(exc.value) == "Invalid JSON-RPC response: no response for id 2"


def test_a_response_for_no_request_raises() -> None:
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1)], [Ok("a", 1), Ok("b", 7)])
    assert str(exc.value) == "Invalid JSON-RPC response: id 7 matches no request"


def test_an_ok_with_a_null_id_for_no_request_raises() -> None:
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1)], [Ok("x", None)])
    assert str(exc.value) == "Invalid JSON-RPC response: id None matches no request"


def test_two_responses_for_one_id_raise() -> None:
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id="k")], [Ok("a", "k"), Ok("b", "k")])
    assert str(exc.value) == "Invalid JSON-RPC response: two responses for id 'k'"


def test_two_requests_with_one_id_raise() -> None:
    with pytest.raises(ValueError) as exc:
        match_responses([request("a", id=1), request("b", id=1)], [Ok("a", 1)])
    assert not isinstance(exc.value, InvalidResponse)
    assert (
        str(exc.value)
        == "Two requests have the id 1, so their responses can't be told apart"
    )


def test_only_notifications_give_an_empty_dict() -> None:
    assert match_responses([notification("log")], [UNREAD]) == {}


@pytest.mark.parametrize("batch", [[], ()])
def test_an_empty_batch_gives_an_empty_dict(batch: Any) -> None:
    assert match_responses(batch, []) == {}


def test_unparsed_responses_raise_type_error() -> None:
    reply: Any = [{"jsonrpc": "2.0", "result": "pong", "id": 1}]
    with pytest.raises(TypeError) as exc:
        match_responses([request("a", id=1)], reply)
    assert str(exc.value) == (
        "responses must be what parse returned, not a list of dict"
    )


def test_an_unhashable_response_id_matches_no_request() -> None:
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1)], parse([{"result": 1, "id": [1]}]))
    assert str(exc.value) == "Invalid JSON-RPC response: id [1] matches no request"


def test_an_id_with_an_unhashable_part_matches_no_request() -> None:
    reply = parse([{"result": 1, "id": (1, [2])}])
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1)], reply)
    assert str(exc.value) == (
        "Invalid JSON-RPC response: id (1, [2]) matches no request"
    )


def test_true_is_not_the_id_1() -> None:
    # In JSON, true and 1 are different ids. Python says True == 1.
    with pytest.raises(InvalidResponse) as exc:
        match_responses([request("a", id=1)], [Ok("x", True)])
    assert str(exc.value) == "Invalid JSON-RPC response: id True matches no request"
    with pytest.raises(InvalidResponse):
        match_responses([request("a", id=True)], [Ok("x", 1)])
    assert match_responses([request("a", id=True)], [Ok("x", True)]) == {
        True: Ok("x", True)
    }


def test_1_and_1_0_are_the_same_id() -> None:
    assert match_responses([request("a", id=1)], [Ok("x", 1.0)]) == {1: Ok("x", 1.0)}


@pytest.mark.parametrize(
    "reply,name",
    [({"jsonrpc": "2.0", "result": 1, "id": 1}, "dict"), ('[{"id": 1}]', "str")],
)
def test_a_reply_that_was_not_parsed_raises_type_error(reply: Any, name: str) -> None:
    with pytest.raises(TypeError) as exc:
        match_responses([request("a", id=1)], reply)
    assert str(exc.value) == f"responses must be what parse returned, not a {name}"


def test_requests_as_json_strings_raise_type_error() -> None:
    with pytest.raises(TypeError) as exc:
        match_responses([request_json("a", id=1)], [Ok("x", 1)])  # type: ignore[list-item]  # pyright: ignore[reportArgumentType]
    assert str(exc.value) == (
        "requests must be the dicts that request and notification return, not str"
    )


def test_requests_with_ids_1_and_true_cannot_share_a_dict() -> None:
    with pytest.raises(ValueError, match="Two requests have the id 1"):
        match_responses([request("a", id=1), request("b", id=True)], [])
