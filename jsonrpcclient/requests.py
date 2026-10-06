"""Requests"""

import json
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from . import id_generators
from .sentinels import NOID

# JSON-RPC params are either positional (a list or tuple) or named (a dict).
Params = Union[Dict[str, Any], List[Any], Tuple[Any, ...]]


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
    """Create a notification, optionally passing params"""
    return notification_pure(method, params if params else ())


def notification_json(method: str, params: Optional[Params] = None) -> str:
    """JSON (string) version of "notification"."""
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
    """Create a request. Unless id is given, ids count up from 1."""
    return request_impure(_decimal_ids, method, params, id)


def request_hex(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Create a request. Unless id is given, ids count up in hex: "1", ..., "a"."""
    return request_impure(_hex_ids, method, params, id)


def request_random(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Create a request. Unless id is given, ids are random 8-character strings."""
    return request_impure(_random_ids, method, params, id)


def request_uuid(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> Dict[str, Any]:
    """Create a request. Unless id is given, ids are random UUIDs (version 4)."""
    return request_impure(_uuid_ids, method, params, id)


# Older name for request.
request_natural = request


def request_json(method: str, params: Optional[Params] = None, id: Any = NOID) -> str:
    """JSON (string) version of "request"."""
    return json.dumps(request(method, params, id))


def request_json_hex(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> str:
    """JSON (string) version of "request_hex"."""
    return json.dumps(request_hex(method, params, id))


def request_json_random(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> str:
    """JSON (string) version of "request_random"."""
    return json.dumps(request_random(method, params, id))


def request_json_uuid(
    method: str, params: Optional[Params] = None, id: Any = NOID
) -> str:
    """JSON (string) version of "request_uuid"."""
    return json.dumps(request_uuid(method, params, id))
