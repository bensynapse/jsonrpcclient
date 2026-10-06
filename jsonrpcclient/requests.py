"""Requests"""

import json
from functools import partial
from typing import Any, Dict, Iterator, Tuple, Union

from . import id_generators
from .sentinels import NOID
from .utils import compose


def notification_pure(
    method: str, params: Union[Dict[str, Any], Tuple[Any, ...]]
) -> Dict[str, Any]:
    """Create a notification"""
    return {
        "jsonrpc": "2.0",
        "method": method,
        **({"params": params} if params else {}),
    }


def notification(
    method: str, params: Union[Dict[str, Any], Tuple[Any, ...], None] = None
) -> Dict[str, Any]:
    """Create a notification, optionally passing params"""
    return notification_pure(method, params if params else ())


# JSON (string) version of "notification"
notification_json = compose(json.dumps, notification)


def request_pure(
    id_generator: Iterator[Any],
    method: str,
    params: Union[Dict[str, Any], Tuple[Any, ...]],
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
    params: Union[Dict[str, Any], Tuple[Any, ...], None] = None,
    id: Any = NOID,
) -> Dict[str, Any]:
    """Create a request, optionally passing params and id"""
    return request_pure(
        id_generator or id_generators.decimal(), method, params or (), id
    )


# Create a request, auto-populating the id
request_natural = partial(request_impure, id_generators.decimal())
request_hex = partial(request_impure, id_generators.hexadecimal())
request_random = partial(request_impure, id_generators.random())
request_uuid = partial(request_impure, id_generators.uuid())
request = request_natural  # Standard request has incrementing decimal ids.

# JSON (string) versions of the above id-populating functions
request_json = compose(json.dumps, request_natural)
request_json_hex = compose(json.dumps, request_hex)
request_json_random = compose(json.dumps, request_random)
request_json_uuid = compose(json.dumps, request_uuid)
