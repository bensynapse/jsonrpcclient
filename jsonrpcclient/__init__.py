"""Create JSON-RPC 2.0 requests and parse responses in Python.

jsonrpcclient builds requests and parses responses. It doesn't send anything,
so you pair it with any transport. Documentation:
https://bensynapse.github.io/jsonrpcclient/
"""

from .requests import (
    notification,
    notification_json,
    request,
    request_hex,
    request_json,
    request_json_hex,
    request_json_random,
    request_json_uuid,
    request_random,
    request_uuid,
)
from .responses import Error, InvalidResponse, Ok, parse, parse_json

__version__ = "4.1.0"
"""The version of jsonrpcclient, as a string. Added in 4.0.4."""

__all__ = [
    "Error",
    "InvalidResponse",
    "Ok",
    "notification",
    "notification_json",
    "parse",
    "parse_json",
    "request",
    "request_hex",
    "request_json",
    "request_json_hex",
    "request_json_random",
    "request_json_uuid",
    "request_random",
    "request_uuid",
]
