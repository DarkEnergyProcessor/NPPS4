import base64
import hashlib
import json
import secrets
import sys


def main(args: list[str]):
    serial_code = args[0]
    sysrand = secrets.SystemRandom()
    salt = sysrand.randbytes(16)
    serial_code_bytes = serial_code.encode("utf-8")
    digest = hashlib.sha256(salt + serial_code_bytes, usedforsecurity=False)
    json.dump({"hash": digest.hexdigest(), "salt": str(base64.urlsafe_b64encode(salt), "utf-8")}, sys.stdout)
    print(file=sys.stderr)


async def run_script(args: list[str]):
    main(args)


if __name__ == "__main__":
    main(sys.argv[1:])
