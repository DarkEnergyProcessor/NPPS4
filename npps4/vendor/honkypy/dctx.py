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

from .error import *
from .util import calculate_md5

from typing import ClassVar, cast

__all__ = [
    "DecrypterContext",
    "Version1Context",
    "Version2Context",
    "Version3Context",
    "Version4Context",
    "setup_v3",
]


class _LCGKeys:
    def __init__(self, a: int, c: int, s: int):
        self.a = a
        self.c = c
        self.shift = s

    def next(self, x: int):
        return (x * self.a + self.c) & 0xFFFFFFFF


_V4_LCG_PARAM = [
    _LCGKeys(1103515245, 12345, 15),
    _LCGKeys(22695477, 1, 23),
    _LCGKeys(214013, 2531011, 24),
    _LCGKeys(65793, 4282663, 8),
]


class DecrypterContext:
    # Contains the header size of this particular decrypter context.
    HEADER_SIZE: ClassVar[int] = cast(int, 0)

    # Contains the crypt version number for this context.
    VERSION: ClassVar[int] = cast(int, 0)

    def decrypt_int(self, data: int) -> int:
        """Decrypt single byte represented as int.

        Args:
            data (int): Single byte to decrypt, in range of 0 inclusive to 256 exclusive.

        Returns:
            int: Decrypted byte as int.
        """
        raise NotImplementedError("Please derive")

    def goto_offset(self, pos: int) -> None:
        """Recalculate decrypter context to decrypt at specified position in the file stream.

        Args:
            pos (int): New position, starting from the start of file.

        Raises:
            NotImplementedError: Raised when seeking is not supported.
        """
        raise NotImplementedError("Please derive")

    def decrypt_block(self, data: bytes) -> bytes:
        """Decrypt bytes of data and return new bytes from it.

        Args:
            data (bytes): Data to decrypt.

        Returns:
            bytes: Decrypted data.
        """
        return bytes(map(self.decrypt_int, data))

    def emit_header(self) -> bytes:
        """Print out the file header that identify the encryption mode.

        Returns:
            bytes: Header that should be written before encrypted data.
        """
        return b""


class Version1Context(DecrypterContext):
    VERSION: ClassVar[int] = 1

    def __init__(
        self, prefix: bytes, filename: bytes, key_tables: list[int] | None = None, header_test: bytes | None = None
    ):
        digest, basename = calculate_md5(prefix, filename)
        self.update_key = (len(basename) & 0x3F) + 1
        self.init_key = (digest[0] << 24) | (digest[1] << 16) | (digest[2] << 8) | digest[3]
        self.xor_key = self.init_key
        self.pos = 0

    def decrypt_int(self, data: int) -> int:
        # Same key used to decrypt 4 bytes at a time, from msb to lsb.
        index = self.pos & 3
        key = (self.xor_key >> (3 - index) * 8) & 0xFF
        result = data ^ key
        if index == 3:
            self._step()
        self.pos = self.pos + 1
        return result

    def goto_offset(self, pos: int):
        # Is it bounded?
        pos = max(pos, 0)
        currentpos4 = self.pos // 4
        newpos4 = pos // 4
        if currentpos4 == newpos4:
            # Only set pos
            self.pos = pos
            return
        # Is it forward?
        if newpos4 > currentpos4:
            for i in range(currentpos4, newpos4):
                self._step()
            self.pos = pos
            return
        # TODO: Check if it's worth starting from beginning
        # Start from beginning
        self.xor_key = self.init_key
        for i in range(newpos4):
            self._step()
        self.pos = pos

    def _step(self):
        self.xor_key = (self.xor_key + self.update_key) & 0xFFFFFFFF


