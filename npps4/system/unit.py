import collections.abc
import dataclasses
import itertools
import math

import pydantic
import sqlalchemy

from . import album
from . import common
from . import exchange
from . import item_model
from . import reward
from . import unit_model
from .. import const
from .. import db
from .. import idol
from .. import idoltype
from .. import util
from ..db import main
from ..db import unit

from typing import Literal, cast, overload


@dataclasses.dataclass
class UnitStatsResult:
    level: int
    smile: int
    pure: int
    cool: int
    hp: int
    next_exp: int
    merge_exp: int
    merge_cost: int
    sale_price: int


@dataclasses.dataclass(eq=True, frozen=True, kw_only=True)
class UnitStatsCalculationID:
    unit_id: int
    exp: int
    max_level: int
    level_limit_id: int

    @staticmethod
    def from_unit_data(unit_data: main.Unit, /):
        return UnitStatsCalculationID(
            unit_id=unit_data.unit_id,
            exp=unit_data.exp,
            max_level=unit_data.max_level,
            level_limit_id=unit_data.level_limit_id,
        )


async def count_units(context: idol.BasicSchoolIdolContext, user: main.User, active: bool):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Unit)
        .where(main.Unit.user_id == user.id, main.Unit.active == active)
    )
    result = await context.db.main.execute(q)
    return result.scalar() or 0


async def get_all_units(
    context: idol.BasicSchoolIdolContext, user: main.User, active: bool | None = None
) -> collections.abc.Iterable[main.Unit]:
    q = sqlalchemy.select(main.Unit).where(main.Unit.user_id == user.id)
    if active is not None:
        q = q.where(main.Unit.active == active)

    result = await context.db.main.execute(q)
    return result.scalars()


async def create_unit(
    context: idol.BasicSchoolIdolContext,
    user: main.User | None,
    unit_id: int,
    active: bool,
    *,
    level: int = 1,
    is_signed: bool = False,
):
    unit_info = await get_unit_info(context, unit_id)
    if unit_info is None:
        raise ValueError("invalid unit_id")
    if unit_info.disable_rank_up > 0:
        return None

    rarity = await context.db.unit.get(unit.Rarity, unit_info.rarity)
    if rarity is None:
        raise ValueError("cannot get rarity (is db corrupt?)")

    max_level = rarity.after_level_max if unit_info.rank_min == unit_info.rank_max else rarity.before_level_max

    unit_data = main.Unit(
        user_id=user.id if user is not None else 0,
        unit_id=unit_id,
        active=active,
        favorite_flag=False,
        is_signed=is_signed,
        insert_date=util.time(),
        exp=0,
        skill_exp=0,
        max_level=max_level,
        love=0,
        rank=unit_info.rank_min,
        display_rank=unit_info.rank_min,
        level_limit_id=0,
        unit_removable_skill_capacity=unit_info.default_removable_skill_capacity,
    )

    unit_level_up_pattern = await get_unit_level_up_pattern(context, unit_info.unit_level_up_pattern_id)
    unit_data.exp = get_exp_for_target_level(unit_info, unit_level_up_pattern, level)

    if unit_info.rarity == 4:
        # FIXME: Determine if it's promo card and set to 2 in that case
        unit_data.level_limit_id = 1

    return unit_data


async def add_unit_by_object(context: idol.BasicSchoolIdolContext, user: main.User, unit_data: main.Unit):
    unit_info = await get_unit_info(context, unit_data.unit_id)
    if unit_info is None:
        raise ValueError("unit info not found")

    rarity = await get_unit_rarity(context, unit_info.rarity)
    if rarity is None:
        raise ValueError("unit rarity not found")

    stats = await get_unit_stats_from_unit_data(context, UnitStatsCalculationID.from_unit_data(unit_data))
    context.db.main.add(unit_data)
    await album.update(
        context,
        user,
        unit_data.unit_id,
        rank_max=unit_data.rank >= unit_info.rank_max,
        love_max=unit_data.love >= rarity.after_love_max,
        rank_level_max=stats.level >= rarity.after_level_max,
    )
    await context.db.main.flush()


async def add_unit_simple(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    unit_id: int,
    /,
    active: bool,
    extra_data: unit_model.UnitExtraData = unit_model.UnitExtraData.EMPTY,
):
    unit_item = await create_unit_item(context, unit_id, 1, extra_data)
    if isinstance(unit_item, unit_model.UnitItem):
        unit_data = await create_unit_data(context, user, unit_item, active)
        await add_unit_by_object(context, user, unit_data)
        return unit_data
    else:
        await add_supporter_unit(context, user, unit_id)
        return None


async def get_unit(context: idol.BasicSchoolIdolContext, unit_owning_user_id: int):
    result = await context.db.main.get(main.Unit, unit_owning_user_id)
    if result is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_UNIT_NOT_EXIST)
    return result


def validate_unit(user: main.User, unit_data: main.Unit | None):
    if unit_data is None or unit_data.user_id != user.id:
        raise idol.error.by_code(idol.error.ERROR_CODE_UNIT_NOT_EXIST)


async def get_supporter_unit(context: idol.BasicSchoolIdolContext, user: main.User, unit_id: int, ensure: bool = False):
    unit_info = await get_unit_info(context, unit_id)
    if unit_info is None or unit_info.disable_rank_up == 0:
        return None

    q = (
        sqlalchemy.select(main.UnitSupporter)
        .where(main.UnitSupporter.user_id == user.id, main.UnitSupporter.unit_id == unit_id)
        .limit(1)
    )
    result = await context.db.main.execute(q)
    unitsupp = result.scalar()

    if unitsupp is None and ensure:
        unitsupp = main.UnitSupporter(user_id=user.id, unit_id=unit_id, amount=0)
        context.db.main.add(unitsupp)

    return unitsupp


async def add_supporter_unit(context: idol.BasicSchoolIdolContext, user: main.User, unit_id: int, quantity: int = 1):
    if quantity < 1:
        raise ValueError("invalid amount")

    unitsupp = await get_supporter_unit(context, user, unit_id, True)

    if unitsupp is None:
        return False

    unitsupp.amount = unitsupp.amount + quantity
    await album.update(context, user, unit_id, True, True, True)
    await context.db.main.flush()
    return True


