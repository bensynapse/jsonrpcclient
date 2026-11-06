"""Parse JSON-RPC 2.0 responses into `Ok` and `Error`.

`Ok`, `Error`, `InvalidResponse`, `parse`, `parse_json` and `match_responses`
are re-exported from the `jsonrpcclient` package. The `Response` type alias
lives only here: `from jsonrpcclient.responses import Response`.
"""

import json
import math
import reprlib
from collections.abc import Iterable, Mapping
from typing import Any, NamedTuple, cast, overload

Deserialized = dict[str, Any] | list[dict[str, Any]]
"""What `parse` accepts: one response object, or a list of them for a batch."""


class Ok(NamedTuple):
    """A successful response.

    A named tuple, so it also unpacks as `result, id = parsed`.

    Examples:
        >>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
        Ok(result='pong', id=1)
    """

    result: Any
    """The `result` member of the response, as the server sent it."""
    id: Any
    """The id of the request this answers."""

    def __repr__(self) -> str:
        return f"Ok(result={self.result!r}, id={self.id!r})"


class Error(NamedTuple):
    """An error response.

    A named tuple of the members of the response's `error` object plus the id.
    The library doesn't check the types of `code` and `message`; they are
    whatever the server sent.

    Examples:
        >>> error = {"code": -32601, "message": "Method not found"}
        >>> parse({"jsonrpc": "2.0", "error": error, "id": 1})
        Error(code=-32601, message='Method not found', data=None, id=1)
    """

    code: int
    """The error code, for example -32601 for "Method not found"."""
    message: str
    """A short description of the error."""
    data: Any
    """Extra information from the server, or None if it didn't send any."""
    id: Any
    """The id of the request this answers. None if the server couldn't read the
    request's id, for example after a parse error."""

    def __repr__(self) -> str:
        return (
            f"Error(code={self.code!r}, message={self.message!r}, "
            f"data={self.data!r}, id={self.id!r})"
        )


Response = Ok | Error
"""The type of one parsed response. Use it to annotate your own functions."""


class InvalidResponse(ValueError):
    """Raised when a response isn't a valid JSON-RPC 2.0 response.

    The message says what is wrong, for example
    `Invalid JSON-RPC response: missing 'id'`.

    It's a `ValueError`, like `json.JSONDecodeError`, so one `except ValueError`
    catches a body that isn't JSON and one that isn't JSON-RPC.

    Added in 4.1.0. Changed in 5.0: it subclasses `ValueError`. In 4.x it
    subclassed `KeyError` and `TypeError`, which 4.0 raised.
    """


def _type_name(value: object) -> str:
    return "null" if value is None else type(value).__name__


def _invalid(reason: str, index: int | None) -> InvalidResponse:
    where = "" if index is None else f" at index {index} of the batch"
    return InvalidResponse(f"Invalid JSON-RPC response{where}: {reason}")


def _check_strict(response: Mapping[str, Any], index: int | None) -> None:
    """Check the rules that `strict=True` adds. See `parse`."""
    if "jsonrpc" not in response:
        raise _invalid("missing 'jsonrpc'", index)
    if response["jsonrpc"] != "2.0":
        got = reprlib.repr(response["jsonrpc"])
        raise _invalid(f"'jsonrpc' must be \"2.0\", got {got}", index)
    if "id" not in response:
        raise _invalid("missing 'id'", index)
    id_: object = response["id"]
    if isinstance(id_, bool) or not isinstance(id_, (str, int, float, type(None))):
        raise _invalid(
            f"'id' must be a string, a number or null, got {_type_name(id_)}", index
        )
    if isinstance(id_, float) and not math.isfinite(id_):
        raise _invalid(f"'id' must be a string, a number or null, got {id_!r}", index)
    if "result" in response and "error" in response:
        raise _invalid("has both 'result' and 'error'", index)
    if "error" not in response:
        if "result" not in response:
            raise _invalid("needs a 'result' or an 'error'", index)
        return
    error: object = response["error"]
    if not isinstance(error, Mapping):
        raise _invalid(f"'error' must be an object, got {_type_name(error)}", index)
    error_obj = cast("Mapping[str, Any]", error)
    for member in ("code", "message"):
        if member not in error_obj:
            raise _invalid(f"'error' is missing '{member}'", index)
    code: object = error_obj["code"]
    if isinstance(code, bool) or not isinstance(code, int):
        raise _invalid(f"'error.code' must be an int, got {_type_name(code)}", index)
    message: object = error_obj["message"]
    if not isinstance(message, str):
        raise _invalid(
            f"'error.message' must be a str, got {_type_name(message)}", index
        )


