import pydantic

from .. import idol
from ..system import exchange
from ..system import user


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list[exchange.ExchangePointInfo]


class ExchangeItemInfoResponse(ExchangePointResponse):
    exchange_item_info: list[pydantic.SerializeAsAny[exchange.ExchangeItemBase]]


@idol.register("exchange", "owningPoint")
async def exchange_owningpoint(context: idol.SchoolIdolUserParams) -> ExchangePointResponse:
    return ExchangePointResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context))
    )


@idol.register("exchange", "itemInfo")
async def exchange_iteminfo(context: idol.SchoolIdolUserParams) -> ExchangeItemInfoResponse:
    current_user = await user.get_current(context)
    return ExchangeItemInfoResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context)),
        exchange_item_info=await exchange.get_exchange_item_info(context, current_user),
    )
