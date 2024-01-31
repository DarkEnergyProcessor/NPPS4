import dataclasses

import pydantic
import sqlalchemy

from . import item
from ... import achievement_reward
from ... import idol
from ... import util
from ...db import achievement
from ...db import main

from typing import Sequence


class Achievement(pydantic.BaseModel):
    achievement_id: int
    count: int
    is_accomplished: bool
    insert_date: str
    end_date: str | None = None
    remaining_time: str = ""
    is_new: bool
    for_display: bool
    is_locked: bool
    open_condition_string: str = ""
    accomplish_id: str = ""
    reward_list: list[item.Reward]

    @staticmethod
    def from_sqlalchemy(ach: main.Achievement, info: achievement.Achievement):
        return Achievement(
            achievement_id=ach.achievement_id,
            count=ach.count,
            is_accomplished=True,
            insert_date=util.timestamp_to_datetime(ach.insert_date),
            end_date=None if ach.end_date == 0 else util.timestamp_to_datetime(ach.end_date),
            remaining_time="",  # FIXME: What to put here?
            is_new=ach.is_new,
            for_display=bool(info.display_flag),
            is_locked=False,
            reward_list=achievement_reward.get(ach.achievement_id),
        )


@dataclasses.dataclass
class AchievementContext:
    accomplished: list[Achievement] = dataclasses.field(default_factory=list)
    new: list[Achievement] = dataclasses.field(default_factory=list)

    def extend(self, other: "AchievementContext"):
        self.accomplished.extend(other.accomplished)
        self.new.extend(other.new)

    def fix(self):
        # Anything in "new" should be removed if it's in "accomplished"
        accomplished_ids = set(ach.achievement_id for ach in self.accomplished)
        self.new = list(filter(lambda ach: ach.achievement_id not in accomplished_ids, self.new))
        return self

    def __add__(self, other: "AchievementContext"):
        return AchievementContext(self.accomplished + other.accomplished, self.new + other.new).fix()


async def get_achievement_info(context: idol.BasicSchoolIdolContext, achievement_id: int):
    ach = await context.db.achievement.get(achievement.Achievement, achievement_id)
    return ach


async def get_next_achievement_ids(context: idol.BasicSchoolIdolContext, achievement_id: int):
    q = sqlalchemy.select(achievement.Story).where(achievement.Story.achievement_id == achievement_id)
    result = await context.db.achievement.execute(q)
    return list(ach.next_achievement_id for ach in result.scalars())


async def add_achievement(
    context: idol.BasicSchoolIdolContext, user: main.User, ach: achievement.Achievement, time: int
):
    user_ach = main.Achievement(
        achievement_id=ach.achievement_id,
        user_id=user.id,
        achievement_type=ach.achievement_type,
        insert_date=time,
    )
    context.db.main.add(user_ach)
    return user_ach


async def init(context: idol.BasicSchoolIdolContext, user: main.User):
    time = util.time()
    q = sqlalchemy.select(achievement.Achievement).where(achievement.Achievement.default_open_flag == 1)
    result = await context.db.achievement.execute(q)

    for ach in result.scalars():
        start_date = util.datetime_to_timestamp(ach.start_date)
        end_date = util.datetime_to_timestamp(ach.end_date) if ach.end_date is not None else 0

        if time >= start_date and (end_date == 0 or time < end_date):
            user_ach = await add_achievement(context, user, ach, time)
            if end_date > 0:
                user_ach.end_date = end_date

    await context.db.main.flush()


async def test_params(ach_info: achievement.Achievement, args: Sequence[int | None]):
    for i in range(1, min(len(args), 11) + 1):
        if args[i] is not None:
            if getattr(ach_info, f"params{i}", None) != args[i]:
                return False

    return True


