import queue

import sqlalchemy

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


async def add_unit(context: idol.SchoolIdolParams, user: main.User, unit_id: int, active: bool):
    unit_info = await context.db.unit.get(unit.Unit, unit_id)
    if unit_info is None:
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
    context.db.main.add(user_unit)
    await context.db.main.flush()
    return user_unit


async def remove_unit(context: idol.SchoolIdolParams, user: main.User, user_unit: main.Unit):
    if user_unit.user_id != user.id:
        raise ValueError("invalid unit_id")

    # Remove from deck first
    q = sqlalchemy.delete(main.UnitDeckPosition).where(main.UnitDeckPosition.unit_id == user_unit.id)
    await context.db.main.execute(q)

    # Remove from unit
    await context.db.main.delete(user_unit)
    await context.db.main.flush()


TEAM_NAMING = {idoltype.Language.en: "Team %s", idoltype.Language.jp: "ユニット%s"}


@overload
async def load_unit_deck(
    context: idol.SchoolIdolParams, user: main.User, index: int, ensure: Literal[False]
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
            else:
                deckpos = deckposlist.get()

            deckpos.unit_id = unit_id
            deckpos.position = i

    while not deckposlist.empty():
        await context.db.main.delete(deckposlist.get())

    await context.db.main.flush()
