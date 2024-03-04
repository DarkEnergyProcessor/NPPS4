import dataclasses

import pydantic
import sqlalchemy

from . import item
from ... import achievement_reward
from ... import db
from ... import idol
from ... import util
from ...db import achievement
from ...db import main

from typing import Awaitable, Callable, Concatenate, Iterable, Sequence, ParamSpec


class AchievementData(pydantic.BaseModel):
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
    def from_sqlalchemy(ach: main.Achievement, info: achievement.Achievement, rewards: list[item.Reward]):
        return AchievementData(
            achievement_id=ach.achievement_id,
            count=ach.count,
            is_accomplished=ach.is_accomplished,
            insert_date=util.timestamp_to_datetime(ach.insert_date),
            end_date=None if ach.end_date == 0 else util.timestamp_to_datetime(ach.end_date),
            remaining_time="",  # FIXME: What to put here?
            is_new=ach.is_new,
            for_display=bool(info.display_flag),
            is_locked=False,
            reward_list=rewards,
        )


@dataclasses.dataclass
class AchievementContext:
    accomplished: list[main.Achievement] = dataclasses.field(default_factory=list)
    new: list[main.Achievement] = dataclasses.field(default_factory=list)

    def extend(self, other: "AchievementContext"):
        self.accomplished.extend(other.accomplished)
        self.new.extend(other.new)

    def fix(self):
        # Anything in "new" should be removed if it's in "accomplished"
        accomplished_ids = set(ach.achievement_id for ach in self.accomplished)
        self.new = [ach for ach in self.new if ach.achievement_id not in accomplished_ids]
        return self

    def __add__(self, other: "AchievementContext"):
        return AchievementContext(self.accomplished + other.accomplished, self.new + other.new).fix()

    def has_achievement(self):
        return len(self.accomplished) > 0 and len(self.new) > 0


async def get_achievement_info(context: idol.BasicSchoolIdolContext, achievement_id: int):
    info = await db.get_decrypted_row(context.db.achievement, achievement.Achievement, achievement_id)
    if info is None:
        raise ValueError("invalid achievement")

    return info


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
        achievement_filter_category_id=ach.achievement_filter_category_id,
        count=0,
        is_accomplished=False,
        insert_date=time,
        end_date=None if ach.end_date is None else util.datetime_to_timestamp(ach.end_date),
        is_new=True,
    )
    context.db.main.add(user_ach)
    await context.db.main.flush()
    return user_ach


async def to_game_representation(
    context: idol.BasicSchoolIdolContext, achs: list[main.Achievement], rewardss: list[list[item.Reward]]
):
    return [
        AchievementData.from_sqlalchemy(ach, await get_achievement_info(context, ach.achievement_id), rewards)
        for ach, rewards in zip(achs, rewardss)
    ]


async def get_achievement_rewards(context: idol.BasicSchoolIdolContext, ach: main.Achievement):
    return achievement_reward.get(ach.achievement_id)


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


async def get_achievements(context: idol.BasicSchoolIdolContext, user: main.User, accomplished: bool | None = None):
    if accomplished is not None:
        q = sqlalchemy.select(main.Achievement).where(
            main.Achievement.user_id == user.id, main.Achievement.is_accomplished == accomplished
        )
    else:
        q = sqlalchemy.select(main.Achievement).where(main.Achievement.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def get_unclaimed_achievements(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        (main.Achievement.is_accomplished == False) | (main.Achievement.is_reward_claimed == False),
    )
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def get_unclaimed_achievements_by_filter_id(
    context: idol.BasicSchoolIdolContext, user: main.User, achievement_filter_category_id: int
):
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        main.Achievement.achievement_filter_category_id == achievement_filter_category_id,
        (main.Achievement.is_accomplished == False) | (main.Achievement.is_reward_claimed == False),
    )
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def mark_achievement_reward_claimed(context: idol.BasicSchoolIdolContext, ach: main.Achievement):
    ach.is_reward_claimed = True


async def get_achievement_count(
    context: idol.BasicSchoolIdolContext, user: main.User, accomplished: bool | None = None
):
    if accomplished is not None:
        q = (
            sqlalchemy.select(sqlalchemy.func.count())
            .select_from(main.Achievement)
            .where(main.Achievement.user_id == user.id, main.Achievement.is_accomplished == accomplished)
        )
    else:
        q = (
            sqlalchemy.select(sqlalchemy.func.count())
            .select_from(main.Achievement)
            .where(main.Achievement.user_id == user.id)
        )
    result = await context.db.main.execute(q)
    return result.scalar() or 0


