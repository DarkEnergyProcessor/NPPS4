import npps4.script_dummy  # isort:skip

import argparse
import base64
import sys

import npps4.config.config
import npps4.idol
import npps4.system.handover
import npps4.system.lila
import npps4.scriptutils.user


def tobytesutf8(input: str):
    return input.encode("utf-8")


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    npps4.scriptutils.user.register_args(parser.add_mutually_exclusive_group(required=True))
    parser.add_argument("output", nargs="?", help="Exported account data output file")
    parser.add_argument(
        "--secret-key",
        type=tobytesutf8,
        default=npps4.config.config.get_secret_key(),
        help="Secret key used for signing.",
        required=False,
    )
    parser.add_argument("--nullify-credentials", action="store_true", help="Remove credentials from exported data.")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)
        serialized_data, signature = await npps4.system.lila.export_user(
            context, target_user, args.secret_key, args.nullify_credentials
        )

        print("Signature:", str(base64.urlsafe_b64encode(signature), "utf-8"), file=sys.stderr)

        if args.output:
            with open(args.output, "wb") as f:
                f.write(base64.urlsafe_b64encode(serialized_data))
        else:
            sys.stdout.buffer.write(base64.urlsafe_b64encode(serialized_data))


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
