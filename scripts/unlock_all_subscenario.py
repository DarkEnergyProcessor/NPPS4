import argparse

import sqlalchemy

import npps4.idol
import npps4.system.subscenario
import npps4.db.main
import npps4.db.subscenario
import npps4.scriptutils.user


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    group = parser.add_mutually_exclusive_group(required=True)
    npps4.scriptutils.user.register_args(group)
    parser.add_argument("--unread", action="store_true", help="Mark as unread instead of readed.")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)
        q = sqlalchemy.select(npps4.db.subscenario.SubScenario)
        result = await context.db.subscenario.execute(q)
        for game_subsc in result.scalars():
            subsc = await npps4.system.subscenario.get(context, target_user, game_subsc.subscenario_id)
            if subsc is None:
                subsc = npps4.db.main.SubScenario(user_id=target_user.id, subscenario_id=game_subsc.subscenario_id)
                context.db.main.add(subsc)

            subsc.completed = not args.unread


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
