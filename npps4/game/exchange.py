import pydantic

from .. import const
from .. import idol
from .. import util
from ..system import exchange
from ..system import user

from typing import Any


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list[exchange.ExchangePointInfo]


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
    cost_list: list[ExchangeCost]
    already_obtained: bool = False
    got_item_count: int = 0
    term_count: int = 0


class ExchangeItemWithExpiry(ExchangeItemBase):
    term_end_date: str


class ExchangeItemWithMaxCount(ExchangeItemBase):
    max_item_count: int


class ExchangeItemInfoResponse(ExchangePointResponse):
    exchange_item_info: list[pydantic.SerializeAsAny[ExchangeItemBase]]


@idol.register("exchange", "owningPoint")
async def exchange_owningpoint(context: idol.SchoolIdolUserParams) -> ExchangePointResponse:
    return ExchangePointResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context))
    )


@idol.register("exchange", "itemInfo")
async def exchange_iteminfo(context: idol.SchoolIdolUserParams) -> ExchangeItemInfoResponse:
    util.stub("exchange", "itemInfo")
    return ExchangeItemInfoResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context)),
        exchange_item_info=[],
    )
