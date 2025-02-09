import collections.abc
import pydantic
import sqlalchemy

from . import award
from . import background
from . import common
from .. import const
from .. import data
from .. import idol
from .. import util
from ..db import exchange
from ..db import main

from typing import Any


class ExchangePointInfo(pydantic.BaseModel):
    rarity: int
    exchange_point: int


class ExchangeCost(pydantic.BaseModel):
    rarity: int
    cost_value: int


class ExchangeItemBase(pydantic.BaseModel):
    exchange_item_id: int
    title: str
    is_new: bool = False
    option: Any | None = None
    add_type: const.ADD_TYPE
    item_id: int
    amount: int = 1
    item_category_id: int = 0
    is_rank_max: bool = False
    cost_list: list[ExchangeCost]  # Note: Limited to 3 costs
    already_obtained: bool = False
    got_item_count: int = 0
    term_count: int = 0


class ExchangeItemWithExpiry(ExchangeItemBase):
    term_end_date: str


class ExchangeItemWithMaxCount(ExchangeItemBase):
    max_item_count: int


class ExchangeItemWithMaxCountAndExpiry(ExchangeItemBase):
    term_end_date: str
    max_item_count: int


@common.context_cacheable("exchange_festival_point_unit")
async def is_festival_unit(context: idol.BasicSchoolIdolContext, unit_id: int, /):
    test = await context.db.exchange.get(exchange.ExchangeFestivalPointUnit, unit_id)
    return test is not None


@common.context_cacheable("exchange_no_point_unit")
async def should_give_sticker(context: idol.BasicSchoolIdolContext, unit_id: int, /):
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


async def get_exchange_point_list(
    context: idol.BasicSchoolIdolContext, user: main.User, /
) -> collections.abc.Iterable[main.ExchangePointItem]:
    q = sqlalchemy.select(main.ExchangePointItem).where(
        main.ExchangePointItem.user_id == user.id, main.ExchangePointItem.amount > 0
    )
    result = await context.db.main.execute(q)
    return result.scalars()


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
    q = sqlalchemy.select(main.ExchangePointItem).where(main.ExchangePointItem.user_id == user.id)
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


async def _get_exchange_item_limit(
    context: idol.BasicSchoolIdolContext, /, user: main.User, exchange_item_id: int, guarantee: bool
):
    q = sqlalchemy.select(main.ExchangeItemLimit).where(
        main.ExchangeItemLimit.user_id == user.id, main.ExchangeItemLimit.exchange_item_id == exchange_item_id
    )
    result = await context.db.main.execute(q)
    exchange_limit = result.scalar()

    if exchange_limit is None and guarantee:
        exchange_limit = main.ExchangeItemLimit(user_id=user.id, exchange_item_id=exchange_item_id)
        context.db.main.add(exchange_limit)

    return exchange_limit


async def add_exchange_item_got_count(
    context: idol.BasicSchoolIdolContext, /, user: main.User, exchange_item_id: int, amount: int
):
    exchange_limit = await _get_exchange_item_limit(context, user, exchange_item_id, True)
    assert exchange_limit is not None
    exchange_limit.count = exchange_limit.count + amount
    await context.db.main.flush()


async def get_exchange_item_info_by_raw_info(
    context: idol.BasicSchoolIdolContext, user: main.User, raw_info: data.schema.StickerShop, time: int | None = None, /
):
    if time is None:
        time = util.time()

    exchange_item_id = raw_info.exchange_item_id
    exchange_limit = await _get_exchange_item_limit(context, user, exchange_item_id, False)
    exchange_title = context.get_text(raw_info.name, raw_info.name_en)
    exchange_is_new = exchange_limit is None
    exchange_limit = await _get_exchange_item_limit(context, user, exchange_item_id, True)
    assert exchange_limit is not None
    exchange_max_amount = None
    exchange_got_item_count = exchange_limit.count
    exchange_term_count = max((raw_info.end_time - time + 86399) // 86400, 0)
    if raw_info.limit > 0:
        exchange_max_amount = raw_info.limit

    # Handling special case
    match raw_info.add_type:
        case const.ADD_TYPE.AWARD:
            exchange_max_amount = 1
            exchange_got_item_count = int(await award.has_award(context, user, raw_info.item_id))
        case const.ADD_TYPE.BACKGROUND:
            exchange_max_amount = 1
            exchange_got_item_count = int(await background.has_background(context, user, raw_info.item_id))

    # Oh no
    exchange_item_data = ExchangeItemBase(
        exchange_item_id=exchange_item_id,
        title=exchange_title,
        is_new=exchange_is_new,
        add_type=raw_info.add_type,
        item_id=raw_info.item_id,
        amount=raw_info.amount,
        cost_list=[
            ExchangeCost(rarity=cost.rarity, cost_value=cost.cost) for cost in raw_info.costs[:3]
        ],  # Client crash if you have more than 3
        already_obtained=exchange_got_item_count > 0,
        got_item_count=exchange_got_item_count,
        term_count=exchange_term_count,
    )
    if exchange_max_amount is not None:
        if raw_info.end_time > 0:
            exchange_item_data = ExchangeItemWithMaxCountAndExpiry(
                term_end_date=util.timestamp_to_datetime(raw_info.end_time),
                max_item_count=exchange_max_amount,
                **exchange_item_data.model_dump(),
            )
        else:
            exchange_item_data = ExchangeItemWithMaxCount(
                max_item_count=exchange_max_amount, **exchange_item_data.model_dump()
            )
    elif raw_info.end_time > 0:
        exchange_item_data = ExchangeItemWithExpiry(
            term_end_date=util.timestamp_to_datetime(raw_info.end_time), **exchange_item_data.model_dump()
        )
    return exchange_item_data


async def get_exchange_item_info(context: idol.BasicSchoolIdolContext, /, user: main.User):
    server_data = data.get()
    result: list[ExchangeItemBase] = []

    for raw_info in server_data.sticker_shop:
        time = util.time()

        if raw_info.end_time == 0 or raw_info.end_time >= time:
            result.append(await get_exchange_item_info_by_raw_info(context, user, raw_info, time))

    return result


async def find_raw_exchange_item_info_by_id(context: idol.BasicSchoolIdolContext, exchange_item_id: int, /):
    server_data = data.get()

    for raw_info in server_data.sticker_shop:
        if raw_info._internal_id == exchange_item_id:
            return raw_info

    return None
