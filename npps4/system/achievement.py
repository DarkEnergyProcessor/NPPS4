import abc
import collections.abc
import dataclasses
import typing

import pydantic
import sqlalchemy

from . import advanced
from . import common
from . import item
from . import item_model
from . import unit
from . import reward
from .. import const
from .. import data
from .. import db
from .. import idol
from .. import util
from ..db import achievement
from ..db import main

from typing import Any, Callable, Protocol

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


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateLiveClear:
    """Instantiate this to perform checks on achievement with "Live Clear" trigger."""

    live_track_id: int
    difficulty: int
    score_rank: int
    combo_rank: int
    team_unit_ids: tuple[int, int, int, int, int, int, int, int, int]
    team_unit_type_ids: tuple[int, int, int, int, int, int, int, int, int]


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateSecretbox:
    """Instantiate this to perform checks on achievement with "Scouting" trigger."""

    secretbox_id: int
    amount: int


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateNewUnit:
    """Instantiate this to perform checks on achievement with "New Unique Unit" trigger."""

    value: int
    """Total amount"""


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateUnitRankUp:
    """Instantiate this to perform checks on achievement with "Idolize" trigger."""

    value: int
    """Total amount"""


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateUnitMaxLevel:
    """Instantiate this to perform checks on achievement with "Max Level" trigger."""

    value: int
    """Total amount"""


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateUnitMaxLove:
    """Instantiate this to perform checks on achievement with "Max Bond" trigger."""

    value: int
    """Total amount"""


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateLevelUp:
    """Instantiate this to perform checks on achievement with "Level Up" trigger."""

    rank: int
    """Current player rank"""


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateLoginBonus:
    """Instantiate this to perform checks on achievement with "Login Bonus" trigger."""

    login_days: int
    """Total days logged in"""


@dataclasses.dataclass(kw_only=True)
class AchievementUpdateUnitMerge:
    """Instantiate this to perform checks on achievement with "Practice" trigger."""

    unit_owning_user_id: int
    skill_level: int


class AchievementUpdateFinishScenario:
    """Instantiate this to perform checks on achievement with "Clearing Main Story" trigger."""

    scenario_id: int
    """Main story ID"""


class AchievementUpdateItemCollect:
    """Instantiate this to perform checks on achievement with "Got Item" trigger."""

    add_type: const.ADD_TYPE
    item_id: int
    amount: int


class AchievementUpdateAnywhere:
    """Instantiate this to perform achievement checks anywhere."""

    pass


class AchievementChecker[T](abc.ABC):
    @abc.abstractmethod
    async def test_param(
        self, context: idol.BasicSchoolIdolContext, data: T, achievement_info: achievement.Achievement
    ) -> bool: ...

    async def update(
        self, context: idol.BasicSchoolIdolContext, oldvalue: int, data: T, achievement_info: achievement.Achievement
    ) -> int:
        return oldvalue + 1

    @abc.abstractmethod
    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool: ...

    @property
    def recursive(self) -> bool:
        return False


ACHIEVEMENT_CHECKER: dict[type, dict[int, AchievementChecker[Any]]] = {}


def register_achievement_checker(achievement_id: int):
    def wrap0[T: AchievementChecker[Any]](cls: type[T]):
        achtestinfo = ACHIEVEMENT_CHECKER.setdefault(cls, {})
        inst = cls()
        achtestinfo[achievement_id] = inst
        return cls

    return wrap0


