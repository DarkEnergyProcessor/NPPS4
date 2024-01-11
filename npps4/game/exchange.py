from .. import idol
from .. import util

import pydantic


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list


@idol.register("exchange", "owningPoint")
async def exchange_owningpoint(context: idol.SchoolIdolUserParams) -> ExchangePointResponse:
    # TODO
    util.stub("exchange", "owningPoint", context.raw_request_data)
    return ExchangePointResponse(exchange_point_list=[])