async def sub_supporter_unit(context: idol.BasicSchoolIdolContext, user: main.User, unit_id: int, quantity: int = 1):
    if quantity < 1:
        raise ValueError("invalid amount")

    unitsupp = await get_supporter_unit(context, user, unit_id)

    if unitsupp is not None and unitsupp.amount >= quantity:
        unitsupp.amount = unitsupp.amount - quantity
        await context.db.main.flush()
        return True

    return False


async def get_all_supporter_unit(context: idol.BasicSchoolIdolContext, user: main.User):
    q = (
        sqlalchemy.select(main.UnitSupporter)
        .where(main.UnitSupporter.user_id == user.id)
        .order_by(main.UnitSupporter.unit_id)
    )
    result = await context.db.main.execute(q)
    supporters: list[tuple[int, int]] = []

    for row in result.scalars():
        supporters.append((row.unit_id, row.amount))

    return supporters


async def get_unit_support_list_response(context: idol.BasicSchoolIdolContext, /, user: main.User):
    supp_units = await get_all_supporter_unit(context, user)
    return [unit_model.SupporterInfoResponse(unit_id=supp[0], amount=supp[1]) for supp in supp_units]


@common.context_cacheable("unit")
async def get_unit_info(context: idol.BasicSchoolIdolContext, unit_id: int, /):
    unit_info = await db.get_decrypted_row(context.db.unit, unit.Unit, unit_id)
    if unit_info is None:
        raise ValueError(f"info on unit_id {unit_id} does not exist")
    return unit_info


@common.context_cacheable("unit_rarity")
def get_unit_rarity(context: idol.BasicSchoolIdolContext, rarity: int, /):
    return context.db.unit.get(unit.Rarity, rarity)


@common.context_cacheable("unit_by_number")
async def get_unit_info_from_unit_number(context: idol.BasicSchoolIdolContext, unit_number: int, /):
    q = sqlalchemy.select(unit.Unit).where(unit.Unit.unit_number == unit_number)
    result = await context.db.unit.execute(q)
    unit_info = result.scalar()

    if unit_info is None:
        # Try decrypting all rows
        q = sqlalchemy.select(unit.Unit).where(unit.Unit.unit_number == 0)
        result = await context.db.unit.execute(q)
        for encrypted_unit_info in result.scalars():
            decrypted_unit_info = db.decrypt_row(context.db.unit, encrypted_unit_info)
            if decrypted_unit_info and decrypted_unit_info.unit_number == unit_number:
                unit_info = decrypted_unit_info
                break

    return unit_info


@common.context_cacheable("unit_level_up_pattern")
async def get_unit_level_up_pattern(context: idol.BasicSchoolIdolContext, unit_level_up_pattern_id: int, /):
    q = sqlalchemy.select(unit.UnitLevelUpPattern).where(
        unit.UnitLevelUpPattern.unit_level_up_pattern_id == unit_level_up_pattern_id
    )
    result = await context.db.unit.execute(q)
    return list(result.scalars())


@common.context_cacheable("unit_level_limit_pattern")
async def get_unit_level_limit_pattern(context: idol.BasicSchoolIdolContext, level_limit_id: int, /):
    q = sqlalchemy.select(unit.LevelLimitPattern).where(unit.LevelLimitPattern.unit_level_limit_id == level_limit_id)
    result = await context.db.unit.execute(q)
    return list(result.scalars())


@common.context_cacheable("unit_skill")
async def get_unit_skill(context: idol.BasicSchoolIdolContext, default_unit_skill_id: int | None, /):
    if default_unit_skill_id is None or default_unit_skill_id == 0:
        return None

    return await db.get_decrypted_row(context.db.unit, unit.UnitSkill, default_unit_skill_id)


@common.context_cacheable("unit_skill_level_up_pattern")
async def get_unit_skill_level_up_pattern(context: idol.BasicSchoolIdolContext, unit_skill: int, /):
    q = (
        sqlalchemy.select(unit.UnitSkillLevelUpPattern)
        .where(unit.UnitSkillLevelUpPattern.unit_skill_level_up_pattern_id == unit_skill)
        .order_by(unit.UnitSkillLevelUpPattern.skill_level)
    )
    result = await context.db.unit.execute(q)
    return list(result.scalars())


def detach_from_deck_2(unit_owning_user_id: int, deck: main.UnitDeck):
    has = False
    if deck.unit_owning_user_id_1 == unit_owning_user_id:
        deck.unit_owning_user_id_1 = 0
        has = True
    elif deck.unit_owning_user_id_2 == unit_owning_user_id:
        deck.unit_owning_user_id_2 = 0
        has = True
    elif deck.unit_owning_user_id_3 == unit_owning_user_id:
        deck.unit_owning_user_id_3 = 0
        has = True
    elif deck.unit_owning_user_id_4 == unit_owning_user_id:
        deck.unit_owning_user_id_4 = 0
        has = True
    elif deck.unit_owning_user_id_5 == unit_owning_user_id:
        deck.unit_owning_user_id_5 = 0
        has = True
    elif deck.unit_owning_user_id_6 == unit_owning_user_id:
        deck.unit_owning_user_id_6 = 0
        has = True
    elif deck.unit_owning_user_id_7 == unit_owning_user_id:
        deck.unit_owning_user_id_7 = 0
        has = True
    elif deck.unit_owning_user_id_8 == unit_owning_user_id:
        deck.unit_owning_user_id_8 = 0
        has = True
    elif deck.unit_owning_user_id_9 == unit_owning_user_id:
        deck.unit_owning_user_id_9 = 0
        has = True

    return has


async def detach_from_all_deck(context: idol.SchoolIdolParams, /, user: main.User, unit_data: main.Unit):
    # Remove from deck first
    q = sqlalchemy.select(main.UnitDeck).where(main.UnitDeck.user_id == user.id)
    result = await context.db.main.execute(q)

    for deck in result.scalars():
        if detach_from_deck_2(unit_data.id, deck) and user.active_deck_index == deck.deck_number:
            raise idol.error.by_code(idol.error.ERROR_CODE_IGNORE_MAIN_DECK_UNIT)


