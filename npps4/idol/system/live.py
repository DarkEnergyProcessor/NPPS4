import sqlalchemy

from ... import idol
from ...db import main
from ...db import live


async def unlock_live(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int):
    q = sqlalchemy.select(live.LiveSetting).where(live.LiveSetting.live_track_id == live_track_id)
    result = await context.db.live.execute(q)

    # Get live_setting_ids
    livesettings: list[sqlalchemy.ColumnElement[bool]] = []
    for setting in result.scalars():
        livesettings.append(live.NormalLive.live_setting_id == setting.live_setting_id)

    # Then query live_difficulty_ids
    q = sqlalchemy.select(live.NormalLive).where(sqlalchemy.or_(sqlalchemy.false(), *livesettings))
    result = await context.db.live.execute(q)

    # Add to live clear table
    for normallive in result.scalars():
        live_clear = main.LiveClear(user_id=user.id, live_difficulty_id=normallive.live_difficulty_id)
        context.db.main.add(live_clear)

    await context.db.main.flush()


async def init(context: idol.BasicSchoolIdolContext, user: main.User):
    await unlock_live(context, user, 1)  # Bokura no LIVE Kimi to no LIFE

    # Unlock the rest of the live shows.
    q = sqlalchemy.select(live.NormalLive).where(live.NormalLive.default_unlocked_flag == 1)
    result = await context.db.live.execute(q)

    for normallive in result.scalars():
        live_clear = main.LiveClear(user_id=user.id, live_difficulty_id=normallive.live_difficulty_id)
        context.db.main.add(live_clear)

    await context.db.main.flush()
