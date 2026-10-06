"""Build JSON-RPC 2.0 requests and notifications.

Everything here is re-exported from the `jsonrpcclient` package, so import it
from there: `from jsonrpcclient import request`.
"""

import json
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from . import id_generators
from .sentinels import NOID

Params = Union[Dict[str, Any], List[Any], Tuple[Any, ...]]
"""The type of `params`: a list or tuple for positional params, a dict for named.

A tuple is sent as a list. Empty params are left out of the request.
"""


def notification_pure(method: str, params: Params) -> Dict[str, Any]:
    """Create a notification"""
    return {
        "jsonrpc": "2.0",
        "method": method,
        **(
            {"params": list(params) if isinstance(params, tuple) else params}
            if params
            else {}
        ),
    }


def notification(method: str, params: Optional[Params] = None) -> Dict[str, Any]:
    """Build a notification: a request with no id, which the server doesn't answer.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the notification if empty or not given.

    Returns:
        The notification as a dict, ready to serialize. Tuple params are
            converted to a list.

    Examples:
        >>> notification("log", ["hello"])
        {'jsonrpc': '2.0', 'method': 'log', 'params': ['hello']}
    """
    return notification_pure(method, params if params else ())


def notification_json(method: str, params: Optional[Params] = None) -> str:
    """Build a notification as a JSON string.

    The same as `json.dumps(notification(method, params))`.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.

    Returns:
        The notification serialized with `json.dumps`.

    Raises:
        TypeError: If `params` holds something `json.dumps` can't serialize.

    Examples:
        >>> notification_json("log", ["hello"])
        '{"jsonrpc": "2.0", "method": "log", "params": ["hello"]}'
    """
    return json.dumps(notification(method, params))


def request_pure(
    id_generator: Iterator[Any],
    method: str,
    params: Params,
    id: Any,
) -> Dict[str, Any]:
    """Create a request"""
    return {
        "jsonrpc": "2.0",
        "method": method,
        **(
            {"params": list(params) if isinstance(params, tuple) else params}
            if params
            else {}
        ),
        "id": id if id is not NOID else next(id_generator),
    }


def request_impure(
    id_generator: Iterator[Any],
    method: str,
    params: Optional[Params] = None,
    id: Any = NOID,
) -> Dict[str, Any]:
    """Create a request, optionally passing params and id.

    If id is not given, the next value from id_generator is used. If you share
    your own id_generator between threads, make sure it's thread-safe. The ones
    in jsonrpcclient.id_generators are.
    """
    return request_pure(
        id_generator or id_generators.decimal(), method, params or (), id
    )


_decimal_ids = id_generators.decimal()
_hex_ids = id_generators.hexadecimal()
_random_ids = id_generators.random()
_uuid_ids = id_generators.uuid()


def request(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Build a request with an id.

    Unless you pass `id`, ids count up from 1. The sequence is shared by the
    whole process and is safe to use from several threads.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given. Only the type hint
            restricts it; nothing is checked at runtime.
        id: The id to use instead of the next one in the sequence. Any JSON
            value works. `id=None` sends `"id": null`; it does not make a
            notification (use `notification` for that).

    Returns:
        The request as a dict, ready to serialize. Tuple params are converted
            to a list.

    Examples:
        >>> request("sqrt", [16], id=1)
        {'jsonrpc': '2.0', 'method': 'sqrt', 'params': [16], 'id': 1}
        >>> request("greet", {"name": "Ada"}, id="abc")
        {'jsonrpc': '2.0', 'method': 'greet', 'params': {'name': 'Ada'}, 'id': 'abc'}
    """
    return request_impure(_decimal_ids, method, params, id)


def request_hex(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Build a request whose ids count up in hexadecimal strings: "1", ... "9", "a".

    The hex sequence is separate from the one `request` uses.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request as a dict, ready to serialize.
    """
    return request_impure(_hex_ids, method, params, id)


def request_random(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Build a request whose id is a random string of 8 lowercase letters and digits.

    Random ids are not guaranteed to be unique; use `request_uuid` if a clash
    would matter.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request as a dict, ready to serialize.
    """
    return request_impure(_random_ids, method, params, id)


def request_uuid(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Build a request whose id is a random UUID (version 4) string.

    Use this when several processes or machines send requests to the same
    server.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request as a dict, ready to serialize.
    """
    return request_impure(_uuid_ids, method, params, id)


request_natural = request
"""An older name for `request`, kept so that old code still works."""


def request_json(method: str, params: Optional[Params] = None, id: Any = NOID) -> str:
    """Build a request as a JSON string.

    The same as `json.dumps(request(method, params, id))`, and it takes the next
    id from the same sequence as `request`.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request serialized with `json.dumps`.

    Raises:
        TypeError: If `params` or `id` holds something `json.dumps` can't
            serialize.

    Examples:
        >>> request_json("ping", id=1)
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
    """
    return json.dumps(request(method, params, id))


def request_json_hex(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> str:
    """Build a request with a hexadecimal id, as a JSON string.

    The same as `json.dumps(request_hex(method, params, id))`.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request serialized with `json.dumps`.

    Raises:
        TypeError: If `params` or `id` holds something `json.dumps` can't
            serialize.
    """
    return json.dumps(request_hex(method, params, id))


def request_json_random(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> str:
    """Build a request with a random id, as a JSON string.

    The same as `json.dumps(request_random(method, params, id))`.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request serialized with `json.dumps`.

    Raises:
        TypeError: If `params` or `id` holds something `json.dumps` can't
            serialize.
    """
    return json.dumps(request_random(method, params, id))


def request_json_uuid(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> str:
    """Build a request with a UUID id, as a JSON string.

    The same as `json.dumps(request_uuid(method, params, id))`.

    Args:
        method: The name of the method to call.
        params: Positional params as a list or tuple, or named params as a dict.
            Left out of the request if empty or not given.
        id: The id to use instead of the next one in the sequence.

    Returns:
        The request serialized with `json.dumps`.

    Raises:
        TypeError: If `params` or `id` holds something `json.dumps` can't
            serialize.
    """
    return json.dumps(request_uuid(method, params, id))
