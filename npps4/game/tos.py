from .. import idol
from .. import util
from ..idol import error
from ..system import tos
from ..system import user

import pydantic


class TOSCheckResponse(pydantic.BaseModel):
    tos_id: int
    tos_type: int
    is_agreed: bool
    server_timestamp: int


class TOSAgreeRequest(pydantic.BaseModel):
    tos_id: int


@idol.register("tos", "tosCheck")
async def tos_toscheck(context: idol.SchoolIdolUserParams) -> TOSCheckResponse:
    current_user = await user.get_current(context)
    agree = await tos.is_agreed(context, current_user, 1)
    return TOSCheckResponse(tos_id=1, tos_type=1, is_agreed=agree, server_timestamp=util.time())


@idol.register("tos", "tosAgree", batchable=False)
async def tos_tosagree(context: idol.SchoolIdolUserParams, request: TOSAgreeRequest) -> None:
    if request.tos_id == 1:
        current_user = await user.get_current(context)
        if not await tos.is_agreed(context, current_user, 1):
            await tos.agree(context, current_user, 1)
            return

    raise error.IdolError(detail="Invalid ToS agreement")
