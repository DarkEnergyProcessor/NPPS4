import pydantic
import sqlalchemy

from .. import idol
from ..db import exchange
from ..db import main


class ExchangePointInfo(pydantic.BaseModel):
    rarity: int
    exchange_point: int


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


async def get_exchange_point_amount(context: idol.BasicSchoolIdolContext, /, user: main.User, exchange_point_id: int):
    exchange_point = await get_exchange_point(context, user, exchange_point_id, True)
    if exchange_point is None:
        return 0

    return exchange_point.amount


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


async def get_exchange_points_response(context: idol.BasicSchoolIdolContext, /, user: main.User):
    q = sqlalchemy.select(main.ExchangePointItem).where(
        main.ExchangePointItem.user_id == user.id, main.ExchangePointItem.amount > 0
    )
    result = await context.db.main.execute(q)
    return [ExchangePointInfo(rarity=e.exchange_point_id, exchange_point=e.amount) for e in result.scalars()]


async def get_exchange_needed_to_idolize(
    context: idol.BasicSchoolIdolContext, /, exchange_point_id: int, unit_rarity_id: int
) -> int:
    if unit_rarity_id < 2 or unit_rarity_id > 5:
        # Cannot use any sticker to idolize N cards
        return 0

    q = sqlalchemy.select(
        exchange.ExchangePoint.r_rank_up_point,
        exchange.ExchangePoint.sr_rank_up_point,
        exchange.ExchangePoint.ur_rank_up_point,
        exchange.ExchangePoint.ssr_rank_up_point,
    ).where(exchange.ExchangePoint.exchange_point_id == exchange_point_id)
    result = await context.db.exchange.execute(q)
    points = result.first()
    if points is None:
        return 0
    return points[unit_rarity_id - 2] or 0
