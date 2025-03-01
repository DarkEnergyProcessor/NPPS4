import npps4.script_dummy  # isort:skip

import argparse

import npps4.idol
import npps4.system.user
import npps4.scriptutils.user


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    npps4.scriptutils.user.register_args(group)
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)
        await npps4.system.user.delete_user(context, target_user.id)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
