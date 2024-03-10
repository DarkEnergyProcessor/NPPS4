import random

import pydantic
import sqlalchemy


from . import item
from ... import db
from ... import idol
from ...config import config
from ...const import LIVE_GOAL_TYPE
from ...db import main
from ...db import live

from typing import Iterable, Literal, Sequence


class LiveNote(pydantic.BaseModel):
    timing_sec: float
    notes_attribute: int
    notes_level: int
    effect: int
    effect_value: float
    position: int
    speed: float = 1.0  # Higher = slower. Lower = faster.
    vanish: Literal[0, 1, 2] = 0  # 0 = Normal. 1 = Hidden. 2 = Sudden.


class LiveInfo(pydantic.BaseModel):
    live_difficulty_id: int
    is_random: bool = False
    ac_flag: int = 0
    swing_flag: int = 0


class LiveInfoWithNotes(LiveInfo):
    notes_list: list[LiveNote]


class LiveStatus(pydantic.BaseModel):
    live_difficulty_id: int
    status: int
    hi_score: int
    hi_combo_count: int
    clear_cnt: int
    achieved_goal_id_list: list[int]


async def unlock_normal_live(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int):
    q = sqlalchemy.select(live.LiveSetting).where(live.LiveSetting.live_track_id == live_track_id)
    result = await context.db.live.execute(q)

    # Get live_setting_ids
    for setting_data in result.scalars():
        # Then query live_difficulty_ids
        q = sqlalchemy.select(live.NormalLive).where(live.NormalLive.live_setting_id == setting_data.live_setting_id)
        result = await context.db.live.execute(q)

        # Add to live clear table
        normallive = result.scalar()
        if normallive is not None:
            live_clear = main.LiveClear(
                user_id=user.id, live_difficulty_id=normallive.live_difficulty_id, difficulty=setting_data.difficulty
            )
            context.db.main.add(live_clear)

    await context.db.main.flush()


async def init(context: idol.BasicSchoolIdolContext, user: main.User):
    await unlock_normal_live(context, user, 1)  # Bokura no LIVE Kimi to no LIFE

    # Unlock the rest of the live shows.
    q = sqlalchemy.select(live.NormalLive).where(live.NormalLive.default_unlocked_flag == 1)
    result = await context.db.live.execute(q)

    for normallive in result.scalars():
        setting_data = await context.db.live.get(live.LiveSetting, normallive.live_setting_id)
        assert setting_data is not None
        live_clear = main.LiveClear(
            user_id=user.id, live_difficulty_id=normallive.live_difficulty_id, difficulty=setting_data.difficulty
        )
        context.db.main.add(live_clear)

    await context.db.main.flush()


async def get_live_clear_data(context: idol.BasicSchoolIdolContext, user: main.User, live_difficulty_id: int):
    q = sqlalchemy.select(main.LiveClear).where(
        main.LiveClear.user_id == user.id, main.LiveClear.live_difficulty_id == live_difficulty_id
    )
    result = await context.db.main.execute(q)
    return result.scalar()


async def get_normal_live_clear_status(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.LiveClear).where(main.LiveClear.user_id == user.id)
    result = await context.db.main.execute(q)
    return [
        LiveStatus(
            live_difficulty_id=a.live_difficulty_id,
            status=2,
            hi_score=a.hi_score,
            hi_combo_count=a.hi_combo_cnt,
            clear_cnt=a.clear_cnt,
            achieved_goal_id_list=await get_achieved_goal_id_list(context, a),
        )
        for a in result.scalars()
    ]


