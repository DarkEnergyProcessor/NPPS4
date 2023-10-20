import dataclasses

import pydantic
import sqlalchemy

from . import item
from ... import idol
from ... import util
from ...db import achievement
from ...db import main


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


@dataclasses.dataclass
class AchievementContext:
    accomplished: list[Achievement] = dataclasses.field(default_factory=list)
    new: list[Achievement] = dataclasses.field(default_factory=list)

    def extend(self, other: "AchievementContext"):
        self.accomplished.extend(other.accomplished)
        self.new.extend(other.new)


# TODO: Get achievement present?
_reward_def = item.add_loveca(1)
ACHIEVEMENT_REWARD_DEFAULT = item.Reward(
    add_type=_reward_def.add_type, item_id=_reward_def.item_id, amount=_reward_def.amount, reward_box_flag=True
)


async def get_achievement_info(context: idol.BasicSchoolIdolContext, achievement_id: int):
    ach = await context.db.achievement.get(achievement.Achievement, achievement_id)
    return ach


async def get_next_achievement_id(context: idol.BasicSchoolIdolContext, achievement_id: int):
    ach_story = await context.db.achievement.get(achievement.Story, achievement_id)

    if ach_story is None:
        return None
    else:
        return ach_story.next_achievement_id


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


async def check_type_countable(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    achievement_type: int,
    count: int,
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

        target_amount = ach_info.params1 or 0
        if target_amount >= count:
            # Achieved.
            while target_amount >= count:
                ach.count = min(count, target_amount)
                ach.is_accomplished = True
                achieved.append(
                    Achievement(
                        achievement_id=ach.achievement_id,
                        count=ach.count,
                        is_accomplished=True,
                        insert_date=util.timestamp_to_datetime(ach.insert_date),
                        end_date=None if ach.end_date == 0 else util.timestamp_to_datetime(ach.end_date),
                        remaining_time="",  # FIXME: What to put
                        is_new=ach.is_new,
                        for_display=bool(ach_info.display_flag),
                        is_locked=False,
                        reward_list=[ACHIEVEMENT_REWARD_DEFAULT],  # FIXME: Find achievement data?
                    )
                )

                # New achievement
                next_ach_id = await get_next_achievement_id(context, ach.achievement_id)
                if not next_ach_id:
                    # No more achievements.
                    ach_info = None
                    break

                ach_info = await get_achievement_info(context, next_ach_id)
                if ach_info is None:
                    break

                ach = await add_achievement(context, user, ach_info, time)

            if ach_info is not None:
                new.append(
                    Achievement(
                        achievement_id=ach.achievement_id,
                        count=ach.count,
                        is_accomplished=True,
                        insert_date=util.timestamp_to_datetime(ach.insert_date),
                        end_date=None if ach.end_date == 0 else util.timestamp_to_datetime(ach.end_date),
                        remaining_time="",  # FIXME: What to put
                        is_new=ach.is_new,
                        for_display=bool(ach_info.display_flag),
                        is_locked=False,
                        reward_list=[ACHIEVEMENT_REWARD_DEFAULT],  # FIXME: Find achievement data?
                    )
                )
        else:
            ach.count = count

    return AchievementContext(accomplished=achieved, new=new)


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
