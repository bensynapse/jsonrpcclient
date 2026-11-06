"""5.0 checks the type of method and params at run time (plans/5.0.md, D5)."""

from collections import OrderedDict
from collections.abc import Callable
from typing import Any, NamedTuple

import pytest

from jsonrpcclient import (
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
from jsonrpcclient.requests import request_impure

NOTIFICATIONS: list[Callable[..., Any]] = [notification, notification_json]
REQUESTS: list[Callable[..., Any]] = [
    request,
    request_hex,
    request_random,
    request_uuid,
    request_json,
    request_json_hex,
    request_json_random,
    request_json_uuid,
]


def call(build: Callable[..., Any], *args: Any) -> Any:
    """Build with a fixed id, so other tests still see ids start at 1."""
    if build in NOTIFICATIONS:
        return build(*args)
    return build(*args, id=1)


@pytest.mark.parametrize("build", NOTIFICATIONS + REQUESTS)
@pytest.mark.parametrize(
    "method,name", [(123, "int"), (None, "NoneType"), (b"ping", "bytes")]
)
def test_method_must_be_a_str(
    build: Callable[..., Any], method: Any, name: str
) -> None:
    with pytest.raises(TypeError) as exc:
        call(build, method)
    assert str(exc.value) == f"method must be a str, not {name}"


@pytest.mark.parametrize("build", NOTIFICATIONS + REQUESTS)
@pytest.mark.parametrize(
    "params,name",
    [
        ("16", "str"),
        ("", "str"),
        (b"x", "bytes"),
        (5, "int"),
        (0, "int"),
        (False, "bool"),
        ({1, 2}, "set"),
        (iter([1]), "list_iterator"),
    ],
)
def test_params_must_be_a_list_tuple_or_dict(
    build: Callable[..., Any], params: Any, name: str
) -> None:
    with pytest.raises(TypeError) as exc:
        call(build, "sqrt", params)
    assert str(exc.value) == f"params must be a list, tuple or dict, not {name}"


class Point(NamedTuple):
    x: int
    y: int


VALID_PARAMS: list[Any] = [
    None,
    [],
    (),
    {},
    [1],
    (1,),
    {"a": 1},
    OrderedDict(a=1),
    Point(1, 2),
]


@pytest.mark.parametrize("build", NOTIFICATIONS + REQUESTS)
@pytest.mark.parametrize(
    "params",
    VALID_PARAMS,
)
def test_lists_tuples_and_dicts_are_accepted(
    build: Callable[..., Any], params: Any
) -> None:
    call(build, "sqrt", params)


def test_subclasses_are_sent_as_lists_and_dicts() -> None:
    assert request("move", Point(1, 2), id=1)["params"] == [1, 2]
    assert request("move", OrderedDict(x=1), id=1)["params"] == {"x": 1}


def test_a_method_starting_with_rpc_is_allowed() -> None:
    assert notification("rpc.discover") == {"jsonrpc": "2.0", "method": "rpc.discover"}


def test_a_rejected_request_takes_no_id() -> None:
    ids = iter([1, 2])
    with pytest.raises(TypeError):
        request_impure(ids, "sqrt", "16")  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    assert request_impure(ids, "sqrt", [16])["id"] == 1