async def remove_unit(context: idol.SchoolIdolParams, user: main.User, unit_data: main.Unit):
    validate_unit(user, unit_data)

    if user.center_unit_owning_user_id == unit_data.id:
        raise idol.error.by_code(idol.error.ERROR_CODE_UNIT_NOT_DISPOSE)

    # Remove from deck first
    await detach_from_all_deck(context, user, unit_data)

    # Remove SIS
    unit_sis = await get_unit_removable_skills(context, unit_data)
    for removable_skill_id in unit_sis:
        await detach_unit_removable_skill(context, unit_data, removable_skill_id)

    # Remove from unit
    await context.db.main.delete(unit_data)
    await context.db.main.flush()


# TODO: Move to consts
TEAM_NAMING = {idoltype.Language.en: "Team {0}", idoltype.Language.jp: "ユニット{0}"}


@overload
async def load_unit_deck(
    context: idol.BasicSchoolIdolContext, user: main.User, index: int, ensure: Literal[False] = False
) -> tuple[main.UnitDeck, list[int]] | None: ...


@overload
async def load_unit_deck(
    context: idol.BasicSchoolIdolContext, user: main.User, index: int, ensure: Literal[True]
) -> tuple[main.UnitDeck, list[int]]: ...


VALID_DECK_ID = range(1, 19)


async def load_unit_deck(context: idol.BasicSchoolIdolContext, user: main.User, index: int, ensure: bool = False):
    if index not in VALID_DECK_ID:
        raise ValueError("deck index out of range")

    q = sqlalchemy.select(main.UnitDeck).where(main.UnitDeck.user_id == user.id, main.UnitDeck.deck_number == index)
    result = await context.db.main.execute(q)
    deck = result.scalar()
    deckunits = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    if deck is None:
        if not ensure:
            return None

        deck = main.UnitDeck(user_id=user.id, deck_number=index, name=TEAM_NAMING[context.lang].format(chr(index + 64)))
        context.db.main.add(deck)
        await context.db.main.flush()
    else:
        deckunits[0] = deck.unit_owning_user_id_1
        deckunits[1] = deck.unit_owning_user_id_2
        deckunits[2] = deck.unit_owning_user_id_3
        deckunits[3] = deck.unit_owning_user_id_4
        deckunits[4] = deck.unit_owning_user_id_5
        deckunits[5] = deck.unit_owning_user_id_6
        deckunits[6] = deck.unit_owning_user_id_7
        deckunits[7] = deck.unit_owning_user_id_8
        deckunits[8] = deck.unit_owning_user_id_9

    return deck, deckunits


async def save_unit_deck(
    context: idol.BasicSchoolIdolContext, user: main.User, deck: main.UnitDeck, unit_owning_user_ids: list[int]
):
    if deck.user_id != user.id:
        raise ValueError("invalid deck")

    unique_unit_owning_user_ids: set[int] = set()
    for uid in unit_owning_user_ids:
        if uid > 0:
            if uid in unique_unit_owning_user_ids:
                raise ValueError("unit_owning_user_ids has duplicates")
            else:
                unique_unit_owning_user_ids.add(uid)

    deck.unit_owning_user_id_1 = unit_owning_user_ids[0]
    deck.unit_owning_user_id_2 = unit_owning_user_ids[1]
    deck.unit_owning_user_id_3 = unit_owning_user_ids[2]
    deck.unit_owning_user_id_4 = unit_owning_user_ids[3]
    deck.unit_owning_user_id_5 = unit_owning_user_ids[4]
    deck.unit_owning_user_id_6 = unit_owning_user_ids[5]
    deck.unit_owning_user_id_7 = unit_owning_user_ids[6]
    deck.unit_owning_user_id_8 = unit_owning_user_ids[7]
    deck.unit_owning_user_id_9 = unit_owning_user_ids[8]
    await context.db.main.flush()


async def get_all_deck_simple(
    context: idol.BasicSchoolIdolContext, user: main.User
) -> list[tuple[int, str, tuple[int, int, int, int, int, int, int, int, int]]]:
    q = sqlalchemy.select(main.UnitDeck).where(main.UnitDeck.user_id == user.id)
    result = await context.db.main.execute(q)

    return [
        (
            deck.deck_number,
            deck.name,
            (
                deck.unit_owning_user_id_1,
                deck.unit_owning_user_id_2,
                deck.unit_owning_user_id_3,
                deck.unit_owning_user_id_4,
                deck.unit_owning_user_id_5,
                deck.unit_owning_user_id_6,
                deck.unit_owning_user_id_7,
                deck.unit_owning_user_id_8,
                deck.unit_owning_user_id_9,
            ),
        )
        for deck in result.scalars()
    ]


async def find_all_valid_deck_number_ids(context: idol.SchoolIdolParams, user: main.User):
    result: set[int] = set()

    for i in VALID_DECK_ID:
        deck_data = await load_unit_deck(context, user, i, False)
        if deck_data is not None and all(deck_data[1]):
            result.add(i)

    return result


async def set_unit_center(context: idol.BasicSchoolIdolContext, user: main.User, unit_data: main.Unit):
    validate_unit(user, unit_data)
    user.center_unit_owning_user_id = unit_data.id
    await context.db.main.flush()


async def get_unit_center(
    context: idol.BasicSchoolIdolContext, user: main.User, center_team_instead_of_partner: bool = False
):
    if center_team_instead_of_partner:
        current_deck = await load_unit_deck(context, user, user.active_deck_index, True)
        assert current_deck[1][4] > 0
        return current_deck[1][4]

    return user.center_unit_owning_user_id


async def idolize(context: idol.BasicSchoolIdolContext, user: main.User, unit_data: main.Unit):
    if unit_data.user_id != user.id:
        raise ValueError("invalid unit_id")

    unit_info = await get_unit_info(context, unit_data.unit_id)
    if unit_info is None:
        raise ValueError("unit info not found")

    rarity = await get_unit_rarity(context, unit_info.rarity)
    if rarity is None:
        raise ValueError("unit rarity not found")

    if unit_data.rank == unit_info.rank_max:
        # Already idolized
        return False

    unit_data.rank = unit_info.rank_max
    unit_data.display_rank = unit_info.rank_max
    unit_data.max_level = rarity.after_level_max

    await album.update(context, user, unit_data.unit_id, rank_max=True)
    await context.db.main.flush()

    return True


