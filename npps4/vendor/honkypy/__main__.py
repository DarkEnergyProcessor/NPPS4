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

import argparse
import io
import os.path

from . import _COMBINATION, StreamIOWrapper, decrypt_setup_probe, encrypt_setup_by_gametype
from .error import HonkyPyError


def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    mgroup = parser.add_mutually_exclusive_group()
    parser.add_argument("-b", "--basename", help="The actual filename of the file.")
    mgroup.add_argument("-d", "--detect", action="store_true", help="Detect game decryption type as exit code.")
    mgroup.add_argument(
        "-e",
        "--encrypt",
        help="Perform file encryption. Default is SIF JP game file.",
        nargs="?",
        const=_COMBINATION[0][0].lower(),
        choices=[c[0].lower() for c in _COMBINATION],
    )
    parser.add_argument("-v", "--version", type=int, default=3, help="Encryption version")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", nargs="?", default=None, help="Output file path")
    return parser.parse_args()


def main_entry() -> int:
    args = get_args()
    basename = args.basename or os.path.basename(args.input)

    if args.encrypt:
        dctx = encrypt_setup_by_gametype(args.encrypt, basename, args.version)
        with open(args.input, "rb") as f:
            contents = f.read()

        with StreamIOWrapper(open(args.output or args.input, "wb"), dctx, True) as f:
            f.write(contents)
    else:
        with open(args.input, "rb") as f:
            if args.detect:
                try:
                    dctx, _ = decrypt_setup_probe(args.input, f.read(16))
                    return dctx.VERSION
                except HonkyPyError:
                    return 0
            else:
                dctx, _ = decrypt_setup_probe(args.input, f.read(16))
                f.seek(dctx.HEADER_SIZE, io.SEEK_SET)
                decrypted_data = dctx.decrypt_block(f.read())
        with open(args.output or args.input, "wb") as f:
            f.write(decrypted_data)
    return 0


def main():
    import sys

    sys.exit(main_entry())


if __name__ == "__main__":
    main()
