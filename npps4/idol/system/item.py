import pydantic

from ...db import unit


class Item(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    add_type: int
    item_id: int
    amount: int


class RewardWithCategory(Item):
    item_category_id: int = 0  # TODO
    reward_box_flag: bool


class Reward(Item):
    reward_box_flag: bool


def add_loveca(amount: int):
    return Item(add_type=3001, item_id=4, amount=amount)


def add_g(amount: int):
    return Item(add_type=3000, item_id=3, amount=amount)


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
    t = Item(add_type=1001, item_id=unit_info.unit_id, amount=1)
    t.level = level
    t.exp = exp
    t.max_level = unit_rarity.after_level_max if idolized else unit_rarity.before_level_max
    t.rank = unit_info.rank_max if idolized else unit_info.rank_min
    t.love = love
    t.is_signed = is_signed
    t.unit_skill_exp = unit_skill_exp
    t.display_rank = idolized
    t.unit_removable_skill_capacity = unit_info.default_removable_skill_capacity
    return t
