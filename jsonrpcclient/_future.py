"""FutureWarnings about what 5.0 changes. New in 4.2.0, gone in 5.0.

See plans/5.0.md on the main branch.
"""

import sys
import warnings
from typing import Any, Tuple

_SENDS_ANYWAY = "4.x sends it anyway, but 5.0 raises TypeError."


def warn(message: str) -> None:
    """Give a FutureWarning that points at the first caller outside jsonrpcclient."""
    frame = sys._getframe(1)  # pyright: ignore[reportPrivateUsage]
    level = 2
    while frame.f_back is not None and frame.f_globals.get("__name__", "").startswith(
        "jsonrpcclient."
    ):
        frame = frame.f_back
        level += 1
    warnings.warn(message, FutureWarning, stacklevel=level)


def check_request(method: Any, params: Any) -> None:
    """Warn about a method or params that 5.0 rejects with TypeError."""
    if not isinstance(method, str):
        warn(f"method must be a str, not {type(method).__name__}. {_SENDS_ANYWAY}")
    if params is not None and not isinstance(params, (list, tuple, dict)):
        warn(
            "params must be a list, tuple or dict, not "
            f"{type(params).__name__}. {_SENDS_ANYWAY}"
        )


def check_python(version: Tuple[Any, ...]) -> None:
    """Warn once, at import, on a Python that 5.0 doesn't support."""
    if version < (3, 11):
        warnings.warn(
            "jsonrpcclient 5.0 needs Python 3.11 or later. On this Python, pip "
            "keeps installing 4.x.",
            FutureWarning,
            stacklevel=3,
        )
