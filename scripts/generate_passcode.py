import argparse

import npps4.idol
import npps4.system.handover
import npps4.scriptutils.user


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    group = parser.add_mutually_exclusive_group(required=True)
    npps4.scriptutils.user.register_args(group)
    parser.add_argument("passcode", nargs="?", default=None)
    args = parser.parse_args(arg)

    transfer_code = args.passcode or npps4.system.handover.generate_transfer_code()

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)
        target_user.transfer_sha1 = npps4.system.handover.generate_passcode_sha1(target_user.invite_code, transfer_code)

        print("Transfer ID:", target_user.invite_code)
        print("Transfer Passcode:", transfer_code)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
