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


class HonkyPyError(ValueError):
    """Base class for all Honkypy-related errors, excluding user error."""

    def __init__(self, message: str):
        super().__init__(message)


class HonkyPyDecryptError(HonkyPyError):
    def __init__(self, message: str):
        super().__init__(message)


class HonkyPyUserError(HonkyPyError):
    def __init__(self, message: str):
        super().__init__(message)


class NoSuitableModeError(HonkyPyDecryptError):
    """No suitable decryption mode found."""

    def __init__(self):
        super().__init__("No suitable decryption mode found")


class InsufficientHeaderDataError(HonkyPyUserError):
    """Insufficient header data (need at least 16 bytes)"""

    def __init__(self):
        super().__init__("Insufficient header data (need at least 16 bytes)")


class VersionOutOfRange(HonkyPyUserError):
    """Version out-of-range"""

    def __init__(self):
        super().__init__("Version out-of-range")


class VersionUnsupported(HonkyPyDecryptError):
    """Decryption version not supported"""

    def __init__(self, version: str):
        super().__init__(f"Decryption version {version} not supported")


class KeyTablesMissingError(HonkyPyUserError):
    """V3 requires key tables"""

    def __init__(self):
        super().__init__("V3 requires key tables")


class InvalidGameType(HonkyPyUserError):
    """Invalid game type"""

    def __init__(self, gametype: str):
        super().__init__(f"Invalid game type '{gametype}'")


class InvalidHeaderError(HonkyPyDecryptError):
    """Version header invalid"""

    def __init__(self, version: str):
        super().__init__(f"Version {version} header invalid")


class NameSumMismatchError(HonkyPyDecryptError):
    """Version 3 key index name mismatch"""

    def __init__(self):
        super().__init__("Version 3 key index name mismatch")
