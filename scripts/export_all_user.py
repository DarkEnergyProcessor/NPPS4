import npps4.script_dummy  # Must be first

import argparse
import struct
import traceback

import sqlalchemy

import npps4.config.config
import npps4.db.main
import npps4.idol
import npps4.system.handover
import npps4.system.lila


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("output", help="Exported data output file (binary)")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        with open(args.output, "wb") as f:
            q = sqlalchemy.select(npps4.db.main.User).where(
                ((npps4.db.main.User.key != None) & (npps4.db.main.User.passwd != None))
                | (npps4.db.main.User.transfer_sha1 != None)
            )
            result = await context.db.main.execute(q)

            for target_user in result.scalars():
                try:
                    serialized_data, signature = await npps4.system.lila.export_user(context, target_user)
                except Exception as e:
                    print("Cannot export user:", target_user.id, target_user.name, target_user.invite_code)
                    traceback.print_exception(e)
                    continue

                payloadsize = struct.pack("<I", len(serialized_data))
                f.write(bytes((len(signature),)))
                f.write(signature)
                f.write(payloadsize)
                f.write(serialized_data)
                print("Exported user:", target_user.id, target_user.name, target_user.invite_code)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
