"""Generators which yield an id to include in a JSON-RPC request.

Every function here returns an iterator that is safe to share between threads.
"""

import itertools
import threading
from random import choice
from string import ascii_lowercase, digits
from typing import Iterator, TypeVar
from uuid import uuid4

T = TypeVar("T")


class _ThreadSafeIterator(Iterator[T]):
    """Wrap an iterator so that only one thread at a time can advance it.

    A plain generator raises "ValueError: generator already executing" when two
    threads call next() on it at once, and free-threaded CPython can crash.
    """

    def __init__(self, iterator: Iterator[T]) -> None:
        self._iterator = iterator
        self._lock = threading.Lock()

    def __iter__(self) -> "_ThreadSafeIterator[T]":
        return self

    def __next__(self) -> T:
        with self._lock:
            return next(self._iterator)


def decimal(start: int = 1) -> Iterator[int]:
    """
    Increments from `start`.

    e.g. 1, 2, 3, .. 9, 10, 11, etc.

    Args:
        start: The first value to start with.
    """
    return _ThreadSafeIterator(itertools.count(start))


def _hexadecimal(start: int) -> Iterator[str]:
    while True:
        yield f"{start:x}"
        start += 1


def hexadecimal(start: int = 1) -> Iterator[str]:
    """
    Incremental hexadecimal numbers.

    e.g. 1, 2, 3, .. 9, a, b, etc.

    Args:
        start: The first value to start with.
    """
    return _ThreadSafeIterator(_hexadecimal(start))


def _random(length: int, chars: str) -> Iterator[str]:
    while True:
        yield "".join([choice(chars) for _ in range(length)])


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
    return _ThreadSafeIterator(_random(length, chars))


def _uuid() -> Iterator[str]:
    while True:
        yield str(uuid4())


def uuid() -> Iterator[str]:
    """
    Unique uuid ids.

    Example:
        '9bfe2c93-717e-4a45-b91b-55422c5af4ff'
    """
    return _ThreadSafeIterator(_uuid())
