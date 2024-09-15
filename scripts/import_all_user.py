import npps4.script_dummy  # Must be first

import argparse
import struct
import traceback

import npps4.config.config
import npps4.db.main
import npps4.idol
import npps4.system.handover
import npps4.system.lila


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("input", help="Exported data input file (binary)")
    parser.add_argument("--no-verify", action="store_true", help="Disable signature verification")
    args = parser.parse_args(arg)

    with open(args.input, "rb") as f:
        async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
            while True:
                signature_size = f.read(1)
                if len(signature_size) == 0:
                    print("EOF reached. Completing import.")
                    break

                # Read binary data
                signature = f.read(signature_size[0])
                payload_size: int = struct.unpack("<I", f.read(4))[0]
                payload = f.read(payload_size)

                account_data = None
                try:
                    account_data = npps4.system.lila.extract_serialized_data(
                        payload, None if args.no_verify else signature
                    )
                    target_user = await npps4.system.lila.import_user(context, account_data)
                except Exception as e:
                    if account_data is None:
                        account_data = npps4.system.lila.extract_serialized_data(payload, None)
                    print("Cannot import user:", account_data.user.name)
                    traceback.print_exception(e)
                    continue

                print("Imported user:", target_user.id, target_user.name, target_user.invite_code)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
