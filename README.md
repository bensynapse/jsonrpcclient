<p align="center">
  <a href="https://pypi.org/project/jsonrpcclient/"><img src="https://img.shields.io/pypi/v/jsonrpcclient.svg" alt="PyPI" /></a>
  <a href="https://github.com/bensynapse/jsonrpcclient/actions/workflows/ci.yml"><img src="https://github.com/bensynapse/jsonrpcclient/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <img src="https://img.shields.io/pypi/pyversions/jsonrpcclient" alt="Python versions" />
  <img src="https://img.shields.io/pypi/dw/jsonrpcclient" alt="Downloads" />
  <img src="https://img.shields.io/github/license/bensynapse/jsonrpcclient" alt="License" />
</p>

<p align="center">
  <img alt="Jsonrpcclient Logo" src="https://raw.githubusercontent.com/bensynapse/jsonrpcclient/main/logo.png" />
</p>

<p align="center">
  <i>Create JSON-RPC requests and parse responses in Python</i>
</p>

<p align="center">
  <a href="https://bensynapse.github.io/jsonrpcclient/">Documentation</a> |
  <a href="https://bensynapse.github.io/jsonrpcclient/examples/">Examples</a> |
  <a href="https://github.com/bensynapse/jsonrpcclient/blob/main/CHANGELOG.md">Changelog</a>
</p>

https://github.com/user-attachments/assets/080861a5-0819-43ec-a9e2-f8ea7eb694f5

## Installation

```sh
pip install jsonrpcclient
```

It has no dependencies and supports Python 3.8 and later, including
free-threaded builds.

## Usage

Generate a request:

```python
>>> from jsonrpcclient import parse, request
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
```

Parse a response:

```python
>>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
Ok(result='pong', id=1)
```

For strings, use `request_json` and `parse_json`.

jsonrpcclient doesn't send anything itself. The
[examples](https://bensynapse.github.io/jsonrpcclient/examples/) show it with
requests, aiohttp, websockets and ZeroMQ.

## Documentation

Full documentation is at
[bensynapse.github.io/jsonrpcclient](https://bensynapse.github.io/jsonrpcclient/).

## See also

- [jsonrpcserver](https://github.com/bensynapse/jsonrpcserver): process incoming JSON-RPC requests in Python