def to_response(
    response: dict[str, Any], index: int | None = None, *, strict: bool = False
) -> Response:
    """Turn one deserialized response object into an `Ok` or an `Error`.

    Internal; use `parse`. If the response has a non-null "error", it's an
    Error, even if it also has a "result". JSON-RPC 2.0 doesn't allow both, but
    JSON-RPC 1.0 style servers send "result": null alongside an error.

    Args:
        response: One response object.
        index: Its position in a batch, for the error message.
        strict: Check the rules that `parse(..., strict=True)` checks.

    Raises:
        InvalidResponse: If the response is malformed.
    """
    obj = cast(object, response)  # Callers may pass anything at runtime.
    if not isinstance(obj, Mapping):
        raise _invalid(f"expected an object, got {_type_name(obj)}", index)
    checked = cast("Mapping[str, Any]", obj)
    if strict:
        _check_strict(checked, index)
    if "id" not in checked:
        raise _invalid("missing 'id'", index)
    error: object = checked.get("error")
    if error is not None:
        if not isinstance(error, Mapping):
            raise _invalid(f"'error' must be an object, got {_type_name(error)}", index)
        error_obj = cast("Mapping[str, Any]", error)
        for member in ("code", "message"):
            if member not in error_obj:
                raise _invalid(f"'error' is missing '{member}'", index)
        return Error(
            error_obj["code"],
            error_obj["message"],
            error_obj.get("data"),
            checked["id"],
        )
    if "result" in checked:
        return Ok(checked["result"], checked["id"])
    raise _invalid("needs a 'result' or a non-null 'error'", index)


@overload
def parse(deserialized: dict[str, Any], *, strict: bool = False) -> Response: ...


@overload
def parse(
    deserialized: list[dict[str, Any]], *, strict: bool = False
) -> list[Response]: ...


@overload
def parse(
    deserialized: Deserialized, *, strict: bool = False
) -> Response | list[Response]: ...


def parse(
    deserialized: Deserialized, *, strict: bool = False
) -> Response | list[Response]:
    """Parse a deserialized response, or a batch of them.

    A dict gives one `Ok` or `Error`. A list (a batch) gives a list of `Ok` and
    `Error`, in the order the server sent them. Every item is checked before
    `parse` returns. Batch responses can come back in any order, so match them
    up by id with `match_responses`. An empty batch raises `InvalidResponse`.

    Changed in 5.0: a batch gives a list. 4.x gave a one-pass iterator, which
    raised for a bad item only when the loop reached it.

    By default `parse` is lenient, as in 4.x. It needs an `id`, and a `result`
    or an `error` object with `code` and `message`. If a response has a
    non-null `error`, it is an `Error`, even if it also has a `result`.

    Args:
        deserialized: A response that has already been through `json.loads` (or
            your HTTP library's `.json()`).
        strict: Also check the other JSON-RPC 2.0 rules: `"jsonrpc"` is
            `"2.0"`, a response has exactly one of `result` and `error` (a
            null `error` counts), `error.code` is an int and `error.message` a
            str, and `id` is a string, a number or null. New in 5.0.

    Returns:
        An `Ok` or `Error` for a dict, or a list of them for a list.

    Raises:
        InvalidResponse: If a response is malformed. For a batch, the message
            gives the index of the first bad item. A `ValueError`.
        TypeError: If `deserialized` is a `str`, `bytes` or `bytearray`. Use
            `parse_json` for those.

    Examples:
        >>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
        Ok(result='pong', id=1)
        >>> parse([{"jsonrpc": "2.0", "result": "pong", "id": 1}])
        [Ok(result='pong', id=1)]
    """
    if isinstance(deserialized, (str, bytes, bytearray)):
        raise TypeError("Use parse_json on strings")
    return _parse(deserialized, strict)


def _parse(deserialized: Deserialized, strict: bool) -> Response | list[Response]:
    if isinstance(deserialized, list):
        if not deserialized:
            raise InvalidResponse("Invalid JSON-RPC response: batch must not be empty")
        return [
            to_response(item, index, strict=strict)
            for index, item in enumerate(deserialized)
        ]
    return to_response(deserialized, strict=strict)


def parse_json(
    response: str | bytes | bytearray, *, strict: bool = False, **kwargs: Any
) -> Response | list[Response]:
    """Parse a response, or a batch of them, from a JSON string.

    The same as `parse(json.loads(response, **kwargs), strict=strict)`, except
    that it doesn't raise `TypeError` for a string.

    Args:
        response: The response body, as `str`, `bytes` or `bytearray`.
        strict: The same as `parse`'s. New in 5.0. In 4.x, `strict` went to
            `json.loads`. For that option, call
            `parse(json.loads(response, strict=False))`.
        **kwargs: Passed to `json.loads`, for example `parse_float=Decimal`.

    Returns:
        An `Ok` or `Error` for a JSON object, or a list of them for a JSON
            array.

    Raises:
        ValueError: If `response` isn't valid JSON. Usually this is
            `json.JSONDecodeError`, or `UnicodeDecodeError` for bytes that
            aren't valid UTF-8.
        InvalidResponse: If a response is malformed, including JSON that is
            neither an object nor an array.

    Examples:
        >>> parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}')
        Ok(result='pong', id=1)
    """
    deserialized: Deserialized = json.loads(response, **kwargs)
    return _parse(deserialized, strict)


