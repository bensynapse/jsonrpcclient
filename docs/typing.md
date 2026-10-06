---
description: jsonrpcclient ships type hints for mypy and pyright. How parse is typed, how to narrow Ok and Error, and how to annotate your own code.
---

# Typing

jsonrpcclient ships type hints and a `py.typed` marker, so mypy, pyright and
your editor check your calls without any stubs. CI checks the library and its
typing examples with `mypy --strict` and `pyright --strict`.

## What parse returns

`parse` has overloads, so the type depends on what you pass:

| You pass | You get |
|---|---|
| a `dict` | `Ok | Error` |
| a `list` (a batch) | `Iterator[Ok | Error]` |
| something typed `Any` | `Any` |

`parse_json` takes a string, so a type checker can't tell one response from a
batch. It returns `Ok | Error | Iterator[Ok | Error]`.

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
from typing import Any, Dict

from jsonrpcclient import parse

data: Dict[str, Any] = {"jsonrpc": "2.0", "result": "pong", "id": 1}
parsed = parse(data)  # Ok | Error, so the type checker makes you narrow it
```

## Annotating your own code

`jsonrpcclient.responses.Response` is the type alias for `Ok | Error`. Use it
for functions that take or return one parsed response. This example passes
`mypy --strict` and `pyright --strict` in CI:

```python
--8<-- "docs/examples/typing_example.py"
```

```text title="Output"
result 'pong'
error -32601: Method not found
5
```

For params, `jsonrpcclient.requests.Params` is
`Dict[str, Any] | List[Any] | Tuple[Any, ...]`. A string isn't accepted:
`request("sqrt", "16")` is a type error.

The request functions return `Dict[str, Any]`, and the `*_json` versions
return `str`.
