# Examples

jsonrpcclient only builds requests and parses responses, so you pair it with a
transport library. These examples talk to a JSON-RPC server on
`localhost:5000` that answers `ping` with `pong`. CI runs every one of them
against a test server.

## Requests

Using [Requests](https://requests.readthedocs.io/):

```python
--8<-- "docs/examples/requests_client.py"
```

A batch of requests:

```python
--8<-- "docs/examples/requests_batch.py"
```

## aiohttp

```python
--8<-- "docs/examples/aiohttp_client.py"
```

## websockets

Uses the `websockets.asyncio` client from websockets 13 and later.

```python
--8<-- "docs/examples/websockets_client.py"
```

## ZeroMQ

Using [pyzmq](https://pyzmq.readthedocs.io/):

```python
--8<-- "docs/examples/zeromq_client.py"
```
