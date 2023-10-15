import dataclasses
import queue

import sqlalchemy

from . import album
from . import core
from ... import idol
from ... import idoltype
from ...db import main
from ...db import unit

from typing import Literal, overload


async def count_units(context: idol.SchoolIdolParams, user: main.User, active: bool):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Unit)
        .where(main.Unit.user_id == user.id, main.Unit.active == active)
    )
    result = await context.db.main.execute(q)
    return result.scalar() or 0


async def get_all_units(context: idol.SchoolIdolParams, user: main.User, active: bool | None = None):
    if active is None:
        q = sqlalchemy.select(main.Unit).where(main.Unit.user_id == user.id)
    else:
        q = sqlalchemy.select(main.Unit).where(main.Unit.user_id == user.id, main.Unit.active == active)

    result = await context.db.main.execute(q)
    return result.scalars().all()


async def add_unit(context: idol.SchoolIdolParams, user: main.User, unit_id: int, active: bool):
    unit_info = await get_unit_info(context, unit_id)
    if unit_info is None or unit_info.disable_rank_up:
        return None

    rarity = await context.db.unit.get(unit.Rarity, unit_info.rarity)
    if rarity is None:
        return None

    max_level = rarity.after_level_max if unit_info.rank_min == unit_info.rank_max else rarity.before_level_max

    user_unit = main.Unit(
        user_id=user.id,
        unit_id=unit_id,
        active=active,
        max_level=max_level,
        rank=unit_info.rank_min,
        display_rank=unit_info.rank_min,
        unit_removable_skill_capacity=unit_info.default_removable_skill_capacity,
    )

    if unit_info.rarity == 4:
        # FIXME: Determine if it's promo card and set to 2 in that case
        user_unit.level_limit_id = 1

    context.db.main.add(user_unit)
    await album.update(context, user, unit_id, flush=False)
    await context.db.main.flush()
    return user_unit


async def get_supporter_unit(context: idol.SchoolIdolParams, user: main.User, unit_id: int, ensure: bool = False):
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


async def add_supporter_unit(context: idol.SchoolIdolParams, user: main.User, unit_id: int, quantity: int = 1):
    if quantity < 1:
        raise ValueError("invalid amount")

    unitsupp = await get_supporter_unit(context, user, unit_id, True)

    if unitsupp is None:
        return False

    unitsupp.amount = unitsupp.amount + quantity
    await album.update(context, user, unit_id, True, True, True, flush=False)
    await context.db.main.flush()
    return True


async def sub_supporter_unit(context: idol.SchoolIdolParams, user: main.User, unit_id: int, quantity: int = 1):
    if quantity < 1:
        raise ValueError("invalid amount")

    unitsupp = await get_supporter_unit(context, user, unit_id)

    if unitsupp is not None and unitsupp.amount >= quantity:
        unitsupp.amount = unitsupp.amount - quantity
        await context.db.main.flush()
        return True

    return False


async def get_all_supporter_unit(context: idol.SchoolIdolParams, user: main.User):
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


def get_unit_info(context: idol.BasicSchoolIdolContext, unit_id: int):
    return context.db.unit.get(unit.Unit, unit_id)


def get_unit_rarity(context: idol.BasicSchoolIdolContext, unit_data: unit.Unit):
    return context.db.unit.get(unit.Rarity, unit_data.rarity)


async def get_unit_level_up_pattern(context: idol.SchoolIdolParams, unit_data: unit.Unit):
    q = sqlalchemy.select(unit.UnitLevelUpPattern).where(
        unit.UnitLevelUpPattern.unit_level_up_pattern_id == unit_data.unit_level_up_pattern_id
    )
    result = await context.db.unit.execute(q)
    return list(result.scalars())


async def get_unit_skill(context: idol.SchoolIdolParams, unit_data: unit.Unit):
    if unit_data.default_unit_skill_id is None:
        return None

    return await context.db.unit.get(unit.UnitSkill, unit_data.default_unit_skill_id)


async def get_unit_skill_level_up_pattern(context: idol.SchoolIdolParams, unit_skill: unit.UnitSkill | None):
    if unit_skill is None:
        return None

    q = sqlalchemy.select(unit.UnitSkillLevelUpPattern).where(
        unit.UnitSkillLevelUpPattern.unit_skill_level_up_pattern_id == unit_skill.unit_skill_level_up_pattern_id
    )
    result = await context.db.unit.execute(q)
    return list(result.scalars())


async def remove_unit(context: idol.SchoolIdolParams, user: main.User, user_unit: main.Unit):
    if user_unit.user_id != user.id:
        raise ValueError("invalid unit_id")

    # Remove from deck first
    q = sqlalchemy.delete(main.UnitDeckPosition).where(main.UnitDeckPosition.unit_id == user_unit.id)
    await context.db.main.execute(q)

    # Remove from unit
    await context.db.main.delete(user_unit)
    await context.db.main.flush()


