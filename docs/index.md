<style>
.md-content__inner h1:first-of-type {
  display: none;
}
</style>

# jsonrpcclient

![jsonrpcclient](assets/logo.png)

_Create JSON-RPC requests and parse responses in Python._

jsonrpcclient builds [JSON-RPC 2.0](https://www.jsonrpc.org/specification)
requests and parses the responses. It doesn't send anything, so you can use it
with any transport: HTTP, websockets, ZeroMQ, or something else. It has no
dependencies and supports Python 3.8 and later.

```sh
pip install jsonrpcclient
```

```python
>>> from jsonrpcclient import parse, request
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
>>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
Ok(result='pong', id=1)
```

- [Requests](requests.md)
- [Responses](responses.md)
- [Examples](examples.md) with requests, aiohttp, websockets and ZeroMQ
- [FAQ](faq.md)
- [Changelog](https://github.com/bensynapse/jsonrpcclient/blob/main/CHANGELOG.md)
- [Source code and issues](https://github.com/bensynapse/jsonrpcclient)
