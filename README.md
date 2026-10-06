<p align="center">
  <img src="https://img.shields.io/pypi/v/jsonrpcclient.svg" alt="PyPI" />
  <img src="https://github.com/explodinglabs/jsonrpcclient/actions/workflows/code-quality.yml/badge.svg" alt="Code Quality" />
  <img src="https://coveralls.io/repos/github/explodinglabs/jsonrpcclient/badge.svg?branch=main" alt="Coverage Status" />
  <img src="https://img.shields.io/pypi/dw/jsonrpcclient" alt="Downloads" />
  <img src="https://img.shields.io/github/license/explodinglabs/jsonrpcclient" alt="License" />
</p>

<p align="center">
  <img alt="Jsonrpcclient Logo" src="https://github.com/explodinglabs/jsonrpcclient/blob/main/logo.png?raw=true" />
</p>

<p align="center">
  <i>Create JSON-RPC requests and parse responses in Python</i>
</p>

<p align="center">
  <a href="https://explodinglabs.com/jsonrpcclient/">Documentation</a> |
  <a href="https://github.com/explodinglabs/jsonrpcclient/wiki">Developer Wiki</a>
</p>

https://github.com/user-attachments/assets/080861a5-0819-43ec-a9e2-f8ea7eb694f5

## 🚀 Installation

```sh
pip install jsonrpcclient
```

## ⚒️ Usage

Generate a request:

```python
from jsonrpcclient import request, parse

req = request("ping")
# => {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
```

Parse a response:

```python
parsed = parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
# => Ok(result='pong', id=1)
```

> [!TIP]
> For strings, use `request_json` and `parse_json`.

## 📚 Documentation

👉 Full documentation is at [explodinglabs.com/jsonrpcclient/](https://explodinglabs.com/jsonrpcclient/).

👉 See the [Wiki](https://github.com/explodinglabs/jsonrpcclient/wiki) for community-editable usage examples in various frameworks, libraries, and transport protocols.

## 📖 See Also

- [jsonrpcserver](https://github.com/explodinglabs/jsonrpcserver) – Process incoming JSON-RPC requests in Python