# TODO: Move to consts
TEAM_NAMING = {idoltype.Language.en: "Team {0}", idoltype.Language.jp: "ユニット{0}"}


@overload
async def load_unit_deck(
    context: idol.SchoolIdolParams, user: main.User, index: int, ensure: Literal[False] = False
) -> tuple[main.UnitDeck, list[int]] | None:
    ...


@overload
async def load_unit_deck(
    context: idol.SchoolIdolParams, user: main.User, index: int, ensure: Literal[True]
) -> tuple[main.UnitDeck, list[int]]:
    ...


async def load_unit_deck(context: idol.SchoolIdolParams, user: main.User, index: int, ensure: bool = False):
    if index not in range(1, 19):
        raise ValueError("deck index out of range")

    q = sqlalchemy.select(main.UnitDeck).where(main.UnitDeck.user_id == user.id, main.UnitDeck.deck_number == index)
    result = await context.db.main.execute(q)
    deck = result.scalar()
    deckunits = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    if deck is None:
        if not ensure:
            return None

        deck = main.UnitDeck(
            user_id=user.id, deck_number=index, name=TEAM_NAMING[context.lang].format(chr(index + 64))
        )
        context.db.main.add(deck)
        await context.db.main.flush()
    else:
        q = sqlalchemy.select(main.UnitDeckPosition).where(main.UnitDeckPosition.deck_id == deck.id)
        result = await context.db.main.execute(q)
        for row in result.scalars():
            deckunits[row.position - 1] = row.unit_id

    return deck, deckunits


async def save_unit_deck(context: idol.SchoolIdolParams, user: main.User, deck: main.UnitDeck, units: list[int]):
    if deck.user_id != user.id:
        raise ValueError("invalid deck")

    q = sqlalchemy.select(main.UnitDeckPosition).where(main.UnitDeckPosition.deck_id == deck.id)
    result = await context.db.main.execute(q)
    deckposlist: queue.SimpleQueue[main.UnitDeckPosition] = queue.SimpleQueue()
    for deckpos in result.scalars():
        deckposlist.put(deckpos)

    for i, unit_id in enumerate(units, 1):
        if unit_id > 0:
            if deckposlist.empty():
                deckpos = main.UnitDeckPosition(deck_id=deck.id, position=i)
                context.db.main.add(deckpos)
            else:
                deckpos = deckposlist.get()

            deckpos.unit_id = unit_id
            deckpos.position = i

    while not deckposlist.empty():
        await context.db.main.delete(deckposlist.get())

    await context.db.main.flush()


async def set_unit_center(
    context: idol.BasicSchoolIdolContext, user: main.User, unit_data: main.Unit, flush: bool = True
):
    center = await context.db.main.get(main.UnitCenter, user.id)
    if center is None:
        center = main.UnitCenter(user_id=user.id)
        context.db.main.add(center)

    center.unit_id = unit_data.id
    if flush:
        await context.db.main.flush()


async def get_unit_center(context: idol.BasicSchoolIdolContext, user: main.User):
    center = await context.db.main.get(main.UnitCenter, user.id)
    return center


async def idolize(context: idol.BasicSchoolIdolContext, user: main.User, unit_data: main.Unit, flush: bool = True):
    if unit_data.user_id != user.id:
        raise ValueError("invalid unit_id")

    unit_info = await get_unit_info(context, unit_data.unit_id)
    if unit_info is None:
        raise ValueError("unit info not found")

    rarity = await get_unit_rarity(context, unit_info)
    if rarity is None:
        raise ValueError("unit rarity not found")

    if unit_data.rank == unit_info.rank_max:
        # Already idolized
        return False

    unit_data.rank = unit_info.rank_max
    unit_data.display_rank = unit_info.rank_max
    unit_data.max_level = rarity.after_level_max

    await album.update(context, user, unit_data.unit_id, rank_max=True, flush=False)

    if flush:
        await context.db.main.flush()

    return True


@dataclasses.dataclass
class UnitStatsResult:
    level: int
    smile: int
    pure: int
    cool: int
    hp: int
    next_exp: int


def calculate_unit_stats(unit_data: unit.Unit, pattern: list[unit.UnitLevelUpPattern], exp: int):
    last = pattern[-1]
    result = UnitStatsResult(
        level=last.unit_level,
        smile=unit_data.smile_max,
        pure=unit_data.pure_max,
        cool=unit_data.cool_max,
        hp=unit_data.hp_max,
        next_exp=0,
    )

    for diff in pattern:
        if diff.next_exp > exp:
            result.level = diff.unit_level
            result.smile = result.smile - diff.smile_diff
            result.pure = result.pure - diff.pure_diff
            result.cool = result.cool - diff.cool_diff
            result.hp = result.hp - diff.hp_diff
            result.next_exp = diff.next_exp
            break

    return result


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