async def check_type_countable(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    achievement_type: int,
    count: int,
    pindex: int = 1,
    *args: int | None,
):
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        main.Achievement.achievement_type == achievement_type,
        main.Achievement.is_accomplished == False,
    )
    result = await context.db.achievement.execute(q)

    time = util.time()
    achieved: list[Achievement] = []
    new: list[Achievement] = []

    for ach in result.scalars():
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info is None:
            raise ValueError("achievement info is none, database is corrupted?")

        if test_params(ach_info, args):
            target_amount: int = getattr(ach_info, f"params{pindex}", None) or 0
            if target_amount >= count:
                # Achieved.
                ach.count = min(count, target_amount)
                ach.is_accomplished = True
                achieved.append(Achievement.from_sqlalchemy(ach, ach_info))

                # New achievement
                for next_ach_id in await get_next_achievement_ids(context, ach.achievement_id):
                    new_ach_info = await get_achievement_info(context, next_ach_id)
                    if new_ach_info is None:
                        continue

                    new_ach = await add_achievement(context, user, ach_info, time)

                    if new_ach_info is not None:
                        new_target_amount: int = getattr(new_ach_info, f"params{pindex}", None) or 0
                        if new_target_amount >= count:
                            # Trigger re-check
                            new_result = await check_type_countable(context, user, achievement_type, count, pindex)
                            achieved.extend(new_result.accomplished)
                            new.extend(new_result.new)
                        else:
                            # Append to new achievement
                            new.append(Achievement.from_sqlalchemy(new_ach, new_ach_info))
            else:
                ach.count = count

    return AchievementContext(accomplished=achieved, new=new)


async def check_type_increment(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    achievement_type: int,
    increment: bool,
    pindex: int = 1,
    *args: int | None,
):
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        main.Achievement.achievement_type == achievement_type,
        main.Achievement.is_accomplished == False,
    )
    result = await context.db.achievement.execute(q)

    time = util.time()
    achieved: list[Achievement] = []
    new: list[Achievement] = []

    for ach in result.scalars():
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info is None:
            raise ValueError("achievement info is none, database is corrupted?")

        if test_params(ach_info, args):
            target_amount: int = getattr(ach_info, f"params{pindex}", None) or 1
            count = ach.count + increment
            if target_amount >= count:
                # Achieved.
                ach.count = min(count, target_amount)
                ach.is_accomplished = True
                achieved.append(Achievement.from_sqlalchemy(ach, ach_info))

                # New achievement
                for next_ach_id in await get_next_achievement_ids(context, ach.achievement_id):
                    new_ach_info = await get_achievement_info(context, next_ach_id)
                    if new_ach_info is None:
                        continue

                    new_ach = await add_achievement(context, user, ach_info, time)

                    if new_ach_info is not None:
                        # Append to new achievement
                        new.append(Achievement.from_sqlalchemy(new_ach, new_ach_info))
            else:
                ach.count = count

    return AchievementContext(accomplished=achieved, new=new)


def check_type_1(context: idol.BasicSchoolIdolContext, user: main.User, increment: bool):
    """
    Check live show clear achievements.
    """
    return check_type_increment(context, user, 1, increment)


def check_type_18(context: idol.BasicSchoolIdolContext, user: main.User, club_members: int):
    """
    Check amount of club members collected.
    """
    return check_type_countable(context, user, 18, club_members)


def check_type_19(context: idol.BasicSchoolIdolContext, user: main.User, idolized: int):
    """
    Check amount of idolized club members.
    """
    return check_type_countable(context, user, 19, idolized)


def check_type_20(context: idol.BasicSchoolIdolContext, user: main.User, max_love: int):
    """
    Check amount of max bonded idolized club members.
    """
    return check_type_countable(context, user, 20, max_love)


def check_type_21(context: idol.BasicSchoolIdolContext, user: main.User, max_level: int):
    """
    Check amount of max leveled idolized club members.
    """
    return check_type_countable(context, user, 21, max_level)


def check_type_30(context: idol.BasicSchoolIdolContext, user: main.User, rank: int | None = None):
    """
    Check player rank.
    """
    return check_type_countable(context, user, 30, rank or user.level)


def check_type_32(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int, increment: bool):
    """
    Check live show clear of specific `live_track_id`
    """
    return check_type_increment(context, user, 32, increment, 0, live_track_id)