class Version2Context(DecrypterContext):
    HEADER_SIZE: ClassVar[int] = 4
    VERSION: ClassVar[int] = 2

    def __init__(
        self, prefix: bytes, filename: bytes, key_tables: list[int] | None = None, header_test: bytes | None = None
    ):
        digest, basename = calculate_md5(prefix, filename)
        if header_test is not None and digest[4:8] != header_test[:4]:
            raise InvalidHeaderError("2")
        self.header = digest[4:8]
        self.init_key = ((digest[0] & 0x7F) << 24) | (digest[1] << 16) | (digest[2] << 8) | digest[3]
        self.xor_key = ((self.init_key >> 23) & 0xFF) | ((self.init_key >> 7) & 0xFF00)
        self.update_key = self.init_key
        self.pos = 0

    def decrypt_int(self, data: int) -> int:
        # Same key used to decrypt 2 bytes at a time, from lsb to msb.
        index = self.pos & 1
        key = (self.xor_key >> index * 8) & 0xFF
        result = data ^ key
        if index == 1:
            self._step()
        self.pos = self.pos + 1
        return result

    def goto_offset(self, pos: int):
        # Is it bounded?
        pos = max(pos, 0)
        currentpos2 = self.pos // 2
        newpos2 = pos // 2
        if currentpos2 == newpos2:
            # Only set pos
            self.pos = pos
            return
        # Is it forward?
        if newpos2 > currentpos2:
            for i in range(currentpos2, newpos2):
                self._step()
            self.pos = pos
            return
        # TODO: Check if it's worth starting from beginning
        # Start from beginning
        self.xor_key = ((self.init_key >> 23) & 0xFF) | ((self.init_key >> 7) & 0xFF00)
        for i in range(newpos2):
            self._step()
        self.pos = pos

    def _step(self):
        a = self.update_key >> 16
        b = ((a * 0x41A70000) & 0x7FFFFFFF + (self.update_key & 0xFFFF) * 0x41A7) & 0xFFFFFFFF
        c = ((a * 0x41A7) >> 15) & 0xFFFFFFFF
        d = c + b
        e = (d - 0x7FFFFFFF) % 0x100000000
        f = e if e > 0x7FFFFFFE else d
        self.update_key = f
        self.xor_key = ((f >> 23) & 0xFF) | ((f >> 7) & 0xFF00)

    def emit_header(self) -> bytes:
        return self.header


class _V3Base(DecrypterContext):
    HEADER_SIZE: ClassVar[int] = 16
    pos: int
    lcg: _LCGKeys
    init_key: int

    def decrypt_int(self, data: int):
        result = (data & 0xFF) ^ ((self.update_key >> (self.lcg.shift & 0x1F)) & 0xFF)
        self.pos = self.pos + 1
        self._step()
        return result

    def goto_offset(self, pos: int) -> None:
        if self.pos >= pos:
            loop = pos - self.pos
        else:
            self.update_key = self.init_key
            loop = pos
        for i in range(loop):
            self._step()
        self.pos = pos

    def _step(self):
        self.update_key = self.lcg.next(self.update_key)


class Version3Context(_V3Base):
    VERSION: ClassVar[int] = 3

    def __init__(
        self,
        prefix: bytes,
        md5digest: bytes,
        basename: bytes,
        key_tables: list[int],
        enforce_ns: bool = True,
        *,
        flip: bool = False,
        header_ns: int | None = None,
    ):
        if header_ns is not None and not enforce_ns:
            self.name_sum = header_ns
        else:
            self.name_sum = sum(prefix) + sum(basename)

        if header_ns is not None and (not enforce_ns) and header_ns != self.name_sum:
            raise NameSumMismatchError()

        self.lcg = _V4_LCG_PARAM[2]  # MSVC
        self.init_key = key_tables[self.name_sum & 0x3F]
        self.flipped = flip
        if flip == 1:
            self.init_key = (~self.init_key) & 0xFFFFFFFF
        self.update_key = self.init_key
        self.pos = 0
        self.md5 = md5digest

    def emit_header(self) -> bytes:
        return bytes(
            [
                (~self.md5[4]) & 0xFF,
                (~self.md5[5]) & 0xFF,
                (~self.md5[6]) & 0xFF,
                12,
                0,
                0,
                0,
                int(self.flipped),
                (self.name_sum >> 24) & 0xFF,
                (self.name_sum >> 16) & 0xFF,
                (self.name_sum >> 8) & 0xFF,
                self.name_sum & 0xFF,
                0,
                0,
                0,
                0,
            ]
        )


