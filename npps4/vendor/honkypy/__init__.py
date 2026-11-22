# Honky Pie, a HonokaMiku/libhonoka implementation in Python
#
# Copyright (c) 2023 Dark Energy Processor
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
HonkyPy, a HonokaMiku/libhonoka implementation in Python.

This module provides "a certain idol rhythm game" file encryption and decryption
routines written in pure Python.
"""

import collections.abc
import io

from .dctx import DecrypterContext, Version1Context, Version2Context, setup_v3
from .error import *
from .key_tables import *

from typing import Callable, Literal, IO, cast

_SupportsDctxType = Callable[[bytes, bytes, list[int] | None, bytes | None], DecrypterContext]
_ValidGametypes = Literal["JP", "WW", "TW", "CN"]


NAME_PREFIX_JP = b"Hello"
NAME_PREFIX_WW = b"BFd3EnkcKa"
NAME_PREFIX_TW = b"M2o2B7i3M6o6N88"
NAME_PREFIX_CN = b"iLbs0LpvJrXm3zjdhAr4"
NAME_PREFIX_EN = NAME_PREFIX_WW


_COMBINATION: list[tuple[_ValidGametypes, bytes, list[int]]] = [
    ("JP", NAME_PREFIX_JP, KEY_TABLES_JP),
    ("WW", NAME_PREFIX_WW, KEY_TABLES_WW),
    ("TW", NAME_PREFIX_TW, KEY_TABLES_TW),
    ("CN", NAME_PREFIX_CN, KEY_TABLES_CN),
]

_GAME_VERSIONS: list[_SupportsDctxType] = [Version1Context, Version2Context, setup_v3, setup_v3]

_GAME_VERSIONS_PROBE: list[_SupportsDctxType] = [Version2Context, setup_v3, setup_v3]


def decrypt_setup_probe(
    filename: str | bytes, header: bytes, *, version: int = 0
) -> tuple[DecrypterContext, _ValidGametypes]:
    """Initialize decrypter using the best suitable options using the file header.

    Args:
        filename (str | bytes): Name of the file. The basename is used to derive the key.
        header (bytes): First 16-byte of the file data.
        version (int, optional): Specify decryption version, or 0 to automatically determine. Defaults to 0.

    Raises:
        NoSuitableModeError: When there's no suitable decryption method.

    Returns:
        tuple[DecrypterContext, _ValidGametypes]: Newly decrypter context and the game type string.
    """
    # Try all combination
    for gametype, prefix, key_tables in _COMBINATION:
        try:
            dctx = decrypt_setup(prefix, filename, header, key_tables, version)
            return dctx, gametype
        except ValueError:
            pass
    raise NoSuitableModeError()


def decrypt_setup(
    prefix: bytes,
    filename: str | bytes,
    header: bytes,
    key_tables: list[int],
    version: int = 0,
) -> DecrypterContext:
    """Initialize decrypter with specified parameters.

    Args:
        prefix (bytes): Game file prefix. Can be one of `NAME_PREFIX_*`
        filename (str | bytes): Name of the file. The basename is used to derive the key.
        header (bytes): First 16-byte of the file data.
        key_tables (list[int]): Key tables with 64 elements used for V3 decryption. Can be one of `KEY_TABLES_*`.
        version (int, optional): Specify decryption version, or 0 to automatically determine. Defaults to 0.

    Raises:
        InsufficientHeaderDataError: When header data passed is less than 16 byte.
        NoSuitableModeError: When there's no suitable decryption method.
        VersionOutOfRange: When the version specified is out-of-range.

    Returns:
        DecrypterContext: Newly decrypter context.
    """
    if isinstance(filename, str):
        filename = filename.encode("UTF-8")
    if len(header) < 16:
        raise InsufficientHeaderDataError()
    if version == 0:
        for context_class in _GAME_VERSIONS_PROBE:
            try:
                dctx = context_class(prefix, filename, key_tables, header)
                return dctx
            except ValueError:
                pass
        raise NoSuitableModeError()
    elif version < 0 or version > len(_GAME_VERSIONS):
        raise VersionOutOfRange()
    else:
        context_class = _GAME_VERSIONS[version - 1]
        dctx = cast(DecrypterContext, context_class(prefix, filename, key_tables, header))
        return dctx


def encrypt_setup(
    prefix: bytes,
    filename: str | bytes,
    version: int,
    *,
    v3_flip_key: bool = False,
    v3_key_tables: list[int] | None = None,
    v4_lcg_index: int = 0,
) -> DecrypterContext:
    """Initialize decrypter context for encrypting.

    Args:
        prefix (bytes): Game file prefix. Can be one of `NAME_PREFIX_*`
        filename (str | bytes): Name of the file. The basename is used to derive the key.
        version (int): Specify decryption version.
        v3_flip_key (bool, optional): Whetever to flip the initial key in V3. Defaults to False.
        v3_key_tables (list[int] | None, optional): Key tables with 64 elements used for V3 decryption. Defaults to None.
        v4_lcg_index (int, optional): Linear Congruential Generator key index for V4. Defaults to 0.

    Raises:
        VersionOutOfRange: When version is out-of-range.
        KeyTablesMissingError: When version is 3 and `v3_key_tables` is `None`.

    Returns:
        DecrypterContext: Newly decrypter context.
    """
    if isinstance(filename, str):
        filename = filename.encode("UTF-8")
    if version < 0:
        raise VersionOutOfRange()
    if version == 1:
        return Version1Context(prefix, filename, [])
    elif version == 2:
        return Version2Context(prefix, filename, [])
    else:
        if v3_key_tables is None:
            if version == 3:
                raise KeyTablesMissingError()
            v3_key_tables = []
        return setup_v3(prefix, filename, v3_key_tables, version=version, flip_v3=v3_flip_key, lcg_key_v4=v4_lcg_index)


def encrypt_setup_by_gametype(
    gametype: str,
    filename: str | bytes,
    version: int,
    *,
    v3_flip_key: bool = False,
    v4_lcg_index: int = 0,
) -> DecrypterContext:
    """Initialize decrypter context for encrypting using gametype-specific data.

    Args:
        gametype (str): One of "JP", "WW", "TW", or "CN".
        filename (str | bytes): Name of the file. The basename is used to derive the key.
        version (int): Specify decryption version.
        v3_flip_key (bool, optional): Whetever to flip the initial key in V3. Defaults to False.
        v4_lcg_index (int, optional): Linear Congruential Generator key index for V4. Defaults to 0.

    Raises:
        InvalidGameType: When the game type is invalid.

    Returns:
        DecrypterContext: Newly decrypter context.
    """
    gametype_cf = gametype.casefold()

    for gt, prefix, key_tables in _COMBINATION:
        if gametype_cf == gt.casefold():
            return encrypt_setup(
                prefix, filename, version, v3_flip_key=v3_flip_key, v3_key_tables=key_tables, v4_lcg_index=v4_lcg_index
            )
    raise InvalidGameType(gametype)


class StreamIOWrapper(IO[bytes]):
    """Wrap IO bytes through DecrypterContext."""

    def __init__(self, stream: IO[bytes], dctx: DecrypterContext, write_header: bool = False):
        """
        Args:
            stream (IO[bytes]): Bytes IO stream.
            dctx (DecrypterContext): Decrypter context.
            write_header (bool, optional): When encrypting, set this to true to write header automatically just when opening for writing. Defaults to False.
        """
        self._stream = stream
        self._dctx = dctx

        if write_header:
            stream.write(dctx.emit_header())
            dctx.goto_offset(0)

    @property
    def mode(self) -> str:
        return self._stream.mode

    @property
    def name(self) -> str:
        return self._stream.name

    def close(self):
        self._stream.close()

    @property
    def closed(self) -> bool:
        return self._stream.closed

    def fileno(self) -> int:
        return self._stream.fileno()

    def flush(self):
        self._stream.flush()

    def isatty(self):
        return self._stream.isatty()

    def read(self, n: int = -1) -> bytes:
        data = self._stream.read(n)
        return self._dctx.decrypt_block(data)

    def readable(self) -> bool:
        return self._stream.readable()

    def readline(self, limit: int = -1) -> bytes:
        data = self._stream.readline(limit)
        return self._dctx.decrypt_block(data)

    def readlines(self, hint: int = -1) -> list[bytes]:
        data = self._stream.readlines(hint)
        return [self._dctx.decrypt_block(d) for d in data]

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == io.SEEK_SET:
            offset = offset + self._dctx.HEADER_SIZE
        result = self._stream.seek(offset, whence) - self._dctx.HEADER_SIZE
        self._dctx.goto_offset(result)
        return result

    def seekable(self) -> bool:
        return self._stream.seekable()

    def tell(self) -> int:
        return self._stream.tell() - self._dctx.HEADER_SIZE

    def truncate(self, size: int | None = None) -> int:
        raise NotImplementedError("Should it truncate to exact size or size + header?")
        return 0

    def writable(self) -> bool:
        return self._stream.writable()

    def write(self, s: collections.abc.Buffer) -> int:
        return self._stream.write(self._dctx.decrypt_block(bytes(s)))

    def writelines(self, lines: collections.abc.Iterable[collections.abc.Buffer]) -> None:
        self._stream.writelines(self._dctx.decrypt_block(bytes(s)) for s in lines)

    def __enter__(self):
        self._stream.__enter__()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self._stream.__exit__(type, value, traceback)

    def __iter__(self) -> collections.abc.Iterator[bytes]:
        return self._stream.__iter__()

    def __next__(self) -> bytes:
        return self._stream.__next__()
