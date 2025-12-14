import asyncio
import sys

from . import util

_loop = None

match sys.platform:
    case "win32":
        try:
            import winloop  # type: ignore

            util.log("Using winloop.new_event_loop")
            _loop = winloop.new_event_loop
        except ImportError:
            util.log("Using asyncio.SelectorEventLoop")
            _loop = asyncio.SelectorEventLoop
    case _:
        try:
            import uvloop  # type: ignore

            util.log("Using uvloop.new_event_loop")
            _loop = uvloop.new_event_loop
        except ImportError:
            pass


if _loop is None:
    util.log("Using default asyncio.new_event_loop")
    _loop = asyncio.new_event_loop


def new_event_loop():
    assert _loop is not None
    return _loop()
