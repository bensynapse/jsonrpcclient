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

You can also use `match`:

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

Parsing a list gives a list of responses. `match_responses` matches them to
your requests by id:

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
>>> from jsonrpcclient import match_responses, request
>>> by_id = match_responses([request("a", id=1), request("b", id=2)], responses)
>>> by_id[1]
Error(code=-32601, message='Method not found', data=None, id=1)
>>> by_id[2]
Ok(result='pong', id=2)
```

[Batches](batches.md) covers what `match_responses` checks, and the cases
where a batch reply isn't a list.

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

## Strict mode

By default `parse` is lenient. It needs an `id`, and a `result` or an `error`
object with `code` and `message`, and accepts the rest. Many servers bend
the spec, and a client usually wants their answer anyway.

Pass `strict=True` to check every JSON-RPC 2.0 rule for a response:

- `"jsonrpc"` is `"2.0"`.
- There's exactly one of `result` and `error`. A null `error` counts as one.
- `error.code` is an int and `error.message` is a string.
- `id` is a string, a number or null.

```pycon
>>> parse({"result": "pong", "id": 1})
Ok(result='pong', id=1)
>>> parse({"result": "pong", "id": 1}, strict=True)
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: missing 'jsonrpc'
>>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1}, strict=True)
Ok(result='pong', id=1)
```

`parse_json` takes `strict` too. It works the same for a batch, and the
message gives the index of the first bad item. Use it in tests of your own
server, or when a reply that bends the rules should count as a failure.

!!! info "New in 5.0"
    In 4.x, `parse_json(..., strict=...)` passed `strict` on to `json.loads`,
    where `strict=False` allows control characters in strings. For that,
    call `parse(json.loads(text, strict=False))`. 4.2.0 warns about the old
    use.

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

In a batch, `parse` checks every item before it returns. The message gives
the index of the first bad one:

```pycon
>>> parse([{"jsonrpc": "2.0", "result": "pong", "id": 1}, {"jsonrpc": "2.0"}])
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response at index 1 of the batch: missing 'id'
```

`InvalidResponse` is a `ValueError`. It was added in 4.1.0, and until 5.0 it
subclassed `KeyError` and `TypeError` instead.

[Error handling](errors.md) puts this together with transport errors and
untrusted input.
