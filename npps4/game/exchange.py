import pydantic

from .. import idol
from .. import util
from ..system import common
from ..system import exchange
from ..system import user


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list[exchange.ExchangePointInfo]


class ExchangeItemInfoResponse(ExchangePointResponse):
    exchange_item_info: list[pydantic.SerializeAsAny[common.AnyItem]]


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
