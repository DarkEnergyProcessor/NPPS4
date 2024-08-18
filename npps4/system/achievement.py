import collections.abc
import dataclasses

import pydantic
import sqlalchemy

from . import advanced
from . import common
from . import item
from . import item_model
from . import unit
from . import reward
from .. import data
from .. import db
from .. import idol
from .. import util
from ..db import achievement
from ..db import main

from typing import Callable, Protocol

ACHIEVEMENT_REWARD_DEFAULT = [item.base_loveca(1)]


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
    reward_list: list[common.AnyItem]

    @staticmethod
    def from_sqlalchemy(ach: main.Achievement, info: achievement.Achievement, rewards: list[item_model.Item]):
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
            accomplish_id=str(ach.id) if ach.is_accomplished and (not ach.is_reward_claimed) else "",
            reward_list=rewards,
        )


class AchievementMixin(pydantic.BaseModel):
    accomplished_achievement_list: list[AchievementData]
    unaccomplished_achievement_cnt: int
    added_achievement_list: list[AchievementData]
    new_achievement_cnt: int


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


@common.context_cacheable("achievement")
async def get_achievement_info(context: idol.BasicSchoolIdolContext, achievement_id: int):
    info = await db.get_decrypted_row(context.db.achievement, achievement.Achievement, achievement_id)
    if info is None:
        raise ValueError("invalid achievement")

    return info


@common.context_cacheable("achievement_story")
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
        end_date=0 if ach.end_date is None else util.datetime_to_timestamp(ach.end_date),
        is_new=True,
    )
    context.db.main.add(user_ach)
    await context.db.main.flush()
    return user_ach


async def to_game_representation(
    context: idol.BasicSchoolIdolContext, achs: list[main.Achievement], rewardss: list[list[item_model.Item]]
):
    return [
        AchievementData.from_sqlalchemy(ach, await get_achievement_info(context, ach.achievement_id), rewards)
        for ach, rewards in zip(achs, rewardss)
    ]


async def get_achievement_rewards(context: idol.BasicSchoolIdolContext, ach: main.Achievement | int, /):
    if isinstance(ach, main.Achievement):
        ach_id = ach.achievement_id
    else:
        ach_id = ach

    server_data = data.get()
    old_reward_data = server_data.achievement_reward.get(ach_id, ACHIEVEMENT_REWARD_DEFAULT)
    return [await advanced.deserialize_item_data(context, i) for i in old_reward_data]


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


async def get_achievement(context: idol.BasicSchoolIdolContext, /, user: main.User, ach_id: int):
    ach = await context.db.main.get(main.Achievement, ach_id)
    if ach is None or ach.user_id != user.id:
        raise idol.error.IdolError(detail=f"invalid achievement id {ach_id}")

    return ach


