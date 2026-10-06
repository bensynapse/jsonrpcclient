# Responses

## Parsing a response

`parse` turns a deserialized response into an `Ok` or an `Error`. Both are
named tuples.

```python
>>> from jsonrpcclient import parse
>>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
Ok(result='pong', id=1)
>>> parse({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1})
Error(code=-32601, message='Method not found', data=None, id=1)
```

If you have a string or bytes, use `parse_json`. It calls `json.loads` first.

```python
>>> from jsonrpcclient import parse_json
>>> parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}')
Ok(result='pong', id=1)
```

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

On Python 3.10 and later you can use `match`:

<!-- min-python: 3.10 -->
```python
import logging

from jsonrpcclient import Error, Ok, parse

match parse({"jsonrpc": "2.0", "result": "pong", "id": 1}):
    case Ok(result, id):
        print(result)
    case Error(code, message, data, id):
        logging.error(message)
```

## Batch responses

Parsing a list gives an iterator of responses. It is lazy: each item is parsed
when you reach it, and you can only go through it once. Call `list()` on it if
you need the responses more than once.

The server can send batch responses in any order, so match them to your
requests by id:

```python
>>> responses = parse([
...     {"jsonrpc": "2.0", "result": "pong", "id": 2},
...     {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1},
... ])
>>> by_id = {response.id: response for response in responses}
>>> by_id[1]
Error(code=-32601, message='Method not found', data=None, id=1)
>>> by_id[2]
Ok(result='pong', id=2)
```

## A response with both result and error

JSON-RPC 2.0 says a response has a `result` or an `error`, never both. Some
servers, mostly older JSON-RPC 1.0 ones, send `"result": null` next to an
error. If `error` is present and not null, `parse` returns an `Error`:

```python
>>> parse({"jsonrpc": "2.0", "result": None, "error": {"code": -32601, "message": "Method not found"}, "id": 1})
Error(code=-32601, message='Method not found', data=None, id=1)
```

Versions before 4.1.0 returned `Ok(result=None, ...)` here.

## Invalid responses

If a response is malformed, `parse` and `parse_json` raise `InvalidResponse`
with a message saying what's wrong:

```python
>>> from jsonrpcclient import InvalidResponse
>>> parse({"jsonrpc": "2.0", "result": "pong"})
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: missing 'id'
>>> parse_json('"pong"')
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: expected an object, got str
```

`InvalidResponse` was added in 4.1.0. Earlier versions raised a plain
`KeyError` or `TypeError`, so `InvalidResponse` subclasses both. Code that
catches either of those still works.

In a batch, an invalid item raises when the iterator reaches it.

## Responses from servers you don't trust

Catch `InvalidResponse` for malformed responses. `parse_json` uses the
standard `json` module, so invalid JSON raises `json.JSONDecodeError`. Very
deeply nested input raises `RecursionError`, and an integer with more than
4,300 digits raises `ValueError` on recent Pythons. The library sets no size
limit, so limit the size of responses in your transport if the server isn't
trusted.
