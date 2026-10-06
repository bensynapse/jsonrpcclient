"""Responses"""

import json
from typing import Any, Dict, Iterable, List, NamedTuple, Union

from .utils import compose

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


def to_response(response: Dict[str, Any]) -> Response:
    """Create a Response namedtuple from a dict"""
    return (
        Ok(response["result"], response["id"])
        if "result" in response
        else Error(
            response["error"]["code"],
            response["error"]["message"],
            response["error"].get("data"),
            response["id"],
        )
    )


def parse(deserialized: Deserialized) -> Union[Response, Iterable[Response]]:
    """Create a Response or list of Responses from a dict or list of dicts"""
    if isinstance(deserialized, str):
        raise TypeError("Use parse_json on strings")
    return (
        map(to_response, deserialized)
        if isinstance(deserialized, list)
        else to_response(deserialized)
    )


parse_json = compose(parse, json.loads)
