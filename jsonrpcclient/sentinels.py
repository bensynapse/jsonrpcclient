"""Sentinels - used to indicate no data is present.

We don't use "None" because that may be a valid piece of data.
"""

import sys


class Sentinel:
    """Use this class to create a unique object.

    Has a nicer repr than `object()`.
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"<{sys.intern(str(self.name)).rsplit('.', 1)[-1]}>"


NOID = Sentinel("NoId")