async def get_live_info_table(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    live_info = await context.db.live.get(live.SpecialLive, live_difficulty_id)
    if live_info is None:
        live_info = await context.db.live.get(live.NormalLive, live_difficulty_id)
    return live_info


async def get_live_setting(context: idol.BasicSchoolIdolContext, live_info: live.Live):
    return await db.get_decrypted_row(context.db.live, live.LiveSetting, live_info.live_setting_id)


async def get_live_lp(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    live_info = await get_live_info_table(context, live_difficulty_id)
    if live_info is None:
        return None

    return live_info.capital_value


async def get_live_setting_from_difficulty_id(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    live_info = await get_live_info_table(context, live_difficulty_id)
    if live_info is None:
        return None

    live_setting = await get_live_setting(context, live_info)
    return live_setting


async def get_live_info(context: idol.BasicSchoolIdolContext, live_difficulty_id: int, live_setting: live.LiveSetting):
    beatmap_protocol = config.get_beatmap_provider_protocol()
    beatmap_data = await beatmap_protocol.get_beatmap_data(live_setting.notes_setting_asset, context)
    if beatmap_data is None:
        return None

    # TODO: Randomize
    return LiveInfoWithNotes(
        live_difficulty_id=live_difficulty_id,
        ac_flag=live_setting.ac_flag,
        swing_flag=live_setting.swing_flag,
        notes_list=[
            LiveNote(
                timing_sec=l.timing_sec,
                notes_attribute=l.notes_attribute,
                notes_level=l.notes_level,
                effect=l.effect,
                effect_value=l.effect_value,
                position=l.position,
                speed=l.speed,
                vanish=l.vanish,
            )
            for l in beatmap_data
        ],
    )


async def get_live_info_without_notes(
    context: idol.BasicSchoolIdolContext, live_difficulty_id: int, live_setting: live.LiveSetting
):
    return LiveInfo(
        live_difficulty_id=live_difficulty_id,
        ac_flag=live_setting.ac_flag,
        swing_flag=live_setting.swing_flag,
    )


async def get_goal_list_by_live_difficulty_id(context: idol.BasicSchoolIdolContext, live_difficulty_id: int):
    q = sqlalchemy.select(live.LiveGoalReward).where(live.LiveGoalReward.live_difficulty_id == live_difficulty_id)
    result = await context.db.live.execute(q)
    return list(result.scalars())


MAX_INT = 2147483647


def make_rank_range(live_info: live.CommonLive, live_setting: live.LiveSetting):
    return {
        # Note: The ranges are in reverse order
        LIVE_GOAL_TYPE.SCORE: [
            range(live_setting.s_rank_score, MAX_INT),
            range(live_setting.a_rank_score, live_setting.s_rank_score),
            range(live_setting.b_rank_score, live_setting.a_rank_score),
            range(live_setting.c_rank_score, live_setting.b_rank_score),
        ],
        LIVE_GOAL_TYPE.COMBO: [
            range(live_setting.s_rank_combo, MAX_INT),
            range(live_setting.a_rank_combo, live_setting.s_rank_combo),
            range(live_setting.b_rank_combo, live_setting.a_rank_combo),
            range(live_setting.c_rank_combo, live_setting.b_rank_combo),
        ],
        LIVE_GOAL_TYPE.CLEAR: [
            range(live_info.s_rank_complete, MAX_INT),
            range(live_info.a_rank_complete, live_info.s_rank_complete),
            range(live_info.b_rank_complete, live_info.a_rank_complete),
            range(live_info.c_rank_complete, live_info.b_rank_complete),
        ],
    }


def get_index_of_range(value: int, seq: Iterable[Sequence[int]], start: int = 0, default: int = -1):
    for i, r in enumerate(seq, start):
        if value in r:
            return i

    return default


LIVE_GOAL_TYPES = (LIVE_GOAL_TYPE.SCORE, LIVE_GOAL_TYPE.COMBO, LIVE_GOAL_TYPE.CLEAR)


def get_live_ranks(live_info: live.CommonLive, live_setting: live.LiveSetting, score: int, combo: int, clears: int):
    rank_ranges = make_rank_range(live_info, live_setting)
    score_rank = get_index_of_range(score, rank_ranges[LIVE_GOAL_TYPE.SCORE], 1, 5)
    combo_rank = get_index_of_range(combo, rank_ranges[LIVE_GOAL_TYPE.COMBO], 1, 5)
    clear_rank = get_index_of_range(clears, rank_ranges[LIVE_GOAL_TYPE.CLEAR], 1, 5)
    return score_rank, combo_rank, clear_rank


async def get_achieved_goal_id_list(context: idol.BasicSchoolIdolContext, clear_info: main.LiveClear):
    live_info = await get_live_info_table(context, clear_info.live_difficulty_id)
    result: list[int] = []
    if live_info is not None:
        live_setting = await get_live_setting(context, live_info)
        if live_setting is not None:
            # Sort out the goal rewards
            goal_list = await get_goal_list_by_live_difficulty_id(context, clear_info.live_difficulty_id)
            goal_list_by_type = dict(
                (
                    i,
                    sorted(
                        filter(lambda g: g.live_goal_type == i, goal_list),
                        key=lambda g: g.rank,
                    ),
                )
                for i in LIVE_GOAL_TYPES
            )
            score_rank, combo_rank, clear_rank = get_live_ranks(
                live_info, live_setting, clear_info.hi_score, clear_info.hi_combo_cnt, clear_info.clear_cnt
            )
            result.extend(
                g.live_goal_reward_id for g in goal_list_by_type[LIVE_GOAL_TYPE.SCORE] if score_rank <= g.rank
            )
            result.extend(
                g.live_goal_reward_id for g in goal_list_by_type[LIVE_GOAL_TYPE.COMBO] if combo_rank <= g.rank
            )
            result.extend(
                g.live_goal_reward_id for g in goal_list_by_type[LIVE_GOAL_TYPE.CLEAR] if clear_rank <= g.rank
            )

    return result


async def get_goal_rewards(context: idol.BasicSchoolIdolContext, goal_ids: list[int]):
    q = sqlalchemy.select(live.LiveGoalReward).where(live.LiveGoalReward.live_goal_reward_id.in_(goal_ids))
    result = await context.db.live.execute(q)
    return [
        item.item_model.Item(
            add_type=k.add_type,
            item_id=k.item_id,
            amount=k.amount,
            item_category_id=k.item_category_id or 0,
            reward_box_flag=False,
        )
        for k in result.scalars()
    ]


async def has_live_unlock(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int):
    q = sqlalchemy.select(live.LiveSetting).where(live.LiveSetting.live_track_id == live_track_id)
    result = await context.db.live.execute(q)
    live_setting_ids = [setting.live_setting_id for setting in result.scalars()]

    q = sqlalchemy.select(live.NormalLive).where(live.NormalLive.live_setting_id.in_(live_setting_ids))
    result = await context.db.live.execute(q)
    live_difficulty_ids = [l.live_difficulty_id for l in result.scalars()]

    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.LiveClear)
        .where(main.LiveClear.user_id == user.id, main.LiveClear.live_difficulty_id.in_(live_difficulty_ids))
    )
    result = await context.db.main.execute(q)
    return (result.scalar() or 0) > 0


async def get_live_in_progress(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.LiveInProgress).where(main.LiveInProgress.user_id == user.id)
    result = await context.db.main.execute(q)
    return result.scalar()


async def clean_live_in_progress(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.delete(main.LiveInProgress).where(main.LiveInProgress.user_id == user.id)
    result = await context.db.main.execute(q)
    return result.rowcount > 0


async def register_live_in_progress(
    context: idol.BasicSchoolIdolContext, user: main.User, party_user: main.User, lp_factor: int, unit_deck_id: int
):
    live_in_progress = await get_live_in_progress(context, user)
    if live_in_progress is None:
        wip = main.LiveInProgress(
            user_id=user.id, party_user_id=party_user.id, lp_factor=lp_factor, unit_deck_id=unit_deck_id
        )
        context.db.main.add(wip)
    else:
        live_in_progress.party_user_id = party_user.id
        live_in_progress.lp_factor = lp_factor
        live_in_progress.unit_deck_id = unit_deck_id
    await context.db.main.flush()
