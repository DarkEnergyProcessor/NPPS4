import npps4.script_dummy  # isort:skip

import sqlalchemy

import npps4.db.live
import npps4.db.main
import npps4.idol
import npps4.system.live
import npps4.system.user


async def run_script(args: list[str]):
    live_track_map: dict[int, int] = {}
    user_cache: dict[int, npps4.db.main.User] = {}

    async with npps4.idol.BasicSchoolIdolContext(npps4.idol.Language.en) as context:
        q = sqlalchemy.select(npps4.db.main.LiveClear)
        result = await context.db.main.execute(q)

        for row in result.scalars():
            if row.user_id not in user_cache:
                target_user = await npps4.system.user.get(context, row.user_id)
                if target_user is None:
                    continue
                user_cache[row.user_id] = target_user
            else:
                target_user = user_cache[row.user_id]

            if row.live_difficulty_id not in live_track_map:
                q = sqlalchemy.select(npps4.db.live.NormalLive.live_setting_id).where(
                    npps4.db.live.NormalLive.live_difficulty_id == row.live_difficulty_id
                )
                result = await context.db.live.execute(q)
                live_setting_id = result.scalar()
                if live_setting_id is None:
                    continue

                live_setting_info = await npps4.system.live.get_live_setting(context, live_setting_id)
                if live_setting_info is None:
                    continue
                live_track_map[row.live_difficulty_id] = live_setting_info.live_track_id

            await npps4.system.live.unlock_normal_live(context, target_user, live_track_map[row.live_difficulty_id])


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
