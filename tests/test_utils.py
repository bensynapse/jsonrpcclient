"""Test utils.py"""

import json

from jsonrpcclient import parse, request
from jsonrpcclient.utils import compose


def test_compose() -> None:
    request_json = compose(json.dumps, request)
    assert request_json("foo", id=1) == '{"jsonrpc": "2.0", "method": "foo", "id": 1}'
    parse_json = compose(parse, json.loads)
    assert parse_json('{"jsonrpc": "2.0", "result": 1, "id": 1}').result == 1
