from .. import idol
from .. import util

import pydantic


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list


@idol.register("/exchange/owningPoint")
async def exchange_owningpoint(context: idol.SchoolIdolUserParams) -> ExchangePointResponse:
    # TODO
    util.log("STUB /exchange/owningPoint", severity=util.logging.WARNING)
    return ExchangePointResponse(exchange_point_list=[])
