import argparse

import sqlalchemy

import npps4.idol
import npps4.idol.system.background
import npps4.db.main
import npps4.db.item


async def user_from_invite(context: npps4.idol.BasicSchoolIdolContext, invite_code: int):
    q = sqlalchemy.select(npps4.db.main.User).where(npps4.db.main.User.invite_code == invite_code)
    result = await context.db.main.execute(q)
    return result.scalar()


async def user_from_id(context: npps4.idol.BasicSchoolIdolContext, uid: int):
    return await context.db.main.get(npps4.db.main.User, uid)


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--user-id", type=int, help="User ID.")
    group.add_argument("-i", "--invite-code", type=int, help="Invite Code.")
    args = parser.parse_args(arg)

    context = npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en)
    async with context:
        if args.user_id is not None:
            target_user = await user_from_id(context, args.user_id)
        else:
            target_user = await user_from_invite(context, args.invite_code)

        if target_user is None:
            raise Exception("no such user")

        q = sqlalchemy.select(npps4.db.item.Background)
        result = await context.db.item.execute(q)
        for game_bg in result.scalars():
            if not await npps4.idol.system.background.has_background(context, target_user, game_bg.background_id):
                await npps4.idol.system.background.unlock_background(context, target_user, game_bg.background_id)
