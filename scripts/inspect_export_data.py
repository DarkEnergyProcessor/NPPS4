import npps4.script_dummy  # Must be first

import argparse
import base64
import json
import sys

import npps4.config.config
import npps4.idol
import npps4.system.handover
import npps4.system.lila


def tobytesutf8(input: str):
    return input.encode("utf-8")


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("file", nargs="?", help="Base64-encoded exported account data.")
    parser.add_argument(
        "--signature",
        type=base64.urlsafe_b64decode,
        help="Signature data to verify the exported account data.",
        default=None,
    )
    parser.add_argument(
        "--secret-key",
        type=tobytesutf8,
        default=npps4.config.config.get_secret_key(),
        help="Secret key used for signing the account dta.",
        required=False,
    )
    parser.add_argument("--compact", action="store_true", help="Print compact JSON representation.")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        if args.file:
            with open(args.file, "rb") as f:
                contents = f.read()
        else:
            contents = sys.stdin.buffer.read()

        decoded_contents = base64.urlsafe_b64decode(contents)
        signature_text = ""
        exitcode = 0

        if args.signature:
            try:
                account_data = npps4.system.lila.extract_serialized_data(
                    decoded_contents, args.signature, args.secret_key
                )
                signature_text = "// Signature: Good"
            except npps4.system.lila.BadSignature:
                account_data = npps4.system.lila.extract_serialized_data(decoded_contents, None, args.secret_key)
                signature_text = "// Signature: Bad"
                exitcode = 1
        else:
            account_data = npps4.system.lila.extract_serialized_data(decoded_contents, None, args.secret_key)

        if signature_text:
            sys.stderr.writelines((signature_text,))

        if args.compact:
            json_data = json.dumps(account_data.model_dump(), ensure_ascii=False, separators=(",", ":"))
        else:
            json_data = json.dumps(account_data.model_dump(), ensure_ascii=False, indent="\t")

        for i in range(0, len(json_data), 1024):
            sys.stdout.write(json_data[i : i + 1024])

        sys.exit(exitcode)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
