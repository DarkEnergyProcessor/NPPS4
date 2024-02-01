import dataclasses

import pydantic
import sqlalchemy

from . import item
from ... import achievement_reward
from ... import idol
from ... import util
from ...db import achievement
from ...db import main

from typing import Awaitable, Callable, Concatenate, Sequence, ParamSpec


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

    def __nonzero__(self):
        return len(self.accomplished) > 0 and len(self.new) > 0


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


async def get_unaccomplished_achievements(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id, main.Achievement.is_accomplished == False
    )
    result = await context.db.main.execute(q)
    unaccomplished_achievements: list[Achievement] = []

    for ach in result.scalars():
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info:
            unaccomplished_achievements.append(Achievement.from_sqlalchemy(ach, ach_info))

    return unaccomplished_achievements


async def get_unaccomplished_achievement_count(context: idol.BasicSchoolIdolContext, user: main.User):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Achievement)
        .where(main.Achievement.user_id == user.id, main.Achievement.is_accomplished == False)
    )
    result = await context.db.main.execute(q)
    return result.scalar() or 0


def test_params(ach_info: achievement.Achievement, args: Sequence[int | None]):
    if args:
        for i in range(min(len(args), 11) + 1):
            if args[i] is not None:
                if getattr(ach_info, f"params{i + 1}", None) != args[i]:
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


_P = ParamSpec("_P")


def recursive_achievement(
    func: Callable[Concatenate[idol.BasicSchoolIdolContext, main.User, _P], Awaitable[AchievementContext]]
):
    async def wrapper(
        context: idol.BasicSchoolIdolContext, user: main.User, *args: _P.args, **kwargs: _P.kwargs
    ) -> AchievementContext:
        result = AchievementContext()

        while True:
            ach_result = await func(context, user, *args, **kwargs)

            if ach_result:
                result = result + ach_result
            else:
                break

        return result + await check_type_53_recursive(context, user)

    return wrapper


@recursive_achievement
async def check_type_1(context: idol.BasicSchoolIdolContext, user: main.User, increment: bool):
    """
    Check live show clear achievements.
    """
    return await check_type_increment(context, user, 1, increment)


@recursive_achievement
async def check_type_18(context: idol.BasicSchoolIdolContext, user: main.User, club_members: int):
    """
    Check amount of club members collected.
    """
    return await check_type_countable(context, user, 18, club_members)


@recursive_achievement
async def check_type_19(context: idol.BasicSchoolIdolContext, user: main.User, idolized: int):
    """
    Check amount of idolized club members.
    """
    return await check_type_countable(context, user, 19, idolized)


@recursive_achievement
async def check_type_20(context: idol.BasicSchoolIdolContext, user: main.User, max_love: int):
    """
    Check amount of max bonded idolized club members.
    """
    return await check_type_countable(context, user, 20, max_love)


@recursive_achievement
async def check_type_21(context: idol.BasicSchoolIdolContext, user: main.User, max_level: int):
    """
    Check amount of max leveled idolized club members.
    """
    return await check_type_countable(context, user, 21, max_level)


@recursive_achievement
async def check_type_27(context: idol.BasicSchoolIdolContext, user: main.User, nlogins: int):
    """
    Check login bonus count
    """
    return await check_type_countable(context, user, 27, nlogins)


@recursive_achievement
async def check_type_30(context: idol.BasicSchoolIdolContext, user: main.User, rank: int | None = None):
    """
    Check player rank.
    """
    return await check_type_countable(context, user, 30, rank or user.level)


@recursive_achievement
async def check_type_32(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int, increment: bool):
    """
    Check live show clear of specific `live_track_id`
    """
    return await check_type_increment(context, user, 32, increment, 1, live_track_id)


async def check_type_53_recursive(context: idol.BasicSchoolIdolContext, user: main.User):
    """
    Check amount of achievement cleared with specific category
    """
    q = (
        sqlalchemy.select(achievement.Achievement)
        .where(achievement.Achievement.achievement_type == 53)
        .group_by(achievement.Achievement.params1)
    )
    result = await context.db.achievement.execute(q)
    achievement_category_to_check = set(int(ach.params1) for ach in result.scalars() if ach.params1 is not None)
    achievement_id_list_by_category: dict[int, list[int]] = {}

    for ach_cat in achievement_category_to_check:
        q = sqlalchemy.select(achievement.Tag).where(achievement.Tag.achievement_category_id == ach_cat)
        result = await context.db.achievement.execute(q)
        achievement_id_list_by_category[ach_cat] = [ach.achievement_id for ach in result.scalars()]

    achievement_result_all = AchievementContext()

    while True:
        achievement_result = AchievementContext()

        for ach_cat, ach_ids in achievement_id_list_by_category.items():
            q = (
                sqlalchemy.select(sqlalchemy.func.count())
                .select_from(main.Achievement)
                .where(main.Achievement.user_id == user.id, main.Achievement.achievement_id.in_(ach_ids))
            )
            result = await context.db.main.execute(q)
            achievement_result = achievement_result + await check_type_countable(
                context, user, 53, result.scalar() or 0, 2, ach_cat
            )

        if achievement_result:
            achievement_result_all = achievement_result_all + achievement_result
        else:
            break

    return achievement_result_all