LOVE_POS_CALC_ORDER = (4, 0, 1, 2, 3, 5, 6, 7, 8)
LOVE_POS_CALC_WEIGHT = (5, 1, 1, 1, 1, 1, 1, 1, 1)
MAX_LOVE_ADD = [2147483647] * 9


def _get_added_love(love: int, current_love: list[int], max_love: list[int]):
    after_love = current_love.copy()

    # https://github.com/DarkEnergyProcessor/NPPS/blob/v3.1.x/modules/live/reward.php#L337-L369
    while love > 0:
        subtracted = 0

        for i, weight in zip(LOVE_POS_CALC_ORDER, LOVE_POS_CALC_WEIGHT):
            old_love = after_love[i]
            new_love = min(old_love + min(weight, love), max_love[i])
            added_love = new_love - old_love
            after_love[i] = new_love
            subtracted = subtracted + added_love
            love = love - added_love

            if love <= 0:
                break

        if subtracted == 0:
            break

    return after_love, love


async def add_love_by_deck(context: idol.BasicSchoolIdolContext, user: main.User, deck_index: int, love: int):
    deck_data = await load_unit_deck(context, user, deck_index, False)
    if deck_data is None:
        raise ValueError("invalid deck")

    units = util.ensure_no_none(
        [await context.db.main.get(main.Unit, unit_id) for unit_id in deck_data[1]], ValueError, "incomplete deck"
    )
    unit_infos = util.ensure_no_none(
        [await get_unit_info(context, u.unit_id) for u in units], ValueError, "unit info retrieval error"
    )
    unit_rarities = util.ensure_no_none(
        [await get_unit_rarity(context, u.rarity) for u in unit_infos], ValueError, "unit rarity retrieval error"
    )
    max_loves = [
        ur.after_love_max if ud.rank == ui.rank_max else ur.before_love_max
        for ur, ui, ud in zip(unit_rarities, unit_infos, units)
    ]

    before_love = [u.love for u in units]
    loves, remaining = _get_added_love(love, before_love, max_loves)

    total_unit_id_increment: dict[int, int] = {}  # for profile tracking

    for ud, before_love_int, after_love_int in zip(units, before_love, loves):
        value = total_unit_id_increment.get(ud.unit_id, 0) + after_love_int - before_love_int
        total_unit_id_increment[ud.unit_id] = value

    if remaining > 0:
        extra, _ = _get_added_love(remaining, loves, MAX_LOVE_ADD)

        for ud, before_love_int, after_love_int in zip(units, loves, extra):
            value = total_unit_id_increment.get(ud.unit_id, 0) + after_love_int - before_love_int
            total_unit_id_increment[ud.unit_id] = value

    for ur, ud, new_love in zip(unit_rarities, units, loves):
        ud.love = new_love

        await album.update(
            context,
            user,
            ud.unit_id,
            love_max=ud.love >= ur.after_love_max,
            favorite_point=album.Increment(total_unit_id_increment[ud.unit_id]),
        )

    await context.db.main.flush()
    return common.BeforeAfter[list[int]](before=before_love, after=loves)


def calculate_unit_stats(
    unit_info: unit.Unit, pattern: list[unit.UnitLevelUpPattern] | list[unit.LevelLimitPattern], exp: int
):
    result = UnitStatsResult(
        level=1,
        smile=unit_info.smile_max,
        pure=unit_info.pure_max,
        cool=unit_info.cool_max,
        hp=unit_info.hp_max,
        next_exp=0,
        merge_exp=pattern[0].merge_exp,
        merge_cost=pattern[0].merge_cost,
        sale_price=pattern[0].sale_price,
    )

    for diff in pattern:
        result.level = diff.unit_level
        result.smile = unit_info.smile_max - diff.smile_diff
        result.pure = unit_info.pure_max - diff.pure_diff
        result.cool = unit_info.cool_max - diff.cool_diff
        result.hp = unit_info.hp_max - diff.hp_diff
        result.next_exp = diff.next_exp
        result.merge_exp = diff.merge_exp
        result.merge_cost = diff.merge_cost
        result.sale_price = diff.sale_price

        if diff.next_exp > exp:
            break

    return result


def get_exp_for_target_level(
    unit_info: unit.Unit, patterns: list[unit.UnitLevelUpPattern] | list[unit.LevelLimitPattern], level: int
):
    if level == 1:
        return 0

    for pattern in patterns:
        if pattern.unit_level == level - 1:
            return pattern.next_exp

    return patterns[-2].next_exp


def calculate_unit_skill_stats(
    unit_skill: unit.UnitSkill | None, pattern: list[unit.UnitSkillLevelUpPattern] | None, exp: int
):
    if unit_skill is None or pattern is None:
        return (1, 0)

    last = pattern[-1]
    for stat in pattern:
        if stat.next_exp > exp:
            return (stat.skill_level, stat.next_exp)

    return (last.skill_level, 0)


@common.context_cacheable("unit_stats_calculated")
async def get_unit_stats_from_unit_data(context: idol.BasicSchoolIdolContext, calckey: UnitStatsCalculationID):
    unit_info = await get_unit_info(context, calckey.unit_id)
    assert unit_info is not None
    unit_rarity = await get_unit_rarity(context, unit_info.rarity)
    assert unit_rarity is not None

    levelup_pattern = await get_unit_level_up_pattern(context, unit_info.unit_level_up_pattern_id)
    stats = calculate_unit_stats(unit_info, levelup_pattern, calckey.exp)

    if (
        calckey.level_limit_id > 0
        and stats.level >= unit_rarity.after_level_max
        and calckey.max_level > unit_rarity.after_level_max
    ):
        # Use level_limit pattern
        levelup_pattern = await get_unit_level_limit_pattern(context, calckey.level_limit_id)
        stats = calculate_unit_stats(unit_info, levelup_pattern, calckey.exp)

    return stats


