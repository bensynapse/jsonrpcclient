"""Helpers for building your own request and parse functions."""

from functools import reduce
from typing import Any, Callable


def compose(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    """Combine functions into one that applies them from right to left.

    `compose(f, g)(x)` is `f(g(x))`. The last function gets all the arguments;
    each one before it gets the previous one's return value. The FAQ uses it to
    build `request_json` and `parse_json` with another JSON library.

    Args:
        *funcs: Two or more functions. With one function, that function is
            returned unchanged.

    Returns:
        The composed function.

    Raises:
        TypeError: If no functions are given.

    Examples:
        >>> import json
        >>> from jsonrpcclient import request
        >>> to_json = compose(json.dumps, request)
        >>> to_json("ping", id=1)
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
    """
    return reduce(lambda f, g: lambda *a, **kw: f(g(*a, **kw)), funcs)
