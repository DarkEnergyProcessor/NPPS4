import sqlalchemy

from . import common
from . import item_model
from .. import const
from .. import db
from .. import idol
from ..db import item
from ..db import main


async def get_item_category_for_type_1000(context: idol.BasicSchoolIdolContext, item_id: int):
    item_info = await context.db.item.get(item.KGItem, item_id)
    return 0 if item_info is None else (item_info.item_category_id or 0)


async def get_item_category(context: idol.BasicSchoolIdolContext, item_data: item_model.Item):
    match item_data.add_type:
        case const.ADD_TYPE.ITEM:
            return await get_item_category_for_type_1000(context, item_data.item_id)
        case const.ADD_TYPE.GAME_COIN:
            return await get_item_category_for_type_1000(context, 3)
        case const.ADD_TYPE.LOVECA:
            return await get_item_category_for_type_1000(context, 4)
        case const.ADD_TYPE.SOCIAL_POINT:
            return await get_item_category_for_type_1000(context, 5)
        case _:
            return 0


async def update_item_category_id(context: idol.BasicSchoolIdolContext, item_data: item_model.Item):
    item_data.item_category_id = await get_item_category(context, item_data)
    return item_data


def loveca(amount: int, /, paid: bool = False):
    return item_model.Item(add_type=const.ADD_TYPE.LOVECA, item_id=1 if paid else 4, amount=amount, item_category_id=4)


def game_coin(amount: int, /):
    return item_model.Item(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=amount, item_category_id=3)


def social_point(amount: int, /):
    return item_model.Item(add_type=const.ADD_TYPE.SOCIAL_POINT, item_id=2, amount=amount, item_category_id=2)


def base_loveca(amount: int, /, paid: bool = False):
    return item_model.BaseItem(add_type=const.ADD_TYPE.LOVECA, item_id=1 if paid else 4, amount=amount)


async def get_buff_item_ids(context: idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(item.BuffItem.item_id)
    result = await context.db.item.execute(q)
    return list(result.scalars())


async def get_reinforce_item_ids(context: idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(item.UnitReinforceItem.item_id)
    result = await context.db.item.execute(q)
    return list(result.scalars())


async def get_item_list(context: idol.BasicSchoolIdolContext, user: main.User):
    buff_items = set(await get_buff_item_ids(context))
    reinforce_items = set(await get_reinforce_item_ids(context))

    general_item_list: list[common.ItemCount] = []
    buff_item_list: list[common.ItemCount] = []
    reinforce_item_list: list[common.ItemCount] = []

    q = sqlalchemy.select(main.Item).where(main.Item.user_id == user.id, main.Item.amount > 0)
    result = await context.db.main.execute(q)
    for i in result.scalars():
        item_count = common.ItemCount(item_id=i.item_id, amount=i.amount)

        if i.item_id in reinforce_items:
            reinforce_item_list.append(item_count)
        elif i.item_id in buff_items:
            buff_item_list.append(item_count)
        else:
            general_item_list.append(item_count)

    return general_item_list, buff_item_list, reinforce_item_list


async def get_item_data(context: idol.BasicSchoolIdolContext, /, user: main.User, item_id: int):
    q = sqlalchemy.select(main.Item).where(main.Item.user_id == user.id, main.Item.item_id == item_id)
    result = await context.db.main.execute(q)
    return result.scalar()


async def get_item_data_guaranteed(context: idol.BasicSchoolIdolContext, /, user: main.User, item_id: int):
    item_data = await get_item_data(context, user, item_id)
    if item_data is None:
        item_data = main.Item(user_id=user.id, item_id=item_id)
        context.db.main.add(item_data)
    return item_data


async def add_item(context: idol.BasicSchoolIdolContext, /, user: main.User, item_id: int, amount: int):
    match item_id:
        case 2:
            user.social_point = user.social_point + amount
        case 3:
            user.game_coin = user.game_coin + amount
        case 4:
            user.free_sns_coin = user.free_sns_coin + amount
        case _:
            item_data = await get_item_data_guaranteed(context, user, item_id)
            item_data.amount = item_data.amount + amount


async def get_item_count(context: idol.BasicSchoolIdolContext, /, user: main.User, item_id: int):
    match item_id:
        case 2:
            return user.social_point
        case 3:
            return user.game_coin
        case 4:
            return user.free_sns_coin + user.paid_sns_coin
        case _:
            item_data = await get_item_data(context, user, item_id)
            return 0 if item_data is None else item_data.amount


async def get_recovery_item_data(context: idol.BasicSchoolIdolContext, /, user: main.User, recovery_item_id: int):
    q = sqlalchemy.select(main.RecoveryItem).where(
        main.RecoveryItem.user_id == user.id, main.RecoveryItem.item_id == recovery_item_id
    )
    result = await context.db.main.execute(q)
    return result.scalar()


async def get_recovery_item_data_guaranteed(
    context: idol.BasicSchoolIdolContext, /, user: main.User, recovery_item_id: int
):
    item_data = await get_recovery_item_data(context, user, recovery_item_id)
    if item_data is None:
        item_data = main.RecoveryItem(user_id=user.id, item_id=recovery_item_id)
        context.db.main.add(item_data)
    return item_data


async def add_recovery_item(
    context: idol.BasicSchoolIdolContext, /, user: main.User, recovery_item_id: int, amount: int
):
    item_data = await get_recovery_item_data_guaranteed(context, user, recovery_item_id)
    item_data.amount = item_data.amount + amount


async def get_recovery_items(context: idol.BasicSchoolIdolContext, /, user: main.User):
    q = sqlalchemy.select(main.RecoveryItem).where(main.RecoveryItem.user_id == user.id, main.RecoveryItem.amount > 0)
    result = await context.db.main.execute(q)
    return [common.ItemCount(item_id=i.item_id, amount=i.amount) for i in result.scalars()]


@common.context_cacheable("recovery_item")
async def get_recovery_item_info(context: idol.BasicSchoolIdolContext, recovery_item_id: int, /):
    return await db.get_decrypted_row(context.db.item, item.RecoveryItem, recovery_item_id)