def _id_key(id_: Any) -> tuple[bool, Any]:
    """A key that compares ids as JSON does: true isn't 1, though 1.0 is."""
    return (isinstance(id_, bool), id_)


def match_responses(
    requests: Iterable[Mapping[str, Any]], responses: Response | Iterable[Response]
) -> dict[Any, Response]:
    """Match a batch's responses to its requests by id.

    Pass the batch as you sent it, and what `parse` returned for the reply.
    Notifications in the batch are skipped, since they get no response.

    - If `responses` is one `Error`, the server rejected the whole batch, and
      every request gets that error.
    - A response with a null id that matches no request is an error the server
      couldn't tie to a request, for example one it couldn't read. A request
      without a response of its own gets one of those, in order. Any left over
      belong to notifications, and are dropped.

    New in 5.0.

    Args:
        requests: The requests and notifications in the batch, as sent.
        responses: What `parse` returned for the reply.

    Returns:
        A dict from each request's id to its `Ok` or `Error`, in the order of
            the requests.

    Raises:
        InvalidResponse: If a request has no response, a response's id matches
            no request, two responses have the same id, or `responses` is one
            `Ok`.
        ValueError: If two requests have the same id.
        TypeError: If `responses` isn't what `parse` returned, `requests`
            holds something other than dicts, or a request's id isn't
            hashable. JSON-RPC ids are strings, numbers or null, which all are.
            A response's id that isn't hashable matches no request.

    Examples:
        >>> from jsonrpcclient import request
        >>> batch = [request("ping", id=1), request("add", [2, 3], id=2)]
        >>> reply = [
        ...     {"jsonrpc": "2.0", "result": 5, "id": 2},
        ...     {"jsonrpc": "2.0", "result": "pong", "id": 1},
        ... ]
        >>> match_responses(batch, parse(reply))
        {1: Ok(result='pong', id=1), 2: Ok(result=5, id=2)}
    """
    ids: list[Any] = []
    for item in requests:
        if not isinstance(cast(object, item), Mapping):
            raise TypeError(
                "requests must be the dicts that request and notification return, "
                f"not {type(item).__name__}"
            )
        if "id" in item:
            ids.append(item["id"])
    # The result is a dict, so ids that Python calls equal, such as 1 and
    # True, can't both be keys.
    if len(set(ids)) != len(ids):
        duplicate = next(id_ for id_ in ids if ids.count(id_) > 1)
        raise ValueError(
            f"Two requests have the id {duplicate!r}, so their responses can't "
            "be told apart"
        )
    keys = [_id_key(id_) for id_ in ids]
    wanted = set(keys)
    if isinstance(responses, Error):
        return dict.fromkeys(ids, responses)
    if isinstance(responses, Ok):
        raise InvalidResponse(
            "Invalid JSON-RPC response: a batch gets a list of responses, or one "
            f"Error if the server rejected it, not {responses!r}"
        )
    if isinstance(cast(object, responses), (Mapping, str, bytes, bytearray)):
        raise TypeError(
            f"responses must be what parse returned, not a {type(responses).__name__}"
        )
    found: dict[Any, Response] = {}
    unread: list[Error] = []
    for response in responses:
        if not isinstance(cast(object, response), (Ok, Error)):
            raise TypeError(
                "responses must be what parse returned, not a list of "
                f"{type(response).__name__}"
            )
        key = _id_key(response.id)
        try:
            known = key in wanted
        except TypeError:  # An unhashable id, such as [1].
            known = False
        if known:
            if key in found:
                raise InvalidResponse(
                    f"Invalid JSON-RPC response: two responses for id {response.id!r}"
                )
            found[key] = response
        elif response.id is None and isinstance(response, Error):
            unread.append(response)
        else:
            raise InvalidResponse(
                f"Invalid JSON-RPC response: id {response.id!r} matches no request"
            )
    matched: dict[Any, Response] = {}
    for id_, key in zip(ids, keys, strict=True):
        if key in found:
            matched[id_] = found[key]
        elif unread:
            matched[id_] = unread.pop(0)
        else:
            raise InvalidResponse(
                f"Invalid JSON-RPC response: no response for id {id_!r}"
            )
    return matched
