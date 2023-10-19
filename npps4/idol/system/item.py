import dataclasses

from ...db import unit


@dataclasses.dataclass
class AddType:
    add_type: int
    item_id: int
    amount: int


@dataclasses.dataclass
class UnitAddType(AddType):
    level: int
    exp: int
    max_level: int
    rank: int
    love: int
    is_signed: bool
    unit_skill_exp: int
    display_rank: int
    unit_removable_skill_capacity: int


def add_loveca(amount: int):
    return AddType(add_type=3001, item_id=4, amount=amount)


def add_g(amount: int):
    return AddType(add_type=3000, item_id=3, amount=amount)


def add_unit(
    unit_info: unit.Unit,
    unit_rarity: unit.Rarity,
    *,
    level: int = 1,
    exp: int = 0,
    love: int = 0,
    is_signed: bool = False,
    unit_skill_exp: int = 0,
    idolized: bool = False
):
    idolized = unit_info.rank_max == unit_info.rank_min or idolized
    return UnitAddType(
        add_type=1001,
        item_id=unit_info.unit_id,
        amount=1,
        level=level,
        exp=exp,
        max_level=unit_rarity.after_level_max if idolized else unit_rarity.before_level_max,
        rank=unit_info.rank_max if idolized else unit_info.rank_min,
        love=love,
        is_signed=is_signed,
        unit_skill_exp=unit_skill_exp,
        display_rank=idolized,
        unit_removable_skill_capacity=unit_info.default_removable_skill_capacity,
    )
