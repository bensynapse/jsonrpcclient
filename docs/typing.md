---
description: jsonrpcclient ships type hints for mypy and pyright. How parse is typed, how to narrow Ok and Error, and how to annotate your own code.
---

# Typing

jsonrpcclient ships type hints and a `py.typed` marker, so mypy, pyright and
your editor check your calls without any stubs. CI checks the library and its
typing examples with mypy and pyright in strict mode.

## What parse returns

`parse` has overloads, so the type depends on what you pass:

| You pass | You get |
|---|---|
| a `dict` | `Ok | Error` |
| a `list` (a batch) | `list[Ok | Error]` |
| something typed `Any` | `Any` |

`parse_json` takes a string, so a type checker can't tell one response from a
batch. It returns `Ok | Error | list[Ok | Error]`.

!!! info "New in 4.0.4"
    Before 4.0.4, `parse_json` was typed as returning `Any`, and `parse` had
    no overloads.

## Narrow before you use .result

`result` only exists on `Ok`. So this fails type checking, even though it
runs when the call succeeds:

```python
from jsonrpcclient import parse

parsed = parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
print(parsed.result)  # mypy: Item "Error" of "Ok | Error" has no attribute "result"
```

```text title="Output"
pong
```

It's also a real bug: when the server sends an error, `parsed` is an `Error`
and `.result` raises `AttributeError`. Check the type first with
`isinstance` or `match`, as in [Responses](responses.md#using-the-result).
In a quick script you can assert it instead:

```python
from jsonrpcclient import Ok, parse

parsed = parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
assert isinstance(parsed, Ok), parsed
print(parsed.result)
```

```text title="Output"
pong
```

## Watch out for Any

`response.json()` in requests, httpx and aiohttp returns `Any`. Pass that to
`parse` and the result is `Any` too, so the type checker stops checking:
`parse(response.json()).result` passes mypy and still fails at runtime on an
error response. Narrow with `isinstance` anyway, or annotate the data first:

```python
from typing import Any

from jsonrpcclient import parse

data: dict[str, Any] = {"jsonrpc": "2.0", "result": "pong", "id": 1}
parsed = parse(data)  # Ok | Error, so the type checker makes you narrow it
```

## Annotating your own code

`jsonrpcclient.responses.Response` is the type alias for `Ok | Error`. Use it
for functions that take or return one parsed response. This example passes
mypy and pyright in strict mode in CI:

```python
--8<-- "docs/examples/typing_example.py"
```

```text title="Output"
result 'pong'
error -32601: Method not found
5
```

For params, `jsonrpcclient.requests.Params` is
`dict[str, Any] | list[Any] | tuple[Any, ...]`. A string isn't accepted:
`request("sqrt", "16")` is a type error, and a `TypeError` at run time.

## Requests are TypedDicts

`request` and its variants return a `Request`, and `notification` returns a
`Notification`. Both are `TypedDict`s, so a type checker knows their keys.
At run time they're plain dicts. The `*_json` versions return `str`.

```python
from jsonrpcclient import Notification, Request, notification, request

batch: list[Request | Notification] = [request("ping"), notification("log")]
first = batch[0]
print(first["method"])
print(first.get("params"))
```

```text title="Output"
ping
None
```

`params` is left out when it's empty, so the type marks it `NotRequired`.
Read it with `.get("params")`. A type checker flags `["params"]`, which
raises `KeyError` for a request without params.

!!! info "Changed in 5.0"
    The request functions returned `dict[str, Any]` before 5.0. mypy doesn't
    accept a `TypedDict` where `dict[str, Any]` is expected, so annotate with
    `Request`, `Notification` or `Mapping[str, Any]` instead. A request can
    no longer be given extra keys without a type error.
