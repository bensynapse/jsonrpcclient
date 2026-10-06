# Requests

## The request function

`request` builds a request as a dict:

```python
>>> from jsonrpcclient import request
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
```

`request_json` gives the same request as a JSON string. It's `json.dumps`
applied to the result of `request`.

```python
>>> from jsonrpcclient import request_json
>>> request_json("ping")
'{"jsonrpc": "2.0", "method": "ping", "id": 2}'
```

## Ids

Each call takes the next id:

```python
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 3}
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 4}
```

Pass `id` to choose your own:

```python
>>> request("ping", id="foo")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 'foo'}
```

Three other functions generate a different kind of id. Each one has its own
sequence.

```python
>>> from jsonrpcclient import request_hex, request_random, request_uuid
>>> request_hex("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': '1'}
>>> request_random("ping")  # 8 random letters and digits
{'jsonrpc': '2.0', 'method': 'ping', 'id': '...'}
>>> request_uuid("ping")  # a random UUID
{'jsonrpc': '2.0', 'method': 'ping', 'id': '...-...-...-...-...'}
```

`request_json_hex`, `request_json_random` and `request_json_uuid` are the JSON
string versions.

All of these are safe to call from several threads at once. Before 4.0.4,
`request_hex`, `request_random` and `request_uuid` could raise
`ValueError: generator already executing` when used from more than one thread.

## Parameters

Pass a list (or tuple) for positional parameters, or a dict for named ones.
A tuple is sent as a list.

```python
>>> request("sqrt", params=[16])
{'jsonrpc': '2.0', 'method': 'sqrt', 'params': [16], 'id': 5}
>>> request("sqrt", params=(16,))
{'jsonrpc': '2.0', 'method': 'sqrt', 'params': [16], 'id': 6}
>>> request("greet", params={"name": "Ada"})
{'jsonrpc': '2.0', 'method': 'greet', 'params': {'name': 'Ada'}, 'id': 7}
```

Empty params are left out of the request. The library doesn't check the type of
`params` at runtime, but mypy and pyright will flag anything other than a list,
tuple or dict.

## Batch requests

A batch is a list of requests:

```python
>>> import json
>>> json.dumps([request("ping") for _ in range(3)])
'[{"jsonrpc": "2.0", "method": "ping", "id": 8}, {"jsonrpc": "2.0", "method": "ping", "id": 9}, {"jsonrpc": "2.0", "method": "ping", "id": 10}]'
```

## Notifications

A notification is a request without an id. The server doesn't reply to it.

```python
>>> from jsonrpcclient import notification, notification_json
>>> notification("ping")
{'jsonrpc': '2.0', 'method': 'ping'}
>>> notification_json("log", params=["hello"])
'{"jsonrpc": "2.0", "method": "log", "params": ["hello"]}'
```