def test_params(ach_info: achievement.Achievement, args: Sequence[int | None]):
    if args:
        for i in range(min(len(args), 11)):
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
    result = await context.db.main.execute(q)

    time = util.time()
    achieved: list[main.Achievement] = []
    new: list[main.Achievement] = []

    for ach in result.scalars():
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info is None:
            raise ValueError("achievement info is none, database is corrupted?")

        if test_params(ach_info, args):
            target_amount = int(getattr(ach_info, f"params{pindex}", None) or 1)
            if count >= target_amount:
                # Achieved.
                ach.count = min(count, target_amount)
                ach.is_accomplished = True
                achieved.append(ach)

                # New achievement
                for next_ach_id in await get_next_achievement_ids(context, ach.achievement_id):
                    new_ach_info = await get_achievement_info(context, next_ach_id)
                    if new_ach_info is not None:
                        new_ach = await add_achievement(context, user, new_ach_info, time)
                        # Append to new achievement
                        new.append(new_ach)
            else:
                ach.count = count

    await context.db.main.flush()
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
    result = await context.db.main.execute(q)

    time = util.time()
    achieved: list[main.Achievement] = []
    new: list[main.Achievement] = []

    for ach in result.scalars():
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info is None:
            raise ValueError("achievement info is none, database is corrupted?")

        if test_params(ach_info, args):
            target_amount = int(getattr(ach_info, f"params{pindex}", None) or 1)
            count = ach.count + increment
            if count >= target_amount:
                # Achieved.
                ach.count = min(count, target_amount)
                ach.is_accomplished = True
                achieved.append(ach)

                # New achievement
                for next_ach_id in await get_next_achievement_ids(context, ach.achievement_id):
                    new_ach_info = await get_achievement_info(context, next_ach_id)
                    if new_ach_info is not None:
                        new_ach = await add_achievement(context, user, new_ach_info, time)
                        # Append to new achievement
                        new.append(new_ach)
            else:
                ach.count = count

    await context.db.main.flush()
    return AchievementContext(accomplished=achieved, new=new)


_P = ParamSpec("_P")


def recursive_achievement(achievement_type: int, /):
    def wrapper0(
        func: Callable[Concatenate[idol.BasicSchoolIdolContext, main.User, _P], Awaitable[AchievementContext]]
    ):
        async def wrapper1(
            context: idol.BasicSchoolIdolContext, user: main.User, *args: _P.args, **kwargs: _P.kwargs
        ) -> AchievementContext:
            nonlocal achievement_type
            result = AchievementContext()

            while True:
                keep_traversing = False
                ach_result = await func(context, user, *args, **kwargs)

                if ach_result.has_achievement():
                    result = result + ach_result

                    for ach in ach_result.new:
                        if ach.achievement_type == achievement_type:
                            keep_traversing = True
                            break

                if not keep_traversing:
                    break

            return result

        return wrapper1

    return wrapper0


async def check_type_1(context: idol.BasicSchoolIdolContext, user: main.User, increment: bool):
    """
    Check live show clear achievements.
    """
    return await check_type_increment(context, user, 1, increment)


async def check_type_2(context: idol.BasicSchoolIdolContext, user: main.User, difficulty: int, increment: bool):
    """
    Check live show clear achievements by specified difficulty.
    """
    return await check_type_increment(context, user, 2, increment, 2, difficulty)


async def check_type_3(context: idol.BasicSchoolIdolContext, user: main.User, rank: int, increment: bool):
    """
    Check live show clear achievements by specified score rank.
    """
    return await check_type_increment(context, user, 3, increment, 2, rank)


async def check_type_4(context: idol.BasicSchoolIdolContext, user: main.User, rank: int, increment: bool):
    """
    Check live show clear achievements by specified combo rank.
    """
    return await check_type_increment(context, user, 4, increment, 2, rank)


async def check_type_7(context: idol.BasicSchoolIdolContext, user: main.User, unit_type_id: int, increment: bool):
    """
    Check live show clear achievements by specified combo rank.
    """
    return await check_type_increment(context, user, 4, increment, 2, unit_type_id)


@recursive_achievement(18)
async def check_type_18(context: idol.BasicSchoolIdolContext, user: main.User, club_members: int):
    """
    Check amount of club members collected.
    """
    return await check_type_countable(context, user, 18, club_members)


@recursive_achievement(19)
async def check_type_19(context: idol.BasicSchoolIdolContext, user: main.User, idolized: int):
    """
    Check amount of idolized club members.
    """
    return await check_type_countable(context, user, 19, idolized)


