import pydantic

from ... import idol
from ...const import ADD_TYPE
from ...db import item
from ...db import unit

from typing import Any, TypeVar


class Item(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    add_type: int
    item_id: int
    amount: int = 1

    def dump_extra_data(self) -> dict[str, Any]:
        return {}


class ItemWithCategory(Item):
    item_category_id: int = 0


class RewardFlag(pydantic.BaseModel):
    reward_box_flag: bool = False
    comment: str = ""


class Reward(Item, RewardFlag):
    pass


class RewardWithCategory(ItemWithCategory, RewardFlag):
    pass


_T = TypeVar("_T", bound=Item)


def add_loveca(amount: int, *, cls: type[_T] = Item) -> _T:
    return cls(add_type=ADD_TYPE.LOVECA, item_id=4, amount=amount)


def add_g(amount: int, *, cls: type[_T] = Item) -> _T:
    return cls(add_type=ADD_TYPE.GAME_COIN, item_id=3, amount=amount)


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
