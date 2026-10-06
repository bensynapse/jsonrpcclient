"""Utility functions"""

from functools import reduce
from typing import Any, Callable


def compose(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    """Compose two or more functions producing a single composite function."""
    return reduce(lambda f, g: lambda *a, **kw: f(g(*a, **kw)), funcs)
