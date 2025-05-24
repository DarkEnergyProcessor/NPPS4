import math

import pydantic
import sqlalchemy
import sqlalchemy.orm

from . import achievement
from . import award
from . import background
from . import common
from . import core
from . import item
from . import live
from . import scenario
from .. import idol
from .. import util
from ..db import main
from ..db import game_mater
from ..idol import session

from typing import Protocol


class UserInfoData(pydantic.BaseModel):
    user_id: int
    name: str
    level: int
    exp: int
    previous_exp: int
    next_exp: int
    game_coin: int
    sns_coin: int
    free_sns_coin: int
    paid_sns_coin: int
    social_point: int
    unit_max: int
    waiting_unit_max: int
    current_energy: int | None = None
    energy_max: int
    energy_full_time: str
    license_live_energy_recoverly_time: int
    energy_full_need_time: int
    over_max_energy: int
    training_energy: int
    training_energy_max: int
    friend_max: int
    invite_code: str
    insert_date: str
    update_date: str
    tutorial_state: int
    lp_recovery_item: list[common.ItemCount]
    unlock_random_live_muse: int = 0
    unlock_random_live_aqours: int = 0


class NextLevelInfo(pydantic.BaseModel):
    level: int
    from_exp: int


class UserDiffMixin(pydantic.BaseModel):
    before_user_info: UserInfoData
    after_user_info: UserInfoData


async def get(context: idol.BasicSchoolIdolContext, id: int | None = None):
    return await context.db.main.get(main.User, id)


async def get_current(context: idol.SchoolIdolUserParams):
    if context.token is None:
        raise ValueError("logic error, token is None")

    result = await context.db.main.get(main.User, context.token.user_id)
    if result is None:
        raise ValueError("logic error, user is None")

    context.add_task(session.try_cleanup_tokens)

    if result.locked:
        raise idol.error.locked()

    return result


async def get_from_token(context: idol.BasicSchoolIdolContext, token: str, /):
    detoken = await session.decapsulate_token(context, token)
    if detoken is not None:
        return await context.db.main.get(main.User, detoken.user_id)
    return None


async def get_user_info(context: idol.BasicSchoolIdolContext, user: main.User):
    return UserInfoData(
        user_id=user.id,
        name=user.name,
        level=user.level,
        exp=user.exp,
        previous_exp=core.get_next_exp_cumulative(user.level - 1),
        next_exp=core.get_next_exp_cumulative(user.level),
        game_coin=user.game_coin,
        sns_coin=user.free_sns_coin + user.paid_sns_coin,
        free_sns_coin=user.free_sns_coin,
        paid_sns_coin=user.paid_sns_coin,
        social_point=user.social_point,
        unit_max=user.unit_max,
        waiting_unit_max=user.waiting_unit_max,
        current_energy=get_current_energy(user),
        energy_max=user.energy_max,
        energy_full_time=util.timestamp_to_datetime(user.energy_full_time),
        license_live_energy_recoverly_time=user.license_live_energy_recoverly_time,
        energy_full_need_time=(user.over_max_energy == 0) * max(user.energy_full_time - util.time(), 0),
        over_max_energy=user.over_max_energy,
        training_energy=user.training_energy,
        training_energy_max=user.training_energy_max,
        friend_max=user.friend_max,
        invite_code=user.invite_code,
        insert_date=util.timestamp_to_datetime(user.insert_date),
        update_date=util.timestamp_to_datetime(user.update_date),
        tutorial_state=user.tutorial_state,
        lp_recovery_item=await item.get_recovery_items(context, user),
    )


async def create(context: idol.BasicSchoolIdolContext, key: str | None, passwd: str | None):
    user = main.User(key=key)
    if passwd is not None:
        user.set_passwd(passwd)
    context.db.main.add(user)
    await context.db.main.flush()
    user.invite_code = f"{core.get_invite_code(user.id):09d}"
    await achievement.init(context, user)
    await background.init(context, user)
    await award.init(context, user)
    await live.init(context, user)
    await scenario.init(context, user)
    await context.db.main.flush()
    return user


async def find_by_key(context: idol.BasicSchoolIdolContext, key: str):
    q = sqlalchemy.select(main.User).where(main.User.key == key).limit(1)
    result = await context.db.main.execute(q)
    return result.scalar()


async def find_by_invite_code(context: idol.BasicSchoolIdolContext, invite_code: int):
    q = sqlalchemy.select(main.User).where(main.User.invite_code == invite_code).limit(1)
    result = await context.db.main.execute(q)
    return result.scalar()


def get_current_energy(user: main.User, t: int | None = None):
    if t is None:
        t = util.time()
    difftime = max(user.energy_full_time - t, 0)
    used_lp = math.ceil(difftime / game_mater.GAME_SETTING.live_energy_recoverly_time)
    return max(user.energy_max - used_lp, 0) + max(user.over_max_energy - user.energy_max, 0)


def has_energy(user: main.User, energy: int, /, t: int | None = None):
    return get_current_energy(user, t=t) >= energy


def add_energy(user: main.User, /, amount: int, *, t: int | None = None, overflow: bool = True):
    if amount < 0:
        raise ValueError("to subtract use sub_energy")

    if t is None:
        t = util.time()

    before = get_current_energy(user, t)
    sub_time = amount * game_mater.GAME_SETTING.live_energy_recoverly_time
    user.energy_full_time = max(user.energy_full_time - sub_time, t)

    if overflow:
        current_energy = get_current_energy(user, t)
        amount = amount - (current_energy - before)
        if amount > 0:
            user.over_max_energy = max(user.over_max_energy, user.energy_max) + amount
        else:
            user.over_max_energy = 0


