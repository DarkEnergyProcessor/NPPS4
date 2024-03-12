from . import item_model
from .. import idol
from ..const import ADD_TYPE
from ..db import item


async def get_item_category_for_type_1000(context: idol.BasicSchoolIdolContext, item_id: int):
    item_info = await context.db.item.get(item.KGItem, item_id)
    return 0 if item_info is None else (item_info.item_category_id or 0)


async def get_item_category(context: idol.BasicSchoolIdolContext, item_data: item_model.Item):
    match item_data.add_type:
        case ADD_TYPE.ITEM:
            return await get_item_category_for_type_1000(context, item_data.item_id)
        case ADD_TYPE.GAME_COIN:
            return await get_item_category_for_type_1000(context, 3)
        case ADD_TYPE.LOVECA:
            return await get_item_category_for_type_1000(context, 4)
        case ADD_TYPE.SOCIAL_POINT:
            return await get_item_category_for_type_1000(context, 5)
        case _:
            return 0


async def update_item_category_id(context: idol.BasicSchoolIdolContext, item_data: item_model.Item):
    item_data.item_category_id = await get_item_category(context, item_data)
    return item_data


def loveca(amount: int, /):
    return item_model.Item(add_type=ADD_TYPE.LOVECA, item_id=4, amount=amount, item_category_id=4)


def game_coin(amount: int, /):
    return item_model.Item(add_type=ADD_TYPE.GAME_COIN, item_id=3, amount=amount, item_category_id=3)


def social_point(amount: int, /):
    return item_model.Item(add_type=ADD_TYPE.SOCIAL_POINT, item_id=2, amount=amount, item_category_id=2)
