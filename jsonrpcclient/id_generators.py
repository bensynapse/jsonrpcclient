"""Generators which yield an id to include in a JSON-RPC request."""

import itertools
from random import choice
from string import ascii_lowercase, digits
from typing import Iterator
from uuid import uuid4


def decimal(start: int = 1) -> Iterator[int]:
    """
    Increments from `start`.

    e.g. 1, 2, 3, .. 9, 10, 11, etc.

    Args:
        start: The first value to start with.
    """
    return itertools.count(start)


def hexadecimal(start: int = 1) -> Iterator[str]:
    """
    Incremental hexadecimal numbers.

    e.g. 1, 2, 3, .. 9, a, b, etc.

    Args:
        start: The first value to start with.
    """
    while True:
        yield f"{start:x}"
        start += 1


def random(length: int = 8, chars: str = digits + ascii_lowercase) -> Iterator[str]:
    """
    A random string.

    Not unique, but has around 1 in a million chance of collision (with the default 8
    character length).

    Example:
        'fubui5e6'

    Args:
        length: Length of the random string.
        chars: The characters to randomly choose from.
    """
    while True:
        yield "".join([choice(chars) for _ in range(length)])


def uuid() -> Iterator[str]:
    """
    Unique uuid ids.

    Example:
        '9bfe2c93-717e-4a45-b91b-55422c5af4ff'
    """
    while True:
        yield str(uuid4())