class Version4Context(_V3Base):
    VERSION: ClassVar[int] = 4

    def __init__(
        self,
        md5hash: bytes,
        lcg_index: int,
    ):
        self.lcg = _V4_LCG_PARAM[lcg_index]
        self.lcg_index = lcg_index
        self.init_key = (md5hash[8] << 24) | (md5hash[9] << 16) | (md5hash[10] << 8) | md5hash[11]
        self.update_key = self.init_key
        self.pos = 0
        self.md5 = md5hash

    def emit_header(self) -> bytes:
        return bytes(
            [
                (~self.md5[4]) & 0xFF,
                (~self.md5[5]) & 0xFF,
                (~self.md5[6]) & 0xFF,
                12,
                0,
                0,
                self.lcg_index,
                2,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
        )


def _test_v3(header: bytes | None, md5hash: bytes):
    if header is not None:
        if len(header) < 16:
            raise InsufficientHeaderDataError()
        elif header[0] != (~md5hash[4] & 255) or header[1] != (~md5hash[5] & 255) or header[2] != (~md5hash[6] & 255):
            raise InvalidHeaderError("3+")


def setup_v3(
    prefix: bytes,
    filename: bytes,
    key_tables: list[int] | None = None,
    header_test: bytes | None = None,
    *,
    version: int = 0,
    flip_v3: bool = False,
    lcg_key_v4: int = 0,
    enforce_ns_v3: bool = True,
):
    """Routine for encrypt/decryption setup for Version 3+ game files.

    Args:
        prefix (bytes): Game file prefix. Can be one of `NAME_PREFIX_*`
        filename (bytes): Name of the file. The basename is used to derive the key.
        key_tables (list[int] | None, optional): Key tables with 64 elements used for V3 decryption. Can be one of `KEY_TABLES_*`. Defaults to None.
        header_test (bytes | None, optional): When decrypting, first 16 bytes of the file contents. Defaults to None which means encryption is assumed.
        version (int, optional): Decrypt/encrypt version. Must be 0 or at least 3 or more. Defaults to 0.
        flip_v3 (bool, optional): Whetever to flip the initial key in V3. Defaults to False.
        lcg_key_v4 (int, optional): Linear Congruential Generator key index for V4. Defaults to 0.
        enforce_ns_v3 (bool, optional): Perform strict name-sum checking in V3 header. Defaults to True.

    Raises:
        VersionOutOfRange: When version is 0 (when encrypting) or less than 0.
        VersionUnsupported: When the header needs newer decryption version that HonkyPy doesn't support.
        KeyTablesMissingError: When V3 decryption is used but no key tables is present.
        NameSumMismatchError: When name-sum mismatch is detected in V3 header when decrypting.

    Returns:
        _type_: _description_
    """
    digest, basename = calculate_md5(prefix, filename)
    header_ns = None
    if header_test is not None:
        _test_v3(header_test, digest)
        if version <= 0:
            if header_test[7] < 2:
                version = 3
                flip_v3 = header_test[7] == 1
                header_ns = (header_test[10] << 8) | header_test[11]
            elif header_test[7] == 2:
                version = 4
                lcg_key_v4 = header_test[6]
            else:
                # TODO
                raise VersionUnsupported("5+")
        elif version < 3:
            raise VersionOutOfRange()
    if version <= 0:
        raise VersionOutOfRange()
    if version == 3:
        if key_tables is None:
            raise KeyTablesMissingError()
        return Version3Context(prefix, digest, basename, key_tables, enforce_ns_v3, flip=flip_v3, header_ns=header_ns)
    elif version == 4:
        return Version4Context(digest, lcg_key_v4)
    raise VersionOutOfRange()