async def get_achievements(context: idol.BasicSchoolIdolContext, user: main.User, accomplished: bool | None = None):
    if accomplished is not None:
        q = sqlalchemy.select(main.Achievement).where(
            main.Achievement.user_id == user.id, main.Achievement.is_accomplished == accomplished
        )
    else:
        q = sqlalchemy.select(main.Achievement).where(main.Achievement.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def get_unclaimed_achievements(
    context: idol.BasicSchoolIdolContext, /, user: main.User, accomplished_but_unclaimed_only: bool = False
):
    q = sqlalchemy.select(main.Achievement).where(main.Achievement.user_id == user.id)

    if accomplished_but_unclaimed_only:
        q = q.where(main.Achievement.is_accomplished == True, main.Achievement.is_reward_claimed == False)
    else:
        q = q.where((main.Achievement.is_accomplished == False) | (main.Achievement.is_reward_claimed == False))
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


async def get_accomplished_achievements_by_filter_id(
    context: idol.BasicSchoolIdolContext, user: main.User, achievement_filter_category_id: int
):
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        main.Achievement.achievement_filter_category_id == achievement_filter_category_id,
        main.Achievement.is_accomplished == True,
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


async def test_params(ach_info: achievement.Achievement, args: collections.abc.Sequence[int | None]):
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
    test: Callable[
        [achievement.Achievement, collections.abc.Sequence[int | None]], collections.abc.Awaitable[bool]
    ] = test_params,
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

        if await test(ach_info, args):
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
    test: Callable[
        [achievement.Achievement, collections.abc.Sequence[int | None]], collections.abc.Awaitable[bool]
    ] = test_params,
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

        if await test(ach_info, args):
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


class RecursiveAchievementCall[**P](Protocol):
    def __call__(
        self, context: idol.BasicSchoolIdolContext, user: main.User, /, *args: P.args, **kwargs: P.kwargs
    ) -> collections.abc.Awaitable[AchievementContext]: ...


def recursive_achievement(achievement_type: int, /):
    def wrapper0[**P](func: RecursiveAchievementCall[P]):
        async def wrapper1(
            context: idol.BasicSchoolIdolContext, user: main.User, /, *args: P.args, **kwargs: P.kwargs
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


async def check_type_1(context: idol.BasicSchoolIdolContext, user: main.User, /, increment: bool):
    """
    Check live show clear achievements.
    """
    return await check_type_increment(context, user, 1, increment)


async def check_type_2(context: idol.BasicSchoolIdolContext, user: main.User, /, difficulty: int, increment: bool):
    """
    Check live show clear achievements by specified difficulty.
    """
    return await check_type_increment(context, user, 2, increment, 2, difficulty)


async def check_type_3(context: idol.BasicSchoolIdolContext, user: main.User, /, rank: int, increment: bool):
    """
    Check live show clear achievements by specified score rank.
    """
    return await check_type_increment(context, user, 3, increment, 2, rank)


async def check_type_4(context: idol.BasicSchoolIdolContext, user: main.User, /, rank: int, increment: bool):
    """
    Check live show clear achievements by specified combo rank.
    """
    return await check_type_increment(context, user, 4, increment, 2, rank)


async def check_type_7(context: idol.BasicSchoolIdolContext, user: main.User, /, unit_type_id: int, increment: bool):
    """
    Check live show clear achievements by specified combo rank.
    """
    return await check_type_increment(context, user, 4, increment, 2, unit_type_id)


@recursive_achievement(18)
async def check_type_18(context: idol.BasicSchoolIdolContext, user: main.User, /, club_members: int):
    """
    Check amount of club members collected.
    """
    return await check_type_countable(context, user, 18, club_members)


@recursive_achievement(19)
async def check_type_19(context: idol.BasicSchoolIdolContext, user: main.User, /, idolized: int):
    """
    Check amount of idolized club members.
    """
    return await check_type_countable(context, user, 19, idolized)


@recursive_achievement(20)
async def check_type_20(context: idol.BasicSchoolIdolContext, user: main.User, /, max_love: int):
    """
    Check amount of max bonded idolized club members.
    """
    return await check_type_countable(context, user, 20, max_love)


@recursive_achievement(21)
async def check_type_21(context: idol.BasicSchoolIdolContext, user: main.User, /, max_level: int):
    """
    Check amount of max leveled idolized club members.
    """
    return await check_type_countable(context, user, 21, max_level)


async def check_type_23(context: idol.BasicSchoolIdolContext, user: main.User, /, scenario_id: int):
    """
    Check main story clear.
    """

    # Note, there's no "count" in scenario but the database requires it, so specify unused parameter index (e.g. 2)
    return await check_type_countable(context, user, 23, 1, 2, scenario_id)


async def check_type_27(context: idol.BasicSchoolIdolContext, user: main.User, /, nlogins: int):
    """
    Check login bonus count
    """
    return await check_type_countable(context, user, 27, nlogins)


async def check_type_29(context: idol.BasicSchoolIdolContext, user: main.User, /):
    """
    Check one-time login bonus.
    """
    return await check_type_countable(context, user, 29, 1)


@recursive_achievement(30)
async def check_type_30(context: idol.BasicSchoolIdolContext, user: main.User, /, rank: int | None = None):
    """
    Check player rank.
    """
    return await check_type_countable(context, user, 30, user.level if rank is None else rank)


@recursive_achievement(32)
async def check_type_32(context: idol.BasicSchoolIdolContext, user: main.User, /, live_track_id: int):
    """
    Check live show clear of specific `live_track_id`
    """

    # Note, there's no "count" in here but the database requires it, so specify unused parameter index (e.g. 2)
    return await check_type_countable(context, user, 32, 1, 2, live_track_id)


async def check_type_37(context: idol.BasicSchoolIdolContext, user: main.User, /, live_track_id: int, increment: bool):
    """
    Check live show clear of specific `live_track_id`
    """

    # Note, there's no "count" in here but the database requires it, so specify unused parameter index (e.g. 2)
    return await check_type_increment(context, user, 37, increment, 2, live_track_id)


class _Type50Checker:
    def __init__(self, context: idol.BasicSchoolIdolContext, user: main.User, unit_deck: list[int], /):
        self.context = context
        self.user = user
        self.unit_deck = unit_deck
        self.achievement_groups: list[set[int]] = []

    async def init(self):
        if len(self.achievement_groups) == 0:
            previous_unit_set: dict[int, set[int]] = {}

            for unit_id in self.unit_deck:
                if unit_id in previous_unit_set:
                    self.achievement_groups.append(previous_unit_set[unit_id])
                else:
                    # Perform query on unit type
                    unit_info = await unit.get_unit_info(self.context, unit_id)
                    result: set[int] = set()
                    if unit_info is not None:
                        q = sqlalchemy.select(achievement.UnitTypeGroup.achievement_unit_type_group_id).where(
                            achievement.UnitTypeGroup.unit_type_id == unit_info.unit_type_id
                        )
                        r = await self.context.db.achievement.execute(q)
                        result.update(r.scalars())

                    previous_unit_set[unit_id] = result
                    self.achievement_groups.append(result)

    async def all(self, achievement_unit_type_group_id: int):
        await self.init()
        for group_id in self.achievement_groups:
            if achievement_unit_type_group_id not in group_id:
                return False

        return True

    async def any(self, achievement_unit_type_group_id: int):
        await self.init()
        for group_id in self.achievement_groups:
            if achievement_unit_type_group_id in group_id:
                return True

        return False

    async def __call__(self, ach_info: achievement.Achievement, args: collections.abc.Sequence[int | None]):
        if (
            ach_info.params8 is not None
            and (ach_info.params1 is None or ach_info.params1 == args[0])
            and (ach_info.params6 is None or ach_info.params6 == args[1])
        ):
            match ach_info.params9:
                case 1:
                    return await self.all(ach_info.params8)
                case 2:
                    return await self.any(ach_info.params8)
        return False


async def check_type_50(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    /,
    live_track_id: int,
    combo_rank: int,
    unit_deck: list[int],
    increment: bool,
):
    """
    Check live show clear where all or one of the deck are in specific group.
    """

    return await check_type_increment(
        context, user, 50, increment, 10, live_track_id, combo_rank, test=_Type50Checker(context, user, unit_deck)
    )


async def check_type_53_old(context: idol.BasicSchoolIdolContext, user: main.User, /):
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
    context: idol.BasicSchoolIdolContext, user: main.User, /, achievement_category_id: int, count: int
):
    """
    Check amount of achievement cleared with specific category
    """
    return await check_type_countable(context, user, 53, count, 2, achievement_category_id)


async def check_type_53_recursive(context: idol.BasicSchoolIdolContext, user: main.User, /):
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


async def check_type_57(context: idol.BasicSchoolIdolContext, user: main.User, /, completed_scenario_count: int):
    """
    Check amount of cleared main stories.
    """

    return await check_type_countable(context, user, 57, completed_scenario_count)


async def check_type_58(context: idol.BasicSchoolIdolContext, user: main.User, /, increment: bool):
    """
    Check live show clear achievements.
    """
    return await check_type_increment(context, user, 58, increment)


async def check_type_59(context: idol.BasicSchoolIdolContext, user: main.User, /, unlocked_scenario_count: int):
    """
    Check amount of unlocked main stories.
    """

    return await check_type_countable(context, user, 59, unlocked_scenario_count)


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
    result = await context.db.main.execute(q)
    all_accomplished = list(result.scalars())

    q = (
        sqlalchemy.select(achievement.Tag)
        .where(achievement.Tag.achievement_id.in_(all_accomplished))
        .group_by(achievement.Tag.achievement_category_id)
        .with_only_columns(
            achievement.Tag.achievement_category_id, sqlalchemy.func.count(achievement.Tag.achievement_id.distinct())
        )
    )
    result = await context.db.achievement.execute(q)
    return [(int(r[0]), int(r[1])) for r in result]


async def give_achievement_reward(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    ach_info: achievement.Achievement,
    rewards: list[item_model.Item],
):
    for r in rewards:
        # TODO: Proper message for reward insertion
        if r.reward_box_flag:
            await reward.add_item(
                context,
                user,
                r,
                ach_info.title or "FIXME",
                ach_info.title_en or ach_info.title or "FIXME EN",
            )
        else:
            add_result = await advanced.add_item(context, user, r)
            if not add_result.success:
                await reward.add_item(
                    context,
                    user,
                    r,
                    ach_info.title or "FIXME",
                    ach_info.title_en or ach_info.title or "FIXME EN",
                )


async def process_achievement_reward(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    achievements: list[main.Achievement],
    rewardss: list[list[item_model.Item]],
):
    for ach, reward_list in zip(achievements, rewardss):
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info is not None and ach_info.auto_reward_flag:
            await give_achievement_reward(context, user, ach_info, reward_list)
            await mark_achievement_reward_claimed(context, ach)
    await context.db.main.flush()