@recursive_achievement(20)
async def check_type_20(context: idol.BasicSchoolIdolContext, user: main.User, max_love: int):
    """
    Check amount of max bonded idolized club members.
    """
    return await check_type_countable(context, user, 20, max_love)


@recursive_achievement(21)
async def check_type_21(context: idol.BasicSchoolIdolContext, user: main.User, max_level: int):
    """
    Check amount of max leveled idolized club members.
    """
    return await check_type_countable(context, user, 21, max_level)


async def check_type_27(context: idol.BasicSchoolIdolContext, user: main.User, nlogins: int):
    """
    Check login bonus count
    """
    return await check_type_countable(context, user, 27, nlogins)


async def check_type_29(context: idol.BasicSchoolIdolContext, user: main.User):
    """
    Check one-time login bonus.
    """
    return await check_type_countable(context, user, 29, 1)


@recursive_achievement(30)
async def check_type_30(context: idol.BasicSchoolIdolContext, user: main.User, rank: int | None = None):
    """
    Check player rank.
    """
    return await check_type_countable(context, user, 30, rank or user.level)


@recursive_achievement(32)
async def check_type_32(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int):
    """
    Check live show clear of specific `live_track_id`
    """
    return await check_type_countable(context, user, 32, 1, 1, live_track_id)


async def check_type_37(context: idol.BasicSchoolIdolContext, user: main.User, live_track_id: int, increment: bool):
    """
    Check live show clear of specific `live_track_id`
    """
    return await check_type_increment(context, user, 37, increment, 1, live_track_id)


async def check_type_53_old(context: idol.BasicSchoolIdolContext, user: main.User):
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
        achievement_count_by_category: dict[int, int] = dict((i, 0) for i in achievement_id_list_by_category.keys())

        achievements = await get_achievements(context, user, True)
        for ach in achievements:
            for ach_cat_id, ach_ids in achievement_id_list_by_category.items():
                if ach.achievement_id in ach_ids:
                    achievement_count_by_category[ach_cat_id] = achievement_count_by_category[ach_cat_id] + 1

        for ach_cat_id in achievement_id_list_by_category.keys():
            achievement_result = achievement_result + await check_type_countable(
                context, user, 53, achievement_count_by_category[ach_cat_id] or 0, 2, ach_cat_id
            )

        if achievement_result.has_achievement():
            achievement_result_all = achievement_result_all + achievement_result
        else:
            break

    return achievement_result_all


@recursive_achievement(53)
async def check_type_53(
    context: idol.BasicSchoolIdolContext, user: main.User, achievement_category_id: int, count: int
):
    """
    Check amount of achievement cleared with specific category
    """
    return await check_type_countable(context, user, 53, count, 2, achievement_category_id)


async def check_type_53_recursive(context: idol.BasicSchoolIdolContext, user: main.User):
    """
    Check amount of achievement cleared on all available categories
    """
    result_complete = AchievementContext()

    while True:
        keep_going = False
        all_accomplished_by_category = await count_accomplished_achievement_by_category(context, user)
        result = AchievementContext()
        for achievement_category_id, amount in all_accomplished_by_category:
            result.extend(await check_type_53(context, user, achievement_category_id, amount))

        result_complete.extend(result)
        # Should we keep recurse?
        for ach in result.new:
            if ach.achievement_type == 53:
                keep_going = True
                break

        if not keep_going:
            break

    return result_complete


async def check_type_58(context: idol.BasicSchoolIdolContext, user: main.User, increment: bool):
    """
    Check live show clear achievements.
    """
    return await check_type_increment(context, user, 58, increment)


async def get_achievement_filter_ids(context: idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(achievement.FilterCategory)
    result = await context.db.achievement.execute(q)
    return [filter_cat.achievement_filter_category_id for filter_cat in result.scalars()]


async def count_accomplished_achievement_by_category(context: idol.BasicSchoolIdolContext, user: main.User):
    # Get all achieved
    q = (
        sqlalchemy.select(main.Achievement)
        .where(main.Achievement.user_id == user.id, main.Achievement.is_accomplished == True)
        .with_only_columns(main.Achievement.achievement_id)
    )
    print(q)
    result = await context.db.main.execute(q)
    all_accomplished = list(result.scalars())

    q = (
        sqlalchemy.select(achievement.Tag)
        .where(achievement.Tag.achievement_id.in_(all_accomplished))
        .with_only_columns(
            achievement.Tag.achievement_category_id, sqlalchemy.func.count(achievement.Tag.achievement_id.distinct())
        )
    )
    result = await context.db.achievement.execute(q)
    return [(int(r[0]), int(r[1])) for r in result]
