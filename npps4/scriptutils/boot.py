import asyncio
import collections.abc
import sys

from .. import script_dummy  # type: ignore[reportUnusedImport]

from typing import Any, Callable


def start(entry: Callable[[list[str]], collections.abc.Coroutine[Any, Any, None]]):
    asyncio.run(entry(sys.argv[1:]))
