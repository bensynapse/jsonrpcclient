---
description: Parse JSON-RPC 2.0 responses in Python with parse and parse_json, and handle the Ok and Error results with isinstance or match.
---

# Responses

## Parsing a response

`parse` turns a deserialized response into an `Ok` or an `Error`. Both are
named tuples.

```pycon
>>> from jsonrpcclient import parse
>>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
Ok(result='pong', id=1)
>>> parse(
...     {
...         "jsonrpc": "2.0",
...         "error": {"code": -32601, "message": "Method not found"},
...         "id": 1,
...     }
... )
Error(code=-32601, message='Method not found', data=None, id=1)
```

If you have a string or bytes, use `parse_json`. It calls `json.loads` first,
and passes any keyword arguments on to it:

```pycon
>>> from decimal import Decimal
>>> from jsonrpcclient import parse_json
>>> parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}')
Ok(result='pong', id=1)
>>> parse_json('{"jsonrpc": "2.0", "result": 1.1, "id": 1}', parse_float=Decimal)
Ok(result=Decimal('1.1'), id=1)
```

`parse` refuses a string or bytes with `TypeError: Use parse_json on strings`.

## Ok and Error

`Ok` has two fields:

- `result`: the server's result, as it sent it
- `id`: the id of the request it answers

`Error` has four:

- `code`: the error code, such as `-32601` for "Method not found"
- `message`: a short description
- `data`: extra details from the server, or `None` if it sent none
- `id`: the id of the request, or `None` if the server couldn't read it

## Using the result

Check which one you got with `isinstance`:

```python
import logging

from jsonrpcclient import Error, Ok, parse

parsed = parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    logging.error(parsed.message)
```

```text title="Output"
pong
```

On Python 3.10 and later you can use `match`:

<!-- min-python: 3.10 -->
```python
import logging

from jsonrpcclient import Error, Ok, parse

match parse({"jsonrpc": "2.0", "result": "pong", "id": 1}):
    case Ok(result=result):
        print(result)
    case Error(code=code, message=message):
        logging.error("%s (code %s)", message, code)
```

```text title="Output"
pong
```

A type checker needs one of these checks before you use `.result`. See
[Typing](typing.md).

## Batch responses

Parsing a list gives an iterator of responses, which you match to your
requests by id:

```pycon
>>> responses = parse(
...     [
...         {"jsonrpc": "2.0", "result": "pong", "id": 2},
...         {
...             "jsonrpc": "2.0",
...             "error": {"code": -32601, "message": "Method not found"},
...             "id": 1,
...         },
...     ]
... )
>>> by_id = {response.id: response for response in responses}
>>> by_id[1]
Error(code=-32601, message='Method not found', data=None, id=1)
>>> by_id[2]
Ok(result='pong', id=2)
```

[Batches](batches.md) covers the cases where a batch reply isn't a list.

## A response with both result and error

JSON-RPC 2.0 says a response has a `result` or an `error`, never both. Some
servers, mostly older JSON-RPC 1.0 style ones, send `"result": null` next to
an error. If `error` is present and not null, `parse` returns an `Error`:

```pycon
>>> parse(
...     {
...         "jsonrpc": "2.0",
...         "result": None,
...         "error": {"code": -32601, "message": "Method not found"},
...         "id": 1,
...     }
... )
Error(code=-32601, message='Method not found', data=None, id=1)
```

This only works when `error` is an object with `code` and `message`.
JSON-RPC 1.0 didn't fix the shape of an error, so a server that sends, say, a
string as the error gets `InvalidResponse` instead (see below).

!!! info "New in 4.1.0"
    Versions before 4.1.0 returned `Ok(result=None, ...)` here and dropped the
    error.

## Invalid responses

If a response is malformed, `parse` and `parse_json` raise `InvalidResponse`
with a message saying what's wrong:

```pycon
>>> from jsonrpcclient import InvalidResponse
>>> parse({"jsonrpc": "2.0", "result": "pong"})
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: missing 'id'
>>> parse({"jsonrpc": "2.0", "error": "Not found", "id": 1})
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: 'error' must be an object, got str
>>> parse_json('"pong"')
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: expected an object, got str
```

In a batch, an invalid item raises when the iterator reaches it.

!!! info "New in 4.1.0"
    `InvalidResponse` was added in 4.1.0. Earlier versions raised a plain
    `KeyError` or `TypeError`, so `InvalidResponse` subclasses both, and code
    that catches either of those still works.

[Error handling](errors.md) puts this together with transport errors and
untrusted input.
