# jsonrpcclient Change Log

## 4.1.0

- If a response has both `result` and `error`, and `error` is not null,
  `parse` now returns an `Error`. It used to return `Ok(result=None)` and drop
  the server's error. JSON-RPC 2.0 doesn't allow both, but JSON-RPC 1.0 style
  servers send `"result": null` with an error.
- Malformed responses now raise `InvalidResponse` with a message that says what
  is wrong, for example `missing 'id'`. It subclasses `KeyError` and
  `TypeError`, which earlier versions raised, so existing `except` clauses
  still catch it.
- `parse_json` on JSON that isn't an object or array, such as `"pong"`, used to
  say "Use parse_json on strings". It now says it expected an object.
- `parse` given bytes now raises the same "Use parse_json on strings" error as
  a str.
- `notification` sends tuple params as a list, the same as `request` does.
  The JSON output is unchanged, but the returned dict now holds a list.
- The `parse` docstring now says that a batch gives a one-pass lazy iterator,
  not a list.

## 4.0.4

This release fixes the links on the PyPI page. The 4.0.3 page linked to the
project's old website domain, which now belongs to someone else and serves a
gambling site. Issue #229 was closed when the link changed in this repository,
but PyPI kept showing the old link until a new release. With this release it is
really fixed (#229, #230). The links now point to
https://bensynapse.github.io/jsonrpcclient/ and
https://github.com/bensynapse/jsonrpcclient.

- `request_hex`, `request_random` and `request_uuid` are now safe to call from
  several threads at once. Before, they could raise `ValueError: generator
  already executing`, and free-threaded Python could crash. The iterators from
  `jsonrpcclient.id_generators` are thread-safe too.
- Type hints: `params` accepts a list. The `*_json` functions return `str`, and
  `parse` has overloads, so a type checker knows a dict gives one response and
  a list gives an iterator. `parse_json` used to be typed as `Any`. Code that
  uses its result without an `isinstance` check now needs one to pass mypy.
- Added `__version__`.
- Needs Python 3.8 or later (was 3.6). Tested on 3.8 to 3.14 and on
  free-threaded 3.14. Older Pythons will keep installing 4.0.3.
- The documentation moved to https://bensynapse.github.io/jsonrpcclient/.
- Releases now include both an sdist and a wheel. They are published from
  GitHub Actions with build attestations.

## 4.0.3 (23 Feb, 2023)

- Change build system interface to pyproject.toml.

## 4.0.2 (27 Nov, 2021)

- Documentation.

## 4.0.1 (30 Sep, 2021)

- Add FAQ page to documentation.

## 4.0.0 (1 Sep, 2021)

Complete rewrite and the usage has completely changed. See the
[documentation](https://bensynapse.github.io/jsonrpcclient/).

## 3.3.6 (21 Apr, 2020)

- Add py.typed for PEP-561 compliance (#143)
- Pass `**kwargs` to AiohttpClient from client.send() call (#145)
- Change click dependency to allow version 7 (#147)

## 3.3.5 (8 Jan, 2020)

- Fix file permissions.

## 3.3.4 (10 Sep, 2019)

- Package with license.
- Support Python 3.8.

## 3.3.3 (22 Jun, 2019)

- Use faster method of jsonschema validation.

## 3.3.2 (15 Jun, 2019)

- Update jsonschema dependency to allow 3.x.

## 3.3.1 (19 Jan, 2019)

- Fix sending lists or dictionaries as positional arguments. (#118)

## 3.3.0 (10 Jan, 2019)

- Add timeout parameter in AiohttpClient

## 3.2.2 (20 Oct, 2018)

- Fix basic_logging option which was adding too many log handlers.

## 3.2.1 (6 Oct, 2018)

- Pass response_expected to send_message. Lets clients know if a response is
  expected from the request. Certain socket clients can use this to not listen
  for a response.

## 3.2.0 (6 Oct, 2018)

- Returned the convenience functions, request, notify and send.
- Clean up response.py.

## 3.1.0 (6 Oct, 2018)

- Add a socket client.
- Fixed missing import in async_client.py.

## 3.0.2 (30 Sep, 2018)

- response.data will _never_ be None. For single requests it's _always_ a
  JSONRPCResponse, for batch requests it's _always_ a list.
- Raise ReceivedErrorResponse exception on receving a JSON-RPC error
  response. This won't affect too many who are using HTTP, since an
  exception is already raised when a non-2xx error response is returned.
- Removed ParseResponseError, the json.JSONDecodeError is clear enough.

## 3.0.1 (16 Sep, 2018)

- Optionally pass an SSLContext to AiohttpClient. This client now requires
  aiohttp 3+.

## 3.0.0 (18 Aug, 2018)

_The 3.x releases will support Python 3.5+ only._

- Remove the config module. Add new params to configure the client. (#46)
- Remove the `*_server.py` files, which were deprecated. (#79)
- Rename aiohttpClient to AiohttpClient.
- Include http status code and reason in aiohttp log entries.
- Remove headers from http_client's log entries, they weren't used.
- Update the Tornado client to subclass AsyncClient. (#44)
- Remove HTTPClient.last_request and last_response, they weren't used. (#27)
- Remove ReceivedErrorResponse.
- HTTP clients raise an exception on non-2xx status code response. (#67)
- Remove zmq_client module, use zeromq_client instead. (#84)
- Move all client modules into a `clients` subpackage. Import from
  jsonrpcclient.clients. (#83)
- Change code to python 3 style: remove future and past.builtins. Change super
  calls to just super(). Change basestring to str. (#71)
- Remove jsonrpcclient.Request and Notification. Import
  jsonrpcclient.request.Request and Notification instead.
- Remove jsonrpcclient.request. Import jsonrpcclient.clients.http_client.request instead.
- Remove the need for requests library to be installed, if not using it. (#85)
- Add type hints (#92)
- Log to the debug log level (not info).
- Add support for configuration files.
- Remove the convenience functions (request and notify).
- Remove zeromq-async client.
- Configure logging pythonically.

## 2.6.0 (Jun 13, 2018)
- Add command-line interface, see `jsonrpc --help` (#62)
- Fix configuring requests lib (#65)

## 2.5.2 (Nov 29, 2017)
- Ignore empty error bodies

## 2.5.1 (Sep 4, 2017)
- Fix non-string exception 'data' value

## 2.5.0 (Aug 8, 2017)
- Add convenience functions 'request' and 'notify' (#54)

## 2.4.3 (Aug 8, 2017)
- Fix custom headers in Tornado Client (#52)

## 2.4.2 (Oct 12, 2016)
- Allow passing a list of strings to send()

## 2.4.1 (Oct 6, 2016)
- Fix response log prefix

## 2.4.0 (Oct 5, 2016)
- Add asynchronous ZeroMQ client.

## 2.3.0 (Sep 28, 2016)
- Support websockets and aiohttp

## 2.2.4 (Sep 19, 2016)
- Internal refactoring, to make it easier to add clients.

## 2.2.3 (Sep 13, 2016)
- Rename "server" modules and classes to "client". The old names are
  deprecated.

## 2.2.2 (Sep 12, 2016)
- Don't disable log propagate

## 2.2.1 (Sep 12, 2016)
- Bugfix logging configuration

## 2.2.0 (Sep 12, 2016)
- Support Tornado adapter
- Improve logging configuration