async def get_unit_data_full_info(context: idol.BasicSchoolIdolContext, unit_data: main.Unit):
    unit_info = await get_unit_info(context, unit_data.unit_id)
    if unit_info is None:
        raise ValueError("unit_info is none")

    # Calculate unit level
    unit_rarity = await get_unit_rarity(context, unit_info.rarity)
    if unit_rarity is None:
        raise RuntimeError("unit_rarity is none")

    stats = await get_unit_stats_from_unit_data(context, UnitStatsCalculationID.from_unit_data(unit_data))

    # Calculate unit skill level
    skill = await get_unit_skill(context, unit_info.default_unit_skill_id)
    if skill is not None:
        skill_levels = await get_unit_skill_level_up_pattern(
            context,
            skill.unit_skill_level_up_pattern_id,
        )

        skill_stats = calculate_unit_skill_stats(skill, skill_levels, unit_data.skill_exp)
        skill_max = skill_stats[0] == skill.max_level
        skill_level = skill_stats[0]
    else:
        skill_max = True
        skill_level = 1

    idolized = unit_data.rank == unit_info.rank_max
    max_level = unit_rarity.after_level_max if idolized else unit_rarity.before_level_max
    max_love = unit_rarity.after_love_max if idolized else unit_rarity.before_love_max
    real_max_exp = 0 if stats.level == unit_rarity.before_level_max and not idolized else stats.next_exp
    removable_skill_max = unit_data.unit_removable_skill_capacity == unit_info.max_removable_skill_capacity

    return (
        unit_model.UnitInfoData(
            unit_owning_user_id=unit_data.id or 0,
            unit_id=unit_data.unit_id,
            unit_rarity_id=unit_info.rarity,
            exp=unit_data.exp,
            next_exp=real_max_exp,
            level=stats.level,
            max_level=max_level,
            level_limit_id=unit_data.level_limit_id,
            rank=unit_data.rank,
            max_rank=unit_info.rank_max,
            love=unit_data.love,
            max_love=max_love,
            unit_skill_exp=unit_data.skill_exp,
            unit_skill_level=skill_level,
            max_hp=stats.hp,
            unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
            favorite_flag=unit_data.favorite_flag,
            display_rank=unit_data.display_rank,
            is_rank_max=idolized,
            is_love_max=unit_data.love >= unit_rarity.after_love_max,
            is_level_max=stats.level >= unit_rarity.after_level_max,
            is_signed=unit_data.is_signed,
            is_skill_level_max=skill_max,
            is_removable_skill_capacity_max=removable_skill_max,
            insert_date=util.timestamp_to_datetime(unit_data.insert_date),
        ),
        stats,
    )


def calculate_bonus_stat_of_removable_skill(removable_skill: unit.RemovableSkill, stats: tuple[int, int, int]):
    result: list[int] = [0, 0, 0]

    if removable_skill.effect_type in range(1, 4):
        # We only care about smile/pure/cool for now
        i = removable_skill.effect_type - 1
        if removable_skill.fixed_value_flag:
            result[i] = math.ceil(removable_skill.effect_value)
        else:
            result[i] = math.ceil(stats[i] * removable_skill.effect_value / 100.0)

    return result[0], result[1], result[2]


@common.context_cacheable("unit_type_member_tag")
async def _unit_type_has_tag_impl(context: idol.BasicSchoolIdolContext, unit_type_member_tag_ids: tuple[int, int], /):
    q = sqlalchemy.select(unit.UnitTypeMemberTag).where(
        unit.UnitTypeMemberTag.unit_type_id == unit_type_member_tag_ids[0],
        unit.UnitTypeMemberTag.member_tag_id == unit_type_member_tag_ids[1],
    )
    result = await context.db.unit.execute(q)
    return result.scalar() is not None


async def unit_type_has_tag(context: idol.BasicSchoolIdolContext, unit_type_id: int, member_tag_id: int):
    return await _unit_type_has_tag_impl(context, (unit_type_id, member_tag_id))


@common.context_cacheable("unit_leader_skill")
def get_leader_skill(context: idol.BasicSchoolIdolContext, leader_skill: int, /):
    return db.get_decrypted_row(context.db.unit, unit.LeaderSkill, leader_skill)


@common.context_cacheable("unit_extra_leader_skill")
def get_extra_leader_skill(context: idol.BasicSchoolIdolContext, leader_skill: int, /):
    return context.db.unit.get(unit.ExtraLeaderSkill, leader_skill)


async def get_removable_skill_info(context: idol.BasicSchoolIdolContext, user: main.User, removable_skill_id: int):
    q = sqlalchemy.select(main.RemovableSkillInfo).where(
        main.RemovableSkillInfo.user_id == user.id,
        main.RemovableSkillInfo.unit_removable_skill_id == removable_skill_id,
    )
    result = await context.db.main.execute(q)
    return result.scalar()


@common.context_cacheable("unit_removable_skill")
async def get_removable_skill_game_info(context: idol.BasicSchoolIdolContext, removable_skill_id: int, /):
    return await db.get_decrypted_row(context.db.unit, unit.RemovableSkill, removable_skill_id)


async def get_unit_removable_skill_count(
    context: idol.BasicSchoolIdolContext, user: main.User, removable_skill_id: int
):
    removable_skill = await get_removable_skill_info(context, user, removable_skill_id)
    return 0 if removable_skill is None else removable_skill.amount


