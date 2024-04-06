import pydantic

from .. import idol
from ..system import exchange
from ..system import user


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list[exchange.ExchangePointInfo]


@idol.register("exchange", "owningPoint")
async def exchange_owningpoint(context: idol.SchoolIdolUserParams) -> ExchangePointResponse:
    return ExchangePointResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context))
    )
