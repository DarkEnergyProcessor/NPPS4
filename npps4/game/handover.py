from .. import idol
from .. import util
from ..idol import error

import pydantic


class HandoverExecRequest(pydantic.BaseModel):
    handover_code: str
    handover_id: str


class KIDInfoResponse(pydantic.BaseModel):
    auth_url: str
    server_timestamp: int


class KIDStatusResponse(pydantic.BaseModel):
    has_klab_id: bool
    server_timestamp: int


@idol.register("/handover/exec", batchable=False)
async def handover_exec(context: idol.SchoolIdolUserParams, request: HandoverExecRequest) -> pydantic.BaseModel:
    # TODO
    util.log("STUB /handover/exec", request, severity=util.logging.WARNING)
    raise error.IdolError(error.ERROR_HANDOVER_INVALID_ID_OR_CODE, 600)


@idol.register("/handover/kidInfo")
async def handover_kidinfo(context: idol.SchoolIdolUserParams) -> KIDInfoResponse:
    # TODO
    util.log("STUB /handover/kidInfo", severity=util.logging.WARNING)
    raise error.IdolError(error.ERROR_KLAB_ID_SERVICE_MAINTENANCE, 600)
    # return KIDInfoResponse(auth_url=str(context.request.url), server_timestamp=util.time())


@idol.register("/handover/kidStatus")
async def handover_kidstatus(context: idol.SchoolIdolUserParams) -> KIDStatusResponse:
    # TODO
    util.log("STUB /handover/kidStatus", severity=util.logging.WARNING)
    return KIDStatusResponse(has_klab_id=False, server_timestamp=util.time())