def sub_energy(user: main.User, /, amount: int, *, t: int | None = None):
    if amount < 0:
        raise ValueError("to add use add_energy")

    if t is None:
        t = util.time()

    current_energy = get_current_energy(user, t)
    overflow_energy = 0
    if user.over_max_energy > 0:
        overflow_energy = user.over_max_energy - user.energy_max
        current_energy = user.energy_max

    # Is overflow LP >= LP?
    if overflow_energy >= amount:
        user.over_max_energy = user.over_max_energy - amount
        return
    elif overflow_energy == amount:  # Need to handle this special case
        user.over_max_energy = 0
        return

    # Overflow LP < LP.
    consume_normal_energy = amount - overflow_energy
    if current_energy >= consume_normal_energy:
        user.energy_full_time = (
            max(user.energy_full_time, t) + game_mater.GAME_SETTING.live_energy_recoverly_time * consume_normal_energy
        )
        user.over_max_energy = 0
        return

    raise ValueError("not enough energy")


def add_energy_percentage(
    user: main.User, /, percentage: float, ntimes: int = 1, *, t: int | None = None, overflow: bool = True
):
    if percentage < 0.0 or percentage > 1.0:
        raise ValueError("percentage out of range")
    if t is None:
        t = util.time()

    energy_to_add = math.ceil(user.energy_max * percentage) * ntimes
    add_energy(user, energy_to_add, t=t, overflow=overflow)


async def add_exp(context: idol.BasicSchoolIdolContext, user: main.User, exp: int):
    next_exp = core.get_next_exp_cumulative(user.level)
    level_up = False
    max_energy = 0
    next_level_info = [NextLevelInfo(level=user.level, from_exp=user.exp)]
    t = util.time()

    user.exp = user.exp + exp
    while user.exp >= next_exp:
        level_up = True
        user.level = user.level + 1
        next_level_info.append(NextLevelInfo(level=user.level, from_exp=next_exp))
        next_exp = core.get_next_exp_cumulative(user.level)
        max_energy = core.get_energy_by_rank(user.level)
        # Try to increase max LP. Do it here so add_energy below consider it into account.
        user.energy_max = max_energy
        add_energy(user, max_energy, t=t)

    if level_up:
        # Increase max friend
        user.friend_max = core.get_max_friend_by_rank(user.level)
        # Increase master ticket
        user.training_energy_max = core.get_training_energy_by_rank(user.level)

    await context.db.main.flush()
    return next_level_info


def get_loveca(user: main.User, /, *, include_free: bool = True, include_paid: bool = True):
    return user.free_sns_coin * include_free + user.paid_sns_coin * include_paid


def sub_loveca(user: main.User, /, amount: int, *, sub_paid_only: bool = False):
    if sub_paid_only:
        if user.paid_sns_coin < amount:
            return False

        user.paid_sns_coin = user.paid_sns_coin - amount
        return True
    else:
        if get_loveca(user) < amount:
            return False

        amount1 = min(user.free_sns_coin, amount)
        amount2 = amount - amount1
        user.free_sns_coin = user.free_sns_coin - amount1
        user.paid_sns_coin = user.paid_sns_coin - amount2
        return True


class CleanupProtocol(Protocol):
    user_id: sqlalchemy.orm.Mapped[int]


async def _clean_table[T: CleanupProtocol](context: idol.BasicSchoolIdolContext, cls: type[T], user_id: int, /):
    q = sqlalchemy.delete(cls).where(cls.user_id == user_id)
    await context.db.main.execute(q)


async def delete_user(context: idol.BasicSchoolIdolContext, user_id: int):
    user_data = await get(context, user_id)
    if user_data is None:
        raise ValueError("User doesn't exist")
    await _clean_table(context, main.NormalLiveUnlock, user_id)
    await _clean_table(context, main.LocalSerialCodeUsage, user_id)
    await _clean_table(context, main.ExchangePointItem, user_id)
    await _clean_table(context, main.RecoveryItem, user_id)
    await _clean_table(context, main.Item, user_id)
    await _clean_table(context, main.LiveInProgress, user_id)
    await _clean_table(context, main.UnitRemovableSkill, user_id)
    await _clean_table(context, main.RemovableSkillInfo, user_id)
    await _clean_table(context, main.MuseumUnlock, user_id)
    await _clean_table(context, main.LiveClear, user_id)
    await _clean_table(context, main.SubScenario, user_id)
    await _clean_table(context, main.Scenario, user_id)
    await _clean_table(context, main.Incentive, user_id)
    await _clean_table(context, main.LoginBonus, user_id)
    await _clean_table(context, main.Achievement, user_id)
    await _clean_table(context, main.Album, user_id)
    await _clean_table(context, main.UnitSupporter, user_id)
    await _clean_table(context, main.UnitDeck, user_id)
    await _clean_table(context, main.TOSAgree, user_id)
    await _clean_table(context, main.Award, user_id)
    await _clean_table(context, main.Background, user_id)
    await _clean_table(context, main.RequestCache, user_id)

    # Delete session
    q = sqlalchemy.delete(main.Session).where(main.Session.user_id == user_id)
    await context.db.main.execute(q)

    # Perform failsafe on party_user_id
    q = (
        sqlalchemy.update(main.LiveInProgress)
        .where(main.LiveInProgress.party_user_id == user_id)
        .values(party_user_id=main.LiveInProgress.user_id)
    )
    await context.db.main.execute(q)

    await _clean_table(context, main.Unit, user_id)

    # Delete user
    await context.db.main.delete(user_data)
    await context.db.main.flush()
