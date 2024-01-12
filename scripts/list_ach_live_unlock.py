#!/usr/bin/env python -m npps4.script
import sqlalchemy

import npps4.db.main
import npps4.db.achievement
import npps4.db.live
import npps4.idol

from typing import TypeVar, cast

_T = TypeVar("_T")


def assume_some(v: _T | None) -> _T:
    return cast(_T, v)


def select_en(jp: str, en: str | None):
    return en or jp


async def run_script(args: list[str]):
    context = npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en)

    async with context:
        # Get achievement that require live show unlocks
        q = sqlalchemy.select(npps4.db.achievement.Achievement).where(
            npps4.db.achievement.Achievement.achievement_type == 32
        )
        result = await context.db.achievement.execute(q)
        live_clear_ach = dict((a.achievement_id, a) for a in result.scalars())

        fast_live_clear_ach_lookup = set(live_clear_ach.keys())
        q = sqlalchemy.select(npps4.db.achievement.Story).where(
            npps4.db.achievement.Story.next_achievement_id.in_(live_clear_ach.keys())
        )
        result = await context.db.achievement.execute(q)
        ach_trees = list(filter(lambda a: a.next_achievement_id in fast_live_clear_ach_lookup, result.scalars()))

        for ach_id in sorted(ach_trees, key=lambda k: k.achievement_id):
            ach = live_clear_ach[ach_id.next_achievement_id]
            live_track_id = int(ach.params1 or 0)
            live_track = assume_some(await context.db.live.get(npps4.db.live.LiveTrack, live_track_id))
            track_name = select_en(live_track.name, live_track.name_en)
            # 110: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=3)],  # Reward: Snow Halation
            print(
                f"{ach_id.achievement_id}: [item.Reward(add_type=ADD_TYPE.LIVE, item_id={live_track_id})],  # Reward: {track_name}"
            )
