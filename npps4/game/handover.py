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


@idol.register("/handover/exec", batchable=False)
def handover_exec(context: idol.SchoolIdolUserParams, request: HandoverExecRequest):
    util.log("STUB /handover/exec", request, severity=util.logging.WARNING)
    raise error.IdolError(error.ERROR_HANDOVER_INVALID_ID_OR_CODE, 600)


@idol.register("/handover/kidInfo")
def handover_kidinfo(context: idol.SchoolIdolUserParams) -> KIDInfoResponse:
    util.log("STUB /handover/kidInfo", severity=util.logging.WARNING)
    return KIDInfoResponse(auth_url=str(context.request.url), server_timestamp=util.time())
