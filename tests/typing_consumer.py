"""Static typing checks, run by mypy and pyright (not by pytest).

Each line shows what a user of the library should see from a type checker.
"""

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal

from jsonrpcclient import (
    Error,
    InvalidResponse,
    Notification,
    Ok,
    Request,
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
    from typing import assert_type

    # List, tuple and dict params are all accepted.
    assert_type(request("sqrt", params=[1, 2]), Request)
    assert_type(request("sqrt", params=(1, 2)), Request)
    assert_type(request("sqrt", params={"x": 1}), Request)
    assert_type(request_hex("sqrt", [1]), Request)
    assert_type(request_random("sqrt", [1]), Request)
    assert_type(request_uuid("sqrt", [1], id="a"), Request)
    assert_type(notification("log", params=[1]), Notification)

    # Requests and notifications are TypedDicts, so their fields are typed.
    built = request("sqrt", [16])
    assert_type(built["method"], str)
    assert_type(built["jsonrpc"], Literal["2.0"])
    assert_type(built["id"], Any)
    assert_type(notification("log")["method"], str)
    built["bogus"]  # type: ignore[typeddict-item]  # pyright: ignore[reportGeneralTypeIssues]
    notification("log")["id"]  # type: ignore[typeddict-item]  # pyright: ignore[reportGeneralTypeIssues]

    # They still go wherever a mapping or JSON is expected.
    as_mapping: Mapping[str, Any] = request("ping")
    batch: list[Request | Notification] = [request("ping"), notification("log")]
    json.dumps(batch)

    # The JSON versions return str, not Any.
    assert_type(request_json("ping"), str)
    assert_type(request_json_uuid("ping", [1]), str)
    assert_type(notification_json("ping"), str)

    # A plain string is not valid params.
    request("sqrt", params="abc")  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]

    # parse knows a dict gives one response and a list gives a list.
    assert_type(parse({"jsonrpc": "2.0", "result": 1, "id": 1}), Ok | Error)
    assert_type(parse([{"jsonrpc": "2.0", "result": 1, "id": 1}]), list[Response])
    assert_type(parse_json("{}"), Ok | Error | list[Response])
    assert_type(parse({"result": 1, "id": 1}, strict=True), Ok | Error)
    assert_type(parse([{"result": 1, "id": 1}], strict=True), list[Response])
    assert_type(
        parse_json("{}", strict=True, parse_float=str), Ok | Error | list[Response]
    )

    parsed = parse({"jsonrpc": "2.0", "result": 1, "id": 1})
    if isinstance(parsed, Ok):
        assert_type(parsed.result, Any)
    else:
        assert_type(parsed, Error)
        assert_type(parsed.message, str)

    # InvalidResponse is a ValueError, and no longer a KeyError or TypeError.
    value_error: ValueError = InvalidResponse("x")
    key_error: KeyError = InvalidResponse("x")  # type: ignore[assignment]  # pyright: ignore[reportAssignmentType]
