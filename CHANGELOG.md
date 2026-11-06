# Changelog

Dates are release dates.

## 5.0.0rc1 (not released yet)

The first release candidate of 5.0. `pip install --pre jsonrpcclient` installs
it. `pip install jsonrpcclient` keeps installing 4.x until 5.0.0.
[Migration](https://github.com/bensynapse/jsonrpcclient/blob/main/docs/migration.md#from-4x-to-50)
lists every change with its replacement, and
[#252](https://github.com/bensynapse/jsonrpcclient/issues/252) tracks the
release. 4.x gets fixes on the `release/4.x` branch.

Code that builds requests with `request` or `notification`, sends them, and
reads one response with `parse` or `parse_json` keeps working. A test pins
that.

### Added

- `match_responses(batch, parse(reply))` matches a batch's responses to its
  requests by id and returns a dict in request order. It gives every request
  the error when the server rejects the whole batch. It fills requests the
  server couldn't read with their null-id errors. Anything it can't match
  raises `InvalidResponse`.
- `parse(..., strict=True)` and `parse_json(..., strict=True)` check the
  JSON-RPC 2.0 rules the default skips. These are `"jsonrpc": "2.0"`,
  exactly one of `result` and `error`, an int `error.code`, a str
  `error.message`, and an id that's a string, a number or null.
- `Request` and `Notification`, `TypedDict`s for what `request` and
  `notification` return. At run time they're still plain dicts.

### Changed

- `parse` on a list, and `parse_json` on a JSON array, return a `list`
  instead of a one-pass iterator. Every item is checked before they return,
  and a bad item's message gives its index. `next(parse(batch))` no longer
  works. Use `parse(batch)[0]`.
- `InvalidResponse` subclasses `ValueError`, like `json.JSONDecodeError`. It
  no longer subclasses `KeyError` and `TypeError`, so `except KeyError` and
  `except TypeError` don't catch it any more.
- `request`, `notification` and their variants raise `TypeError` when
  `method` isn't a str, or `params` isn't a list, tuple, dict or None. 4.x
  sent the request anyway. A rejected request uses up no id.
- `parse_json`'s `strict` keyword is the new strict mode. 4.x passed it on to
  `json.loads`. `parse(json.loads(text, strict=False))` does what it did.
- The request functions are typed as returning `Request` or `Notification`,
  not `dict[str, Any]`. mypy doesn't accept those where `dict[str, Any]` is
  expected. Annotate with `Request`, `Notification` or `Mapping[str, Any]`.

### Removed

- Python 3.8, 3.9 and 3.10, which have reached end of life. 5.0 needs Python
  3.11 or later. Older Pythons keep installing 4.x.

## 4.2.0 (2026-11-06)

Warnings about what 5.0 changes, so an upgrade doesn't surprise you. Nothing
else changes. Each is a `FutureWarning`, which Python shows by default.

- A `method` that isn't a string, or `params` that aren't a list, tuple or
  dict, warn. 4.x sends the request anyway. 5.0 raises `TypeError`. This
  covers `request`, `notification` and their variants.
- `parse_json(..., strict=...)` warns. 4.x passes `strict` on to
  `json.loads`. In 5.0 it turns on stricter checks of the response instead.
  `parse(json.loads(text, strict=False))` keeps the `json.loads` option.
- Importing jsonrpcclient on Python 3.8, 3.9 or 3.10 warns once. 5.0 needs
  Python 3.11 or later, and pip keeps installing 4.x on older Pythons.

Two more changes can't be detected at run time, so they don't warn. In 5.0
`parse` on a batch returns a list, not an iterator, so `next(parse(batch))`
stops working. And `InvalidResponse` stops subclassing `KeyError` and
`TypeError`. The
[5.0 plan](https://github.com/bensynapse/jsonrpcclient/blob/main/plans/5.0.md)
lists everything that changes.

## 4.1.0 (2026-11-06)

See [Migration](https://bensynapse.github.io/jsonrpcclient/migration/#from-40-to-41)
for what to check when upgrading.

### Changed

- `parse` and `parse_json` now raise `InvalidResponse` for an empty response
  batch. They used to return an empty iterator and silently accept the invalid
  reply.
- If a response has both `result` and `error`, and `error` is not null,
  `parse` now returns an `Error`. It used to return `Ok(result=None)` and drop
  the server's error. JSON-RPC 2.0 doesn't allow both, but JSON-RPC 1.0 style
  servers send `"result": null` with an error.
- If a response has a `result` and a non-null `error` that isn't an object
  with `code` and `message` (for example a string, `false` or `""`), `parse`
  now raises `InvalidResponse`. 4.0 returned `Ok` and ignored the error.
- `parse_json` on JSON that isn't an object or array, such as `"pong"`, used to
  say "Use parse_json on strings". It now says it expected an object.
- `parse` given bytes now raises the same "Use parse_json on strings" error as
  a str.
- `notification` sends tuple params as a list, the same as `request` does.
  The JSON output is unchanged, but the returned dict now holds a list.

### Added

- Malformed responses now raise `InvalidResponse` with a message that says what
  is wrong, for example `missing 'id'`. It subclasses `KeyError` and
  `TypeError`, which earlier versions raised, so existing `except` clauses
  still catch it.

### Documentation

- The `parse` docstring now says that a batch gives a one-pass lazy iterator,
  not a list.
- New pages: an API reference generated from the docstrings, a migration
  guide, and one page per transport. New guides cover notifications, batches,
  ids, error handling, typing and threads.

## 4.0.4 (2026-11-06)

This release fixes the links on the PyPI page. The 4.0.3 page linked to the
project's old website domain, which now belongs to someone else and serves a
gambling site. Issue #229 was closed when the link changed in this repository,
but PyPI keeps showing the old link until a new release is published
(#229, #230). The links now point to
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

## 4.0.3 (2023-02-23)

- Change build system interface to pyproject.toml.

## 4.0.2 (2021-11-27)

- Documentation.

## 4.0.1 (2021-09-30)

- Add FAQ page to documentation.

## 4.0.0 (2021-09-01)

Complete rewrite and the usage has completely changed. See
[Migration](https://bensynapse.github.io/jsonrpcclient/migration/) for how to
move from 3.x, and the
[documentation](https://bensynapse.github.io/jsonrpcclient/).

## 3.3.6 (2020-04-21)

- Add py.typed for PEP-561 compliance (#143)
- Pass `**kwargs` to AiohttpClient from client.send() call (#145)
- Change click dependency to allow version 7 (#147)

## 3.3.5 (2020-01-08)

- Fix file permissions.

## 3.3.4 (2019-09-10)

- Package with license.
- Support Python 3.8.

## 3.3.3 (2019-06-22)

- Use faster method of jsonschema validation.

## 3.3.2 (2019-06-15)

- Update jsonschema dependency to allow 3.x.

## 3.3.1 (2019-01-19)

- Fix sending lists or dictionaries as positional arguments. (#118)

## 3.3.0 (2019-01-10)

- Add timeout parameter in AiohttpClient

## 3.2.2 (2018-10-20)

- Fix basic_logging option which was adding too many log handlers.

## 3.2.1 (2018-10-06)

- Pass response_expected to send_message. Lets clients know if a response is
  expected from the request. Certain socket clients can use this to not listen
  for a response.

## 3.2.0 (2018-10-06)

- Returned the convenience functions, request, notify and send.
- Clean up response.py.

## 3.1.0 (2018-10-06)

- Add a socket client.
- Fixed missing import in async_client.py.

## 3.0.2 (2018-09-30)

- response.data will _never_ be None. For single requests it's _always_ a
  JSONRPCResponse, for batch requests it's _always_ a list.
- Raise ReceivedErrorResponse exception on receving a JSON-RPC error
  response. This won't affect too many who are using HTTP, since an
  exception is already raised when a non-2xx error response is returned.
- Removed ParseResponseError, the json.JSONDecodeError is clear enough.

## 3.0.1 (2018-09-16)

- Optionally pass an SSLContext to AiohttpClient. This client now requires
  aiohttp 3+.

## 3.0.0 (2018-08-18)

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

## 2.6.0 (2018-06-13)

- Add command-line interface, see `jsonrpc --help` (#62)
- Fix configuring requests lib (#65)

## 2.5.2 (2017-11-29)

- Ignore empty error bodies

## 2.5.1 (2017-09-04)

- Fix non-string exception 'data' value

## 2.5.0 (2017-08-08)

- Add convenience functions 'request' and 'notify' (#54)

## 2.4.3 (2017-08-08)

- Fix custom headers in Tornado Client (#52)

## 2.4.2 (2016-10-12)

- Allow passing a list of strings to send()

## 2.4.1 (2016-10-06)

- Fix response log prefix

## 2.4.0 (2016-10-05)

- Add asynchronous ZeroMQ client.

## 2.3.0 (2016-09-28)

- Support websockets and aiohttp

## 2.2.4 (2016-09-19)

- Internal refactoring, to make it easier to add clients.

## 2.2.3 (2016-09-13)

- Rename "server" modules and classes to "client". The old names are
  deprecated.

## 2.2.2 (2016-09-12)

- Don't disable log propagate

## 2.2.1 (2016-09-12)

- Bugfix logging configuration

## 2.2.0 (2016-09-12)

- Support Tornado adapter
- Improve logging configuration
