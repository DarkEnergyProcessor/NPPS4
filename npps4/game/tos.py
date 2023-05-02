from .. import idol
from .. import util

import pydantic


class TOSCheckResponse(pydantic.BaseModel):
    tos_id: int
    tos_type: int
    server_timestamp: int


class TOSAgreeRequest(pydantic.BaseModel):
    tos_id: int


@idol.register("/tos/tosCheck")
def tos_toscheck(context: idol.SchoolIdolUserParams) -> TOSCheckResponse:
    return TOSCheckResponse(tos_id=1, tos_type=1, server_timestamp=util.time())


@idol.register("/tos/tosAgree")
def tos_tosagree(context: idol.SchoolIdolUserParams, request: TOSAgreeRequest) -> pydantic.BaseModel:
    return pydantic.BaseModel()
