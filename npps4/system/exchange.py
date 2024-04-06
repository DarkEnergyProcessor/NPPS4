import sqlalchemy
from .. import idol
from ..db import exchange
from ..db import main


async def is_festival_unit(context: idol.BasicSchoolIdolContext, /, unit_id: int):
    test = await context.db.exchange.get(exchange.ExchangeFestivalPointUnit, unit_id)
    return test is not None


async def should_give_sticker(context: idol.BasicSchoolIdolContext, /, unit_id: int):
    test = await context.db.exchange.get(exchange.ExchangeNoPointUnit, unit_id)
    return test is None


async def get_exchange_point(
    context: idol.BasicSchoolIdolContext, /, user: main.User, exchange_point_id: int, ensure: bool
):
    q = sqlalchemy.select(main.ExchangePointItem).where(
        main.ExchangePointItem.user_id == user.id, main.ExchangePointItem.exchange_point_id == exchange_point_id
    )
    result = await context.db.main.execute(q)
    exchange_point = result.scalar()

    if exchange_point is None and ensure:
        exchange_point = main.ExchangePointItem(user_id=user.id, exchange_point_id=exchange_point_id)
        context.db.main.add(exchange_point)
        await context.db.main.flush()

    return exchange_point


async def add_exchange_point(
    context: idol.BasicSchoolIdolContext, /, user: main.User, exchange_point_id: int, quantity: int
):
    if quantity < 1:
        raise ValueError("invalid amount")

    exchange_point = await get_exchange_point(context, user, exchange_point_id, True)
    if exchange_point is None:
        return False

    exchange_point.amount = exchange_point.amount + quantity
    await context.db.main.flush()
    return True


async def sub_exchange_point(
    context: idol.BasicSchoolIdolContext, /, user: main.User, exchange_point_id: int, quantity: int = 1
):
    if quantity < 1:
        raise ValueError("invalid amount")

    exchange_point = await get_exchange_point(context, user, exchange_point_id, False)
    if exchange_point is not None and exchange_point.amount >= quantity:
        exchange_point.amount = exchange_point.amount - quantity
        await context.db.main.flush()
        return True

    return False
