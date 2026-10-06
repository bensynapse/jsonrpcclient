---
description: API reference for jsonrpcclient, generated from the source code. Every public function and class, with signatures, parameters, return values and exceptions.
---

# API reference

This page is generated from the docstrings in the source code, so it matches
the code on the main branch.

Everything in the first four sections can be imported from the package
itself, for example `from jsonrpcclient import request, parse`. The other
public names are in `jsonrpcclient.id_generators`, `jsonrpcclient.utils`,
`jsonrpcclient.responses` (the `Response` type) and `jsonrpcclient.requests`
(the `Params` type). Anything not listed here is internal and can change in
any release.

In the signatures, `id=NOID` means "no id given": the request takes the next
id from its sequence.

## Requests

::: jsonrpcclient.request

::: jsonrpcclient.request_hex

::: jsonrpcclient.request_random

::: jsonrpcclient.request_uuid

::: jsonrpcclient.request_json

::: jsonrpcclient.request_json_hex

::: jsonrpcclient.request_json_random

::: jsonrpcclient.request_json_uuid

## Notifications

::: jsonrpcclient.notification

::: jsonrpcclient.notification_json

## Responses

::: jsonrpcclient.parse

::: jsonrpcclient.parse_json

::: jsonrpcclient.Ok

::: jsonrpcclient.Error

## Exceptions

::: jsonrpcclient.InvalidResponse

## Id generators

::: jsonrpcclient.id_generators
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - decimal
        - hexadecimal
        - random
        - uuid

## Types

::: jsonrpcclient.responses.Response

::: jsonrpcclient.requests.Params

## Utilities

::: jsonrpcclient.utils.compose

## Version

::: jsonrpcclient.__version__

## Older names

::: jsonrpcclient.requests.request_natural