@register_achievement_checker(1)
class CheckLiveClear(AchievementChecker[AchievementUpdateLiveClear]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLiveClear,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1


@register_achievement_checker(2)
class CheckLiveClearWithDifficulty(AchievementChecker[AchievementUpdateLiveClear]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLiveClear,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None and data.difficulty == achievement_info.params1

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params2 is not None
        return value >= achievement_info.params2


@register_achievement_checker(3)
class CheckLiveClearWithScoreRank(AchievementChecker[AchievementUpdateLiveClear]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLiveClear,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None and data.score_rank <= achievement_info.params1

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params2 is not None
        return value >= achievement_info.params2


@register_achievement_checker(4)
class CheckLiveClearWithComboRank(AchievementChecker[AchievementUpdateLiveClear]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLiveClear,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None and data.combo_rank <= achievement_info.params1

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params2 is not None
        return value >= achievement_info.params2


@register_achievement_checker(7)
class CheckLiveClearWithUnitType(AchievementChecker[AchievementUpdateLiveClear]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLiveClear,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None and achievement_info.params1 in data.team_unit_type_ids

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params2 is not None
        return value >= achievement_info.params2


@register_achievement_checker(9)
class CheckLiveClearWithTrackAndUnitGroup(AchievementChecker[AchievementUpdateLiveClear]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLiveClear,
        achievement_info: achievement.Achievement,
    ) -> bool:
        if achievement_info.params1 is None or achievement_info.params2 is None or achievement_info.params3 is None:
            return False

        unit_type_groups = await get_unit_type_groups(context, achievement_info.params3)
        return achievement_info.params1 is not None and achievement_info.params1 in data.team_unit_type_ids

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params3 is not None
        return value >= achievement_info.params3


@register_achievement_checker(10)
class CheckGachaPon(AchievementChecker[AchievementUpdateSecretbox]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateSecretbox,
        achievement_info: achievement.Achievement,
    ) -> bool:
        if achievement_info.params1 is None or achievement_info.params3 is None:
            return False

        # TODO: Perform aliased secretbox ID check in here.
        return achievement_info.params1 == data.secretbox_id

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateSecretbox,
        achievement_info: achievement.Achievement,
    ) -> int:
        return oldvalue + data.amount

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params3 is not None
        return value >= achievement_info.params3

    @property
    def recursive(self):
        return True


@register_achievement_checker(11)
class CheckUnitMerge(AchievementChecker[AchievementUpdateUnitMerge]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateUnitMerge,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1

    @property
    def recursive(self):
        return True


@register_achievement_checker(13)
class CheckUnitSkillUp(AchievementChecker[AchievementUpdateUnitMerge]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateUnitMerge,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateUnitMerge,
        achievement_info: achievement.Achievement,
    ) -> int:
        return data.skill_level

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1

    @property
    def recursive(self):
        return True


@register_achievement_checker(18)
class CheckCollectUniqueUnit(AchievementChecker[AchievementUpdateNewUnit]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateNewUnit,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateNewUnit,
        achievement_info: achievement.Achievement,
    ) -> int:
        return data.value

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1

    @property
    def recursive(self):
        return True


@register_achievement_checker(19)
class CheckRankUpUniqueUnit(AchievementChecker[AchievementUpdateUnitRankUp]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateUnitRankUp,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateUnitRankUp,
        achievement_info: achievement.Achievement,
    ) -> int:
        return data.value

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1

    @property
    def recursive(self):
        return True


@register_achievement_checker(20)
class CheckMaxLoveUnit(AchievementChecker[AchievementUpdateUnitMaxLove]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateUnitMaxLove,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateUnitMaxLove,
        achievement_info: achievement.Achievement,
    ) -> int:
        return data.value

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1

    @property
    def recursive(self):
        return True


@register_achievement_checker(21)
class CheckMaxLevelUnit(AchievementChecker[AchievementUpdateUnitMaxLevel]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateUnitMaxLevel,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateUnitMaxLevel,
        achievement_info: achievement.Achievement,
    ) -> int:
        return data.value

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1

    @property
    def recursive(self):
        return True


@register_achievement_checker(23)
class CheckFinishScenario(AchievementChecker[AchievementUpdateFinishScenario]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateFinishScenario,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None and achievement_info.params1 == data.scenario_id

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        return value > 0


@register_achievement_checker(26)
class CheckFriendCount(AchievementChecker[AchievementUpdateAnywhere]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateAnywhere,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateAnywhere,
        achievement_info: achievement.Achievement,
    ) -> int:
        return oldvalue

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        # TODO: query friend count
        return False


@register_achievement_checker(27)
class CheckLogin(AchievementChecker[AchievementUpdateLoginBonus]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLoginBonus,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1


@register_achievement_checker(29)
class CheckLoginSingle(AchievementChecker[AchievementUpdateLoginBonus]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLoginBonus,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return True

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        return value > 0


@register_achievement_checker(30)
class CheckPlayerRankUp(AchievementChecker[AchievementUpdateLevelUp]):
    async def test_param(
        self,
        context: idol.BasicSchoolIdolContext,
        data: AchievementUpdateLevelUp,
        achievement_info: achievement.Achievement,
    ) -> bool:
        return achievement_info.params1 is not None

    async def update(
        self,
        context: idol.BasicSchoolIdolContext,
        oldvalue: int,
        data: AchievementUpdateLevelUp,
        achievement_info: achievement.Achievement,
    ) -> int:
        return data.rank

    async def is_accomplished(
        self, context: idol.BasicSchoolIdolContext, value: int, achievement_info: achievement.Achievement
    ) -> bool:
        assert achievement_info.params1 is not None
        return value >= achievement_info.params1


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


@common.context_cacheable("achievement_unit_type_group")
async def get_unit_type_groups(context, achievement_unit_type_group_id: int):
    q = sqlalchemy.select(achievement.UnitTypeGroup).where(
        achievement.UnitTypeGroup.achievement_unit_type_group_id == achievement_unit_type_group_id
    )


async def add_achievement(
    context: idol.BasicSchoolIdolContext, user: main.User, ach: achievement.Achievement, time: int | None = None
):
    if time is None:
        time = util.time()

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
        reset_type=ach.reset_type,
    )
    context.db.main.add(user_ach)
    await context.db.main.flush()
    return user_ach


async def has_achievement(context: idol.BasicSchoolIdolContext, user: main.User, /, achievement_id: int):
    q = sqlalchemy.select(main.Achievement.achievement_id).where(
        main.Achievement.achievement_id == achievement_id, main.Achievement.user_id == user.id
    )
    result = await context.db.main.execute(q)
    return result.scalar() is not None


async def update_resettable_achievement(
    context: idol.BasicSchoolIdolContext, user: main.User, ts: int | None = None, /
):
    if ts is None:
        ts = util.time()

    if context.get_cache(f"update_resettable_achievement_{ts}", user.id) is not None:
        return

    modified = False
    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        main.Achievement.reset_type > 0,
        sqlalchemy.or_(
            sqlalchemy.and_(
                main.Achievement.reset_type == 1, main.Achievement.reset_value != util.get_days_since_unix(ts)
            ),
            sqlalchemy.and_(
                main.Achievement.reset_type == 2, main.Achievement.reset_value != util.get_weeks_since_unix(ts)
            ),
        ),
    )
    result = await context.db.main.execute(q)

    for ach_data in result.scalars():
        ach_info = await context.db.achievement.get(achievement.Achievement, ach_data.achievement_id)

        if ach_info is None or (not ach_info.default_open_flag):
            await context.db.main.delete(ach_data)
        else:
            ach_data.is_accomplished = False
            ach_data.is_reward_claimed = False
            ach_data.count = 0

        modified = True

    if modified:
        await context.db.main.flush()

    context.set_cache(f"update_resettable_achievement_{ts}", user.id, True)


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


async def get_achievements(
    context: idol.BasicSchoolIdolContext, user: main.User, accomplished: bool | None = None
) -> collections.abc.Iterable[main.Achievement]:
    await update_resettable_achievement(context, user)

    q = sqlalchemy.select(main.Achievement).where(main.Achievement.user_id == user.id)
    if accomplished is not None:
        q = q.where(main.Achievement.is_accomplished == accomplished)

    result = await context.db.main.execute(q)
    return result.scalars()


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
    time = util.time()
    await update_resettable_achievement(context, user, time)

    q = sqlalchemy.select(main.Achievement).where(
        main.Achievement.user_id == user.id,
        main.Achievement.achievement_type == achievement_type,
        main.Achievement.is_accomplished == False,
    )
    result = await context.db.main.execute(q)

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

                # Update reset value
                match ach.reset_type:
                    case 1:
                        ach.reset_value = util.get_days_since_unix(time)
                    case 2:
                        ach.reset_value = util.get_weeks_since_unix(time)

                # New achievement
                for next_ach_id in await get_next_achievement_ids(context, ach.achievement_id):
                    new_ach_info = await get_achievement_info(context, next_ach_id)
                    if new_ach_info is not None and not await has_achievement(
                        context, user, new_ach_info.achievement_id
                    ):
                        new_ach = await add_achievement(context, user, new_ach_info, time)
                        # Append to new achievement
                        new.append(new_ach)
            else:
                ach.count = count

            await context.db.main.flush()

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

                # Update reset value
                match ach.reset_type:
                    case 1:
                        ach.reset_value = util.get_days_since_unix(time)
                    case 2:
                        ach.reset_value = util.get_weeks_since_unix(time)

                # New achievement
                for next_ach_id in await get_next_achievement_ids(context, ach.achievement_id):
                    new_ach_info = await get_achievement_info(context, next_ach_id)
                    if new_ach_info is not None and not await has_achievement(
                        context, user, new_ach_info.achievement_id
                    ):
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

    async def false(self, achievement_unit_type_group_id: int):
        return False

    async def test_member_type(self, params8: int | None, params9: int | None):
        if params8 is None:
            return True
        return await _Type50Checker.comparer.get(params9, _Type50Checker.false)(self, params8)

    async def __call__(self, ach_info: achievement.Achievement, args: collections.abc.Sequence[int | None]):
        # args:
        # 0. live_track_id
        # 1. difficulty
        # 2. attribute_id
        # 3. score_rank
        # 4. combo_rank

        args = util.ensure_no_none(args)

        return (
            (ach_info.params1 is None or ach_info.params1 == args[0])
            and (ach_info.params2 is None or ach_info.params2 == args[1])
            and (ach_info.params3 is None or ach_info.params3 == args[2])
            and ach_info.params4 is None  # TODO
            and (ach_info.params5 is None or ach_info.params5 >= args[3])
            and (ach_info.params6 is None or ach_info.params6 >= args[4])
            and (await self.test_member_type(ach_info.params8, ach_info.params9))
        )

    comparer = {None: false, 1: all, 2: any}


async def check_type_50(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    /,
    live_track_id: int,
    difficulty: int,
    attribute: int,
    score_rank: int,
    combo_rank: int,
    unit_deck: list[int],
    increment: bool,
):
    """
    Check live show clear where all or one of the deck are in specific group.
    """

    return await check_type_increment(
        context,
        user,
        50,
        increment,
        10,
        live_track_id,
        difficulty,
        attribute,
        score_rank,
        combo_rank,
        test=_Type50Checker(context, user, unit_deck),
    )


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
    q = sqlalchemy.select(main.Achievement.achievement_id).where(
        main.Achievement.user_id == user.id, main.Achievement.is_accomplished == True
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


BACKGROUND_TITLE_ADD_TYPE = (const.ADD_TYPE.BACKGROUND, const.ADD_TYPE.AWARD)


async def process_achievement_reward(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    achievements: list[main.Achievement],
    rewardss: list[list[item_model.Item]],
):
    for ach, reward_list in zip(achievements, rewardss):
        ach_info = await get_achievement_info(context, ach.achievement_id)
        if ach_info is not None:
            if ach_info.auto_reward_flag:
                await give_achievement_reward(context, user, ach_info, reward_list)
                await mark_achievement_reward_claimed(context, ach)
            else:
                # Backgrounds and titles are always gained, regardless of the auto_reward_flag
                for r in reward_list:
                    if r.add_type in BACKGROUND_TITLE_ADD_TYPE:
                        await advanced.add_item(context, user, r)
    await context.db.main.flush()
