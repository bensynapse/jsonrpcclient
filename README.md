<p align="center">
  <a href="https://pypi.org/project/jsonrpcclient/"><img src="https://img.shields.io/pypi/v/jsonrpcclient.svg" alt="PyPI version" /></a>
  <a href="https://github.com/bensynapse/jsonrpcclient/actions/workflows/ci.yml"><img src="https://github.com/bensynapse/jsonrpcclient/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://bensynapse.github.io/jsonrpcclient/#install"><img src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="Python 3.8 to 3.14" /></a>
  <a href="https://github.com/bensynapse/jsonrpcclient/blob/main/LICENSE"><img src="https://img.shields.io/github/license/bensynapse/jsonrpcclient" alt="License: MIT" /></a>
</p>

<p align="center">
  <img alt="jsonrpcclient" src="https://raw.githubusercontent.com/bensynapse/jsonrpcclient/main/logo.png" />
</p>

<p align="center">
  <i>Create JSON-RPC 2.0 requests and parse responses in Python</i>
</p>

<p align="center">
  <a href="https://bensynapse.github.io/jsonrpcclient/">Documentation</a> |
  <a href="https://bensynapse.github.io/jsonrpcclient/reference/">API reference</a> |
  <a href="https://bensynapse.github.io/jsonrpcclient/examples/">Examples</a> |
  <a href="https://bensynapse.github.io/jsonrpcclient/changelog/">Changelog</a> |
  <a href="https://bensynapse.github.io/jsonrpcclient/migration/">Migrating from 3.x</a>
</p>

jsonrpcclient builds [JSON-RPC 2.0](https://www.jsonrpc.org/specification)
requests and parses the responses. It doesn't send anything, so it works with
any transport: HTTP, websockets, ZeroMQ, or something of your own. It has no
dependencies, ships type hints, and is safe to use from several threads. It
supports Python 3.8 to 3.14, including free-threaded 3.14t.

## Install

```sh
pip install jsonrpcclient
```

The latest release on PyPI is 4.0.3. This README and the documentation
describe 4.1.0, which isn't released yet. The
[changelog](https://bensynapse.github.io/jsonrpcclient/changelog/) lists the
differences.

## Quickstart

This sends `ping` to a JSON-RPC server at `http://localhost:8000/`, using
[requests](https://requests.readthedocs.io/) for the HTTP part:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import Error, Ok, parse, request

url = "http://localhost:8000/"
response = requests.post(url, json=request("ping"), timeout=10)
response.raise_for_status()
parsed = parse(response.json())
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    print("Error:", parsed.message)
```

```text title="Output"
pong
```

For JSON strings, use `request_json` and `parse_json`. The
[examples](https://bensynapse.github.io/jsonrpcclient/examples/) show the same
thing with urllib, httpx, aiohttp, websockets and ZeroMQ.

## Upgrading from 3.x?

The 4.x API is completely different: `request` builds a request and no longer
sends it. A 3.x call such as `request("http://example.com", "get")` still runs
but sends nothing, so read the
[migration guide](https://bensynapse.github.io/jsonrpcclient/migration/)
before upgrading.

## Links

- [Documentation](https://bensynapse.github.io/jsonrpcclient/)
- [Contributing](https://github.com/bensynapse/jsonrpcclient/blob/main/CONTRIBUTING.md)
- [Security policy](https://github.com/bensynapse/jsonrpcclient/blob/main/SECURITY.md)
- [License](https://github.com/bensynapse/jsonrpcclient/blob/main/LICENSE): MIT.
  Created by Beau Barker, maintained by bensynapse.

## See also

[jsonrpcserver](https://github.com/bensynapse/jsonrpcserver) processes
incoming JSON-RPC requests in Python. It's the server-side companion to this
library.
