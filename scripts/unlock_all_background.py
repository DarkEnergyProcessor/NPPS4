import argparse

import sqlalchemy

import npps4.idol
import npps4.system.background
import npps4.db.main
import npps4.db.item
import npps4.scriptutils.user


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    group = parser.add_mutually_exclusive_group(required=True)
    npps4.scriptutils.user.register_args(group)
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)
        q = sqlalchemy.select(npps4.db.item.Background)
        result = await context.db.item.execute(q)
        for game_bg in result.scalars():
            if not await npps4.system.background.has_background(context, target_user, game_bg.background_id):
                await npps4.system.background.unlock_background(context, target_user, game_bg.background_id)
