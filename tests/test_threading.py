"""Ids must stay correct when many threads share the module-level generators."""

import sys
import threading
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from jsonrpcclient import (
    id_generators,
    request,
    request_hex,
    request_random,
    request_uuid,
)

THREADS = 8
CALLS = 2000


@pytest.fixture(autouse=True)
def frequent_thread_switches() -> Iterator[None]:
    """On GIL builds, switch threads as often as possible to provoke races."""
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    yield
    sys.setswitchinterval(old)


def hammer(func: Callable[[], Any]) -> tuple[list[Any], list[str]]:
    """Call func from several threads at once and collect results and errors."""
    ids: list[Any] = []
    errors: list[str] = []
    lock = threading.Lock()
    barrier = threading.Barrier(THREADS)

    def worker() -> None:
        local_ids: list[Any] = []
        local_errors: list[str] = []
        barrier.wait()
        for _ in range(CALLS):
            try:
                local_ids.append(func())
            except Exception as exc:
                local_errors.append(repr(exc))
        with lock:
            ids.extend(local_ids)
            errors.extend(local_errors)

    threads = [threading.Thread(target=worker) for _ in range(THREADS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return ids, errors


@pytest.mark.parametrize(
    "make_request,unique",
    [
        (request, True),
        (request_hex, True),
        (request_uuid, True),
        # Random ids can collide, so only check that nothing raised.
        (request_random, False),
    ],
)
def test_shared_request_functions(
    make_request: Callable[[str], Any], unique: bool
) -> None:
    ids, errors = hammer(lambda: make_request("ping")["id"])
    assert errors == []
    assert len(ids) == THREADS * CALLS
    if unique:
        assert len(set(ids)) == THREADS * CALLS


@pytest.mark.parametrize(
    "generator,unique",
    [
        (id_generators.decimal, True),
        (id_generators.hexadecimal, True),
        (id_generators.uuid, True),
        (id_generators.random, False),
    ],
)
def test_shared_generator(generator: Callable[[], Iterator[Any]], unique: bool) -> None:
    ids_iter = generator()
    ids, errors = hammer(lambda: next(ids_iter))
    assert errors == []
    assert len(ids) == THREADS * CALLS
    if unique:
        assert len(set(ids)) == THREADS * CALLS
