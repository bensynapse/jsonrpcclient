"""4.2.0 warns about the calls that 5.0 handles differently (plans/5.0.md, D10)."""

import json
import warnings
from typing import Any, Callable, Dict

import pytest

import jsonrpcclient
from jsonrpcclient import (
    notification,
    notification_json,
    parse,
    parse_json,
    request,
    request_hex,
    request_json,
    request_json_hex,
    request_json_random,
    request_json_uuid,
    request_random,
    request_uuid,
)

BUILDERS = [
    request,
    request_hex,
    request_random,
    request_uuid,
    request_json,
    request_json_hex,
    request_json_random,
    request_json_uuid,
    notification,
    notification_json,
]


def call(build: Callable[..., Any], *args: Any) -> Any:
    """Build with a fixed id, so other tests still see ids start at 1."""
    if build in (notification, notification_json):
        return build(*args)
    return build(*args, id=1)


@pytest.mark.parametrize("build", BUILDERS)
def test_method_that_is_not_a_str_warns(build: Callable[..., Any]) -> None:
    with pytest.warns(FutureWarning, match="5.0 raises TypeError") as record:
        call(build, 123)
    assert record[0].filename == __file__


@pytest.mark.parametrize("build", BUILDERS)
@pytest.mark.parametrize("params", ["16", "", 5, 0, False])
def test_params_that_are_not_a_list_tuple_or_dict_warn(
    build: Callable[..., Any], params: Any
) -> None:
    with pytest.warns(FutureWarning, match="5.0 raises TypeError") as record:
        call(build, "sqrt", params)
    assert record[0].filename == __file__


@pytest.mark.parametrize("params", [b"x", {1, 2}, iter([1])])
def test_unserializable_params_warn(params: Any) -> None:
    with pytest.warns(FutureWarning, match="5.0 raises TypeError"):
        request("sqrt", params, id=1)


def test_params_warning_names_the_type() -> None:
    with pytest.warns(FutureWarning) as record:
        request("sqrt", "16", id=1)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    assert str(record[0].message) == (
        "params must be a list, tuple or dict, not str. 4.x sends it anyway, "
        "but 5.0 raises TypeError."
    )


def test_method_warning_names_the_type() -> None:
    with pytest.warns(FutureWarning) as record:
        notification(None)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    assert str(record[0].message) == (
        "method must be a str, not NoneType. 4.x sends it anyway, "
        "but 5.0 raises TypeError."
    )


def test_requests_still_work_as_in_4_1() -> None:
    with pytest.warns(FutureWarning):
        sent = request("sqrt", "16", id=1)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
        assert sent == {
            "jsonrpc": "2.0",
            "method": "sqrt",
            "params": "16",
            "id": 1,
        }
    with pytest.warns(FutureWarning):
        sent = notification("log", "")  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
        assert sent == {"jsonrpc": "2.0", "method": "log"}


@pytest.mark.parametrize("build", BUILDERS)
@pytest.mark.parametrize("params", [None, [], (), {}, [1], (1,), {"a": 1}])
def test_valid_requests_do_not_warn(build: Callable[..., Any], params: Any) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        call(build, "sqrt", params)


def test_parse_json_strict_warns() -> None:
    with pytest.warns(FutureWarning, match="parse_json's strict") as record:
        parsed = parse_json('{"result": "a\tb", "id": 1}', strict=False)
    assert parsed == jsonrpcclient.Ok("a\tb", 1)
    assert record[0].filename == __file__


def test_parse_json_strict_is_still_passed_to_json_loads() -> None:
    with pytest.warns(FutureWarning), pytest.raises(json.JSONDecodeError):
        parse_json('{"result": "a\tb", "id": 1}', strict=True)


def test_parse_json_other_kwargs_do_not_warn() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        parse_json('{"result": 1.5, "id": 1}', parse_float=str)


def test_parse_does_not_warn() -> None:
    response: Dict[str, Any] = {"jsonrpc": "2.0", "result": 1, "id": 1}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        parse(response)
        list(parse([response]))
