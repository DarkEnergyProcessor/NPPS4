import npps4.script_dummy  # isort:skip

import sqlalchemy

import npps4.db.live
import npps4.db.main
import npps4.idol
import npps4.system.live
import npps4.system.user

revision = "2_populate_normal_live_unlock"
prev_revision = "1_update_incentive_unit_info"


async def main(context: npps4.idol.BasicSchoolIdolContext):
    live_track_map: dict[int, int] = {}
    user_cache: dict[int, npps4.db.main.User] = {}

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
