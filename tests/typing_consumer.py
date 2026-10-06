"""Static typing checks, run by mypy and pyright (not by pytest).

Each line shows what a user of the library should see from a type checker.
"""

from typing import TYPE_CHECKING, Any, Dict, Iterator, Union

from jsonrpcclient import (
    Error,
    InvalidResponse,
    Ok,
    notification,
    notification_json,
    parse,
    parse_json,
    request,
    request_hex,
    request_json,
    request_json_uuid,
    request_random,
    request_uuid,
)
from jsonrpcclient.responses import Response

if TYPE_CHECKING:
    from typing_extensions import assert_type

    # List, tuple and dict params are all accepted.
    assert_type(request("sqrt", params=[1, 2]), Dict[str, Any])
    assert_type(request("sqrt", params=(1, 2)), Dict[str, Any])
    assert_type(request("sqrt", params={"x": 1}), Dict[str, Any])
    assert_type(request_hex("sqrt", [1]), Dict[str, Any])
    assert_type(request_random("sqrt", [1]), Dict[str, Any])
    assert_type(request_uuid("sqrt", [1], id="a"), Dict[str, Any])
    assert_type(notification("log", params=[1]), Dict[str, Any])

    # The JSON versions return str, not Any.
    assert_type(request_json("ping"), str)
    assert_type(request_json_uuid("ping", [1]), str)
    assert_type(notification_json("ping"), str)

    # A plain string is not valid params.
    request("sqrt", params="abc")  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]

    # parse knows a dict gives one response and a list gives an iterator.
    assert_type(parse({"jsonrpc": "2.0", "result": 1, "id": 1}), Union[Ok, Error])
    assert_type(parse([{"jsonrpc": "2.0", "result": 1, "id": 1}]), Iterator[Response])
    assert_type(parse_json("{}"), Union[Ok, Error, Iterator[Response]])

    parsed = parse({"jsonrpc": "2.0", "result": 1, "id": 1})
    if isinstance(parsed, Ok):
        assert_type(parsed.result, Any)
    else:
        assert_type(parsed, Error)
        assert_type(parsed.message, str)

    # InvalidResponse can be caught as either of the old exception types.
    key_error: KeyError = InvalidResponse("x")
    type_error: TypeError = InvalidResponse("x")
