import npps4.script_dummy  # Must be first

import argparse
import base64
import sys

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
    parser.add_argument("--no-passcode", action="store_true", help="Do not create transfer passcode.")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        if args.file:
            with open(args.file, "rb") as f:
                contents = f.read()
        else:
            contents = sys.stdin.buffer.read()

        decoded_contents = base64.urlsafe_b64decode(contents)
        account_data = npps4.system.lila.extract_serialized_data(decoded_contents, args.signature)

        target_user = await npps4.system.lila.import_user(context, account_data)
        print("User ID:", target_user.id)
        print("Name:", target_user.name)
        print("Friend ID:", target_user.invite_code)

        if not args.no_passcode:
            transfer_code = npps4.system.handover.generate_transfer_code()
            target_user.transfer_sha1 = npps4.system.handover.generate_passcode_sha1(
                target_user.invite_code, transfer_code
            )
            print("Transfer ID:", target_user.invite_code)
            print("Transfer Passcode:", transfer_code)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
