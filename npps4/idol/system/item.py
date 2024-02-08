import pydantic

from ... import idol
from ...const import ADD_TYPE
from ...db import item
from ...db import unit


class Item(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    add_type: int
    item_id: int
    amount: int = 1


class ItemWithCategory(Item):
    item_category_id: int = 0


class RewardWithCategory(ItemWithCategory):
    reward_box_flag: bool


class Reward(Item):
    reward_box_flag: bool = False


def add_loveca(amount: int):
    return Item(add_type=ADD_TYPE.LOVECA, item_id=4, amount=amount)


def add_g(amount: int):
    return Item(add_type=ADD_TYPE.GAME_COIN, item_id=3, amount=amount)


def add_unit(
    unit_info: unit.Unit,
    unit_rarity: unit.Rarity,
    *,
    level: int = 1,
    exp: int = 0,
    love: int = 0,
    is_signed: bool = False,
    unit_skill_exp: int = 0,
    idolized: bool = False,
):
    idolized = unit_info.rank_max == unit_info.rank_min or idolized
    t = Item(add_type=ADD_TYPE.UNIT, item_id=unit_info.unit_id, amount=1)
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


async def get_item_category_by_id(context: idol.BasicSchoolIdolContext, item_id: int):
    item_info = await context.db.item.get(item.KGItem, item_id)
    return 0 if item_info is None else (item_info.item_category_id or 0)


async def get_item_category(context: idol.BasicSchoolIdolContext, item_data: Item):
    match item_data.add_type:
        case ADD_TYPE.ITEM:
            return await get_item_category_by_id(context, item_data.item_id)
        case ADD_TYPE.GAME_COIN:
            return await get_item_category_by_id(context, 3)
        case ADD_TYPE.LOVECA:
            return await get_item_category_by_id(context, 4)
        case ADD_TYPE.SOCIAL_POINT:
            return await get_item_category_by_id(context, 5)
        case _:
            return 0


async def update_item_category_id(context: idol.BasicSchoolIdolContext, item_data: ItemWithCategory):
    item_data.item_category_id = await get_item_category(context, item_data)
    return item_data