async def get_all_unit_removable_skill(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.RemovableSkillInfo).where(main.RemovableSkillInfo.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def get_unit_removable_skills(context: idol.BasicSchoolIdolContext, unit_data: main.Unit):
    q = sqlalchemy.select(main.UnitRemovableSkill).where(main.UnitRemovableSkill.unit_owning_user_id == unit_data.id)
    result = await context.db.main.execute(q)
    return list(sis.unit_removable_skill_id for sis in result.scalars())


async def get_all_unit_removable_skills(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.UnitRemovableSkill).where(main.UnitRemovableSkill.user_id == user.id)
    result = await context.db.main.execute(q)
    sis_by_unit_id: dict[int, list[int]] = {}

    for sis in result.scalars():
        if sis.unit_owning_user_id not in sis_by_unit_id:
            sis_info = []
            sis_by_unit_id[sis.unit_owning_user_id] = sis_info
        else:
            sis_info = sis_by_unit_id[sis.unit_owning_user_id]
        sis_info.append(sis.unit_removable_skill_id)

    return sis_by_unit_id


async def add_unit_removable_skill(
    context: idol.BasicSchoolIdolContext, user: main.User, removable_skill_id: int, amount: int = 1
):
    removable_skill = await get_removable_skill_info(context, user, removable_skill_id)
    if removable_skill is None:
        removable_skill = main.RemovableSkillInfo(
            user_id=user.id, unit_removable_skill_id=removable_skill_id, amount=0, insert_date=util.time()
        )
        context.db.main.add(removable_skill)

    removable_skill.amount = removable_skill.amount + amount
    await context.db.main.flush()
    return removable_skill.amount


async def sub_unit_removable_skill(
    context: idol.BasicSchoolIdolContext, /, user: main.User, removable_skill_id: int, amount: int = 1
):
    removable_skill = await get_removable_skill_info(context, user, removable_skill_id)
    if removable_skill is None:
        return -amount

    removable_skill.amount = removable_skill.amount - amount
    if removable_skill.amount >= 0:
        await context.db.main.flush()
    return removable_skill.amount


async def attach_unit_removable_skill(context: idol.BasicSchoolIdolContext, unit: main.Unit, removable_skill_id: int):
    q = sqlalchemy.select(main.UnitRemovableSkill).where(
        main.UnitRemovableSkill.unit_owning_user_id == unit.id,
        main.UnitRemovableSkill.unit_removable_skill_id == removable_skill_id,
    )
    result = await context.db.main.execute(q)
    if result.scalar() is None:
        sis = main.UnitRemovableSkill(
            unit_owning_user_id=unit.id, user_id=unit.user_id, unit_removable_skill_id=removable_skill_id
        )
        context.db.main.add(sis)
        await context.db.main.flush()
        return True

    return False


async def detach_unit_removable_skill(context: idol.BasicSchoolIdolContext, unit: main.Unit, removable_skill_id: int):
    q = sqlalchemy.delete(main.UnitRemovableSkill).where(
        main.UnitRemovableSkill.unit_owning_user_id == unit.id,
        main.UnitRemovableSkill.unit_removable_skill_id == removable_skill_id,
    )
    result = cast(sqlalchemy.CursorResult, await context.db.main.execute(q))
    return result.rowcount > 0


async def get_removable_skill_info_request(context: idol.BasicSchoolIdolContext, user: main.User):
    owning_info = await get_all_unit_removable_skill(context, user)
    sis_info = await get_all_unit_removable_skills(context, user)

    used_sis: dict[int, int] = {}
    for unit_sis in sis_info.values():
        for sis in unit_sis:
            used_sis[sis] = used_sis.setdefault(sis, 0) + 1

    return unit_model.RemovableSkillInfoResponse(
        owning_info=[
            unit_model.OwningRemovableSkillInfo(
                unit_removable_skill_id=i.unit_removable_skill_id,
                total_amount=i.amount,
                equipped_amount=used_sis.get(i.unit_removable_skill_id, 0),
                insert_date=util.timestamp_to_datetime(i.insert_date),
            )
            for i in owning_info
        ],
        equipment_info=dict(
            (
                str(i),
                unit_model.EquipRemovableSkillInfo(
                    unit_owning_user_id=i,
                    detail=[unit_model.EquipRemovableSkillInfoDetail(unit_removable_skill_id=sis) for sis in v],
                ),
            )
            for i, v in sis_info.items()
        ),
    )


async def unit_to_item[_T: unit_model.UnitSupportItem](
    context: idol.BasicSchoolIdolContext, unit_data: main.Unit, *, cls: type[_T] = unit_model.UnitItem
):
    unit_info_data = await get_unit_data_full_info(context, unit_data)
    return cls.model_validate(
        unit_info_data[0].model_dump() | {"add_type": const.ADD_TYPE.UNIT, "item_id": unit_data.unit_id, "amount": 1}
    )


@common.context_cacheable("unit_support_member")
async def is_support_member(context: idol.BasicSchoolIdolContext, unit_id: int, /):
    unit_info = await context.db.unit.get(unit.Unit, unit_id)
    if unit_info is None:
        raise ValueError("invalid unit_id")
    return unit_info.disable_rank_up > 0


@dataclasses.dataclass
class QuickAddResult:
    unit_id: int
    as_item_reward: unit_model.UnitSupportItem | unit_model.UnitItem
    unit_data: main.Unit | None = None
    full_info: unit_model.UnitInfoData | None = None
    stats: UnitStatsResult | None = None

    def update_unit_owning_user_id(self):
        if self.unit_data is not None:
            if self.full_info is not None:
                self.full_info.unit_owning_user_id = self.unit_data.id
            if isinstance(self.as_item_reward, unit_model.UnitItem):
                self.as_item_reward.unit_owning_user_id = self.unit_data.id


async def quick_create_by_unit_add(
    context: idol.BasicSchoolIdolContext, user: main.User, unit_id: int, *, level: int = 1
):
    new_unit_flag = not await album.has_ever_got_unit(context, user, unit_id)
    if await is_support_member(context, unit_id):
        unit_info = await get_unit_info(context, unit_id)
        assert unit_info is not None
        return QuickAddResult(
            unit_id,
            unit_model.UnitSupportItem(
                item_id=unit_id,
                is_support_member=True,
                new_unit_flag=new_unit_flag,
                unit_rarity_id=unit_info.rarity,
                attribute=unit_info.attribute_id,
            ),
        )
    else:
        unit_data = await create_unit(context, user, unit_id, True, level=level)
        assert unit_data is not None
        unit_info = await get_unit_info(context, unit_id)
        assert unit_info is not None
        unit_full_info = await get_unit_data_full_info(context, unit_data)
        return QuickAddResult(
            unit_id=unit_id,
            as_item_reward=unit_model.UnitItem(
                item_id=unit_id,
                new_unit_flag=new_unit_flag,
                attribute=unit_info.attribute_id,
                **util.shallow_dump(unit_full_info[0]),
            ),
            unit_data=unit_data,
            full_info=unit_full_info[0],
            stats=unit_full_info[1],
        )


async def process_quick_add(
    context: idol.BasicSchoolIdolContext,
    /,
    user: main.User,
    quick_add_result: QuickAddResult,
    *,
    current_unit_count: int | None = None,
    reason_jp: str = "Reward",
    reason_en: str = "Reward",
    expire: int = 0,
):
    if current_unit_count is None:
        current_unit_count = await count_units(context, user, True)
    else:
        # Add directly
        if quick_add_result.unit_data:
            if current_unit_count >= user.unit_max:
                # Move to present box
                quick_add_result.as_item_reward.reward_box_flag = True
                await reward.add_item(context, user, quick_add_result.as_item_reward, reason_jp, reason_en, expire)
            else:
                assert quick_add_result.full_info is not None
                await add_unit_by_object(context, user, quick_add_result.unit_data)
                # Update unit_owning_user_id
                quick_add_result.update_unit_owning_user_id()
                current_unit_count = current_unit_count + 1
        else:
            # Add directly
            await add_supporter_unit(context, user, quick_add_result.unit_id)
    return current_unit_count


async def has_signed_variant(context: idol.BasicSchoolIdolContext, unit_id: int):
    return await context.db.unit.get(unit.SignAsset, unit_id) is not None


async def is_unit_max(context: idol.BasicSchoolIdolContext, user: main.User):
    unit_count = await count_units(context, user, True)
    return unit_count >= user.unit_max


async def get_exchange_point_id_by_unit_id(context: idol.BasicSchoolIdolContext, /, unit_id: int):
    # TODO: Probably allow this to be configurable?
    if await exchange.is_festival_unit(context, unit_id):
        return 6

    unit_info = await get_unit_info(context, unit_id)
    assert unit_info is not None
    match unit_info.rarity:
        case 2:
            return 2
        case 3:
            return 3
        case 4:
            return 4
        case 5:
            return 5
        case _:
            return 0


def get_exp_multiplier(evolution_type: const.EVOLUTION_BONUS_TYPE):
    match evolution_type:
        case const.EVOLUTION_BONUS_TYPE.SUPER_SUCCESS:
            return 1.5
        case const.EVOLUTION_BONUS_TYPE.ULTRA_SUCCESS:
            return 2.0
        case _:
            return 1.0


async def get_max_exp(
    context: idol.BasicSchoolIdolContext,
    /,
    unit_data: main.Unit,
    unit_info: unit.Unit | None = None,
    unit_rarity: unit.Rarity | None = None,
):
    if unit_info is None:
        unit_info = await get_unit_info(context, unit_data.unit_id)
        assert unit_info is not None
    if unit_rarity is None:
        unit_rarity = await get_unit_rarity(context, unit_info.rarity)
        assert unit_rarity is not None

    idolized = unit_data.rank >= unit_info.rank_max
    use_user_rank = unit_data.max_level > unit_rarity.after_love_max and unit_data.level_limit_id > 0
    normal_target_level = unit_rarity.after_level_max if idolized else unit_rarity.before_level_max
    target_level = min(unit_data.max_level, 500) if use_user_rank else normal_target_level

    if use_user_rank:
        levelup_pattern = await get_unit_level_limit_pattern(context, unit_data.level_limit_id)
        return levelup_pattern[target_level - 100].next_exp
    else:
        levelup_pattern = await get_unit_level_up_pattern(context, unit_info.unit_level_up_pattern_id)
        return levelup_pattern[target_level - 2].next_exp


async def get_unit_skill_level_data(context: idol.BasicSchoolIdolContext, /, unit_skill_id: int, level: int):
    q = sqlalchemy.select(unit.UnitSkillLevel).where(
        unit.UnitSkillLevel.unit_skill_id == unit_skill_id, unit.UnitSkillLevel.skill_level == level
    )
    result = await context.db.unit.execute(q)
    return db.decrypt_row(context.db.unit, result.scalar())


async def get_max_skill_exp(context: idol.BasicSchoolIdolContext, /, unit_info: unit.Unit):
    skill = await get_unit_skill(context, unit_info.default_unit_skill_id)
    if skill is not None:
        skill_levels = await get_unit_skill_level_up_pattern(context, skill.unit_skill_level_up_pattern_id)
        if len(skill_levels) > 1:
            return skill_levels[-2].next_exp

    return 0


async def create_unit_item(
    context: idol.BasicSchoolIdolContext,
    unit_id: int,
    amount: int = 1,
    /,
    extra_data: unit_model.UnitExtraData | None = unit_model.UnitExtraData.EMPTY,
):
    unit_info = await get_unit_info(context, unit_id)
    if unit_info is None:
        raise ValueError("invalid unit_id")

    if unit_info.disable_rank_up > 0:
        return unit_model.UnitSupportItem(
            item_id=unit_id, unit_rarity_id=unit_info.rarity, attribute=unit_info.attribute_id, amount=amount
        )

    if extra_data is None:
        extra_data = unit_model.UnitExtraData.EMPTY

    # Calculate unit level
    rarity_data = await get_unit_rarity(context, unit_info.rarity)
    if rarity_data is None:
        raise RuntimeError("unit_rarity is none")

    max_level = (
        rarity_data.after_level_max if unit_info.rank_min == unit_info.rank_max else rarity_data.before_level_max
    )
    # FIXME: Determine if it's promo card and set to 2 in that case
    level_limit_id = int(unit_info.rarity == 4)
    rank = util.clamp(extra_data.rank, unit_info.rank_min, unit_info.rank_max)
    idolized = rank == unit_info.rank_max
    max_level = rarity_data.after_level_max if idolized else rarity_data.before_level_max
    max_love = rarity_data.after_love_max if idolized else rarity_data.before_love_max
    love = util.clamp(extra_data.love, 0, max_love)
    removable_skill_capacity = util.clamp(
        util.default(extra_data.unit_removable_skill_capacity, unit_info.default_removable_skill_capacity),
        0,
        unit_info.max_removable_skill_capacity,
    )
    removable_skill_max = removable_skill_capacity == unit_info.max_removable_skill_capacity

    if extra_data.level is not None:
        unit_level_up_pattern = await get_unit_level_up_pattern(context, unit_info.unit_level_up_pattern_id)
        exp = get_exp_for_target_level(unit_info, unit_level_up_pattern, extra_data.level)
    else:
        exp = extra_data.exp

    # Get next EXP
    stats = await get_unit_stats_from_unit_data(
        context, UnitStatsCalculationID(unit_id=unit_id, exp=exp, max_level=max_level, level_limit_id=level_limit_id)
    )
    real_max_exp = 0 if stats.level == rarity_data.before_level_max and not idolized else stats.next_exp

    # Calculate unit skill level
    skill = await get_unit_skill(context, unit_info.default_unit_skill_id)
    if skill is not None:
        skill_levels = await get_unit_skill_level_up_pattern(
            context,
            skill.unit_skill_level_up_pattern_id,
        )

        skill_stats = calculate_unit_skill_stats(skill, skill_levels, extra_data.skill_exp)
        skill_max = skill_stats[0] == skill.max_level
        skill_level = skill_stats[0]
    else:
        skill_max = True
        skill_level = 1

    return unit_model.UnitItem(
        item_id=unit_id,
        amount=amount,
        unit_owning_user_id=0,
        unit_rarity_id=unit_info.rarity,
        exp=exp,
        next_exp=real_max_exp,
        level=stats.level,
        max_level=max_level,
        level_limit_id=level_limit_id,
        rank=rank,
        max_rank=unit_info.rank_max,
        love=love,
        max_love=max_love,
        unit_skill_exp=extra_data.skill_exp,
        unit_skill_level=skill_level,
        max_hp=stats.hp,
        unit_removable_skill_capacity=removable_skill_capacity,
        favorite_flag=False,
        display_rank=max(extra_data.display_rank, unit_info.rank_min),
        is_rank_max=idolized,
        is_love_max=love >= rarity_data.after_love_max,
        is_level_max=stats.level >= rarity_data.after_level_max,
        is_signed=extra_data.is_signed,
        is_skill_level_max=skill_max,
        is_removable_skill_capacity_max=removable_skill_max,
        insert_date=util.timestamp_to_datetime(),
        attribute=unit_info.attribute_id,
    )


async def create_unit_data(
    context: idol.BasicSchoolIdolContext, user: main.User, unit_item: unit_model.UnitItem, /, active: bool = True
):
    return main.Unit(
        user_id=user.id,
        unit_id=unit_item.unit_id,
        active=active,
        favorite_flag=unit_item.favorite_flag,
        is_signed=unit_item.is_signed,
        insert_date=util.time(),
        exp=unit_item.exp,
        skill_exp=unit_item.unit_skill_exp,
        max_level=unit_item.max_level,
        love=unit_item.love,
        rank=unit_item.rank,
        display_rank=unit_item.display_rank,
        level_limit_id=unit_item.level_limit_id,
        unit_removable_skill_capacity=unit_item.unit_removable_skill_capacity,
    )


async def unit_info_data_to_unit_item(context: idol.BasicSchoolIdolContext, unit_info_data: unit_model.UnitInfoData, /):
    unit_info = await get_unit_info(context, unit_info_data.unit_id)
    if unit_info is None:
        raise ValueError("cannot find unit info (db corrupt?)")

    rarity = unit_info_data.unit_rarity_id
    if rarity is None:
        rarity = unit_info.rarity

    return unit_model.UnitItem(
        item_id=unit_info_data.unit_id,
        unit_owning_user_id=unit_info_data.unit_owning_user_id,
        unit_rarity_id=rarity,
        exp=unit_info_data.exp,
        next_exp=unit_info_data.next_exp,
        level=unit_info_data.level,
        max_level=unit_info_data.max_level,
        level_limit_id=unit_info_data.level_limit_id,
        rank=unit_info_data.rank,
        max_rank=unit_info_data.max_rank,
        love=unit_info_data.love,
        max_love=unit_info_data.max_love,
        unit_skill_exp=unit_info_data.unit_skill_exp,
        unit_skill_level=unit_info_data.skill_level,
        max_hp=unit_info_data.max_hp,
        unit_removable_skill_capacity=unit_info_data.unit_removable_skill_capacity,
        favorite_flag=unit_info_data.favorite_flag,
        display_rank=unit_info_data.display_rank,
        is_rank_max=unit_info_data.is_rank_max,
        is_love_max=unit_info_data.is_love_max,
        is_level_max=unit_info_data.is_level_max,
        is_signed=unit_info_data.is_signed,
        is_skill_level_max=unit_info_data.is_skill_level_max,
        is_removable_skill_capacity_max=unit_info_data.is_removable_skill_capacity_max,
        insert_date=unit_info_data.insert_date,
        attribute=unit_info.attribute_id,
    )


UNIT_FIELDS_TO_COPY = set(
    itertools.chain(unit_model.UnitItem.model_fields.keys(), unit_model.UnitItem.model_computed_fields.keys())
) - set(item_model.Item.model_fields.keys())
UNIT_SUPPORT_FIELDS_TO_COPY = set(
    itertools.chain(
        unit_model.UnitSupportItem.model_fields.keys(), unit_model.UnitSupportItem.model_computed_fields.keys()
    )
) - set(item_model.Item.model_fields.keys())


def populate_unit_item_to_other(unit_item: unit_model.UnitItem | unit_model.UnitSupportItem, other: pydantic.BaseModel):
    match unit_item:
        case unit_model.UnitItem():
            target_set = UNIT_FIELDS_TO_COPY
        case unit_model.UnitSupportItem():
            target_set = UNIT_SUPPORT_FIELDS_TO_COPY
        case _:
            raise TypeError("expected UnitItem or UnitSupportItem")

    for k in target_set:
        setattr(other, k, getattr(unit_item, k))


async def tupleize_unit_id_and_type(context: idol.BasicSchoolIdolContext, unit_ids: list[int]):
    unit_type_ids = [(await get_unit_info(context, u)).unit_type_id for u in unit_ids]
    return (
        unit_ids[0],
        unit_ids[1],
        unit_ids[2],
        unit_ids[3],
        unit_ids[4],
        unit_ids[5],
        unit_ids[6],
        unit_ids[7],
        unit_ids[8],
    ), (
        unit_type_ids[0],
        unit_type_ids[1],
        unit_type_ids[2],
        unit_type_ids[3],
        unit_type_ids[4],
        unit_type_ids[5],
        unit_type_ids[6],
        unit_type_ids[7],
        unit_type_ids[8],
    )
