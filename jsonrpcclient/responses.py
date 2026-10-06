"""Responses"""

import json
from typing import Any, Dict, Iterator, List, Mapping, NamedTuple, Union, cast, overload

Deserialized = Union[Dict[str, Any], List[Dict[str, Any]]]


class Ok(NamedTuple):
    """Ok response"""

    result: Any
    id: Any

    def __repr__(self) -> str:
        return f"Ok(result={self.result!r}, id={self.id!r})"


class Error(NamedTuple):
    """Error response"""

    code: int
    message: str
    data: Any
    id: Any

    def __repr__(self) -> str:
        return (
            f"Error(code={self.code!r}, message={self.message!r}, "
            f"data={self.data!r}, id={self.id!r})"
        )


Response = Union[Ok, Error]


class InvalidResponse(KeyError, TypeError):
    """The server's response isn't a valid JSON-RPC 2.0 response.

    It subclasses KeyError and TypeError because earlier versions raised one of
    those for a malformed response, so existing handlers still catch it.
    """

    def __str__(self) -> str:
        # KeyError would show the message in quotes.
        return Exception.__str__(self)


def _type_name(value: object) -> str:
    return "null" if value is None else type(value).__name__


def to_response(response: Dict[str, Any]) -> Response:
    """Create an Ok or Error from one deserialized response object.

    If the response has a non-null "error", it's an Error, even if it also has a
    "result". JSON-RPC 2.0 doesn't allow both, but JSON-RPC 1.0 servers send
    "result": null alongside an error.

    Raises InvalidResponse if the response is malformed.
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

    A dict gives one Ok or Error. A list (a batch) gives a lazy iterator of Ok
    and Error: each item is parsed when you reach it, and the iterator can only
    be used once. Call list() on it if you need the responses more than once.
    Batch responses can come back in any order, so match them up by id.

    Raises InvalidResponse (a KeyError and TypeError subclass) if a response is
    malformed. For a batch, that happens when the iterator reaches the bad item.
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
    """Parse a JSON string. Same as parse(json.loads(response, **kwargs))."""
    deserialized: Deserialized = json.loads(response, **kwargs)
    return _parse(deserialized)
