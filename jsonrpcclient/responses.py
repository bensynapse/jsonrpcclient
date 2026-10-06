"""Parse JSON-RPC 2.0 responses into `Ok` and `Error`.

`Ok`, `Error`, `InvalidResponse`, `parse` and `parse_json` are re-exported from
the `jsonrpcclient` package. The `Response` type alias lives only here:
`from jsonrpcclient.responses import Response`.
"""

import json
from typing import Any, Dict, Iterator, List, Mapping, NamedTuple, Union, cast, overload

Deserialized = Union[Dict[str, Any], List[Dict[str, Any]]]
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


Response = Union[Ok, Error]
"""The type of one parsed response. Use it to annotate your own functions."""


class InvalidResponse(KeyError, TypeError):
    """Raised when a response isn't a valid JSON-RPC 2.0 response.

    The message says what is wrong, for example
    `Invalid JSON-RPC response: missing 'id'`.

    It subclasses `KeyError` and `TypeError` because versions before 4.1.0
    raised one of those for a malformed response, so `except KeyError` and
    `except TypeError` still catch it.

    Added in 4.1.0.
    """

    def __str__(self) -> str:
        # KeyError would show the message in quotes.
        return Exception.__str__(self)


def _type_name(value: object) -> str:
    return "null" if value is None else type(value).__name__


def to_response(response: Dict[str, Any]) -> Response:
    """Turn one deserialized response object into an `Ok` or an `Error`.

    Internal; use `parse`. If the response has a non-null "error", it's an
    Error, even if it also has a "result". JSON-RPC 2.0 doesn't allow both, but
    JSON-RPC 1.0 style servers send "result": null alongside an error.

    Raises:
        InvalidResponse: If the response is malformed.
    """
    obj = cast(object, response)  # Callers may pass anything at runtime.
    if not isinstance(obj, Mapping):
        raise InvalidResponse(
            f"Invalid JSON-RPC response: expected an object, got {_type_name(obj)}"
        )
    checked = cast("Mapping[str, Any]", obj)
    if "id" not in checked:
        raise InvalidResponse("Invalid JSON-RPC response: missing 'id'")
    error: object = checked.get("error")
    if error is not None:
        if not isinstance(error, Mapping):
            raise InvalidResponse(
                "Invalid JSON-RPC response: 'error' must be an object, "
                f"got {_type_name(error)}"
            )
        error_obj = cast("Mapping[str, Any]", error)
        for member in ("code", "message"):
            if member not in error_obj:
                raise InvalidResponse(
                    f"Invalid JSON-RPC response: 'error' is missing '{member}'"
                )
        return Error(
            error_obj["code"],
            error_obj["message"],
            error_obj.get("data"),
            checked["id"],
        )
    if "result" in checked:
        return Ok(checked["result"], checked["id"])
    raise InvalidResponse(
        "Invalid JSON-RPC response: needs a 'result' or a non-null 'error'"
    )


@overload
def parse(deserialized: Dict[str, Any]) -> Response: ...


@overload
def parse(deserialized: List[Dict[str, Any]]) -> Iterator[Response]: ...


@overload
def parse(deserialized: Deserialized) -> Union[Response, Iterator[Response]]: ...


def parse(deserialized: Deserialized) -> Union[Response, Iterator[Response]]:
    """Parse a deserialized response, or a batch of them.

    A dict gives one `Ok` or `Error`. A list (a batch) gives a lazy iterator of
    `Ok` and `Error`: each item is parsed when you reach it, and the iterator
    can only be used once. Call `list()` on it if you need the responses more
    than once. Batch responses can come back in any order, so match them up by
    id.

    If a response has a non-null `error`, it is an `Error`, even if it also has
    a `result`.

    Args:
        deserialized: A response that has already been through `json.loads` (or
            your HTTP library's `.json()`).

    Returns:
        An `Ok` or `Error` for a dict, or an iterator of them for a list.

    Raises:
        InvalidResponse: If a response is malformed. For a batch, this happens
            when the iterator reaches the bad item. Subclasses `KeyError` and
            `TypeError`.
        TypeError: If `deserialized` is a `str`, `bytes` or `bytearray`. Use
            `parse_json` for those.

    Examples:
        >>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
        Ok(result='pong', id=1)
        >>> list(parse([{"jsonrpc": "2.0", "result": "pong", "id": 1}]))
        [Ok(result='pong', id=1)]
    """
    if isinstance(deserialized, (str, bytes, bytearray)):
        raise TypeError("Use parse_json on strings")
    return _parse(deserialized)


def _parse(deserialized: Deserialized) -> Union[Response, Iterator[Response]]:
    return (
        map(to_response, deserialized)
        if isinstance(deserialized, list)
        else to_response(deserialized)
    )


def parse_json(
    response: Union[str, bytes, bytearray], **kwargs: Any
) -> Union[Response, Iterator[Response]]:
    """Parse a response, or a batch of them, from a JSON string.

    The same as `parse(json.loads(response, **kwargs))`, except that it doesn't
    raise `TypeError` for a string.

    Args:
        response: The response body, as `str`, `bytes` or `bytearray`.
        **kwargs: Passed to `json.loads`, for example `parse_float=Decimal`.

    Returns:
        An `Ok` or `Error` for a JSON object, or an iterator of them for a JSON
            array.

    Raises:
        json.JSONDecodeError: If `response` isn't valid JSON. A `ValueError`
            subclass.
        InvalidResponse: If a response is malformed, including JSON that is
            neither an object nor an array.

    Examples:
        >>> parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}')
        Ok(result='pong', id=1)
    """
    deserialized: Deserialized = json.loads(response, **kwargs)
    return _parse(deserialized)
