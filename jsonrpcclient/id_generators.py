"""Iterators of request ids.

Each function returns a new, independent iterator. Take ids from it with
`next()` and pass them to `request(..., id=...)`. Every iterator is safe to
share between threads.

The `request`, `request_hex`, `request_random` and `request_uuid` functions
each use their own module-level iterator from here, shared by the whole
process.
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
    """Count up in integers: 1, 2, 3, and so on.

    Args:
        start: The first id.

    Returns:
        An endless, thread-safe iterator of ints.

    Examples:
        >>> ids = decimal(100)
        >>> next(ids), next(ids)
        (100, 101)
    """
    return _ThreadSafeIterator(itertools.count(start))


def _hexadecimal(start: int) -> Iterator[str]:
    while True:
        yield f"{start:x}"
        start += 1


def hexadecimal(start: int = 1) -> Iterator[str]:
    """Count up in lowercase hexadecimal strings: "1", ... "9", "a", "b".

    Args:
        start: The first id, as an int. `hexadecimal(10)` starts at "a".

    Returns:
        An endless, thread-safe iterator of strs.

    Examples:
        >>> ids = hexadecimal(9)
        >>> next(ids), next(ids)
        ('9', 'a')
    """
    return _ThreadSafeIterator(_hexadecimal(start))


def _random(length: int, chars: str) -> Iterator[str]:
    while True:
        yield "".join([choice(chars) for _ in range(length)])


def random(length: int = 8, chars: str = digits + ascii_lowercase) -> Iterator[str]:
    """Random strings, such as "fubui5e6".

    The ids are not guaranteed to be unique, and Python's `random.choice`
    is not a secure source of randomness. With the defaults there are 36**8
    (about 2.8 million million) possible ids, so a clash between two ids in
    flight at the same time is very unlikely. Use `uuid` if a clash would
    matter.

    Args:
        length: The number of characters in each id.
        chars: The characters to choose from. The default is the digits and
            the lowercase letters a to z.

    Returns:
        An endless, thread-safe iterator of strs.

    Examples:
        >>> len(next(random(length=12)))
        12
    """
    return _ThreadSafeIterator(_random(length, chars))


def _uuid() -> Iterator[str]:
    while True:
        yield str(uuid4())


def uuid() -> Iterator[str]:
    """Random UUIDs (version 4) as strings.

    For example "9bfe2c93-717e-4a45-b91b-55422c5af4ff". The safe choice when
    several processes or machines send requests to the same server.

    Returns:
        An endless, thread-safe iterator of strs.
    """
    return _ThreadSafeIterator(_uuid())
