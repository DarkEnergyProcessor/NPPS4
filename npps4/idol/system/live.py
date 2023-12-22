import pydantic
import sqlalchemy

from ... import config
from ... import idol
from ...db import main
from ...db import live

from typing import Literal


class LiveNote(pydantic.BaseModel):
    timing_sec: float
    notes_attribute: int
    notes_level: int
    effect: int
    effect_value: float
    position: int
    speed: float = 1.0
    vanish: Literal[0, 1, 2] = 0


class LiveInfo(pydantic.BaseModel):
    live_difficulty_id: int
    is_random: bool = False
    ac_flag: bool = False
    swing_flag: bool = False
    notes_list: list[LiveNote]


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


async def _get_live_info_table(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    live_info = await context.db.live.get(live.SpecialLive, live_difficulty_id)
    if live_info is None:
        live_info = await context.db.live.get(live.NormalLive, live_difficulty_id)
    return live_info


async def _get_live_setting(context: idol.BasicSchoolIdolContext, live_info: live.Live):
    return await context.db.live.get(live.LiveSetting, live_info.live_setting_id)


async def get_live_lp(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    live_info = await _get_live_info_table(context, live_difficulty_id)
    if live_info is None:
        return None

    return live_info.capital_value


async def load_live(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    live_info = await _get_live_info_table(context, live_difficulty_id)
    if live_info is None:
        return None

    live_setting = await _get_live_setting(context, live_info)
    if live_setting is None:
        return None

    # TODO
    return None
