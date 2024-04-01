import pydantic

from .. import idol
from .. import util
from ..system import common


class HandoverExecRequest(pydantic.BaseModel):
    handover_code: str
    handover_id: str


class KIDInfoResponse(common.TimestampMixin):
    auth_url: str


class KIDStatusResponse(common.TimestampMixin):
    has_klab_id: bool


@idol.register("handover", "exec", batchable=False)
async def handover_exec(context: idol.SchoolIdolUserParams, request: HandoverExecRequest) -> None:
    # TODO
    util.stub("handover", "exec", request)
    raise idol.error.by_code(idol.error.ERROR_HANDOVER_INVALID_ID_OR_CODE)


@idol.register("handover", "kidInfo")
async def handover_kidinfo(context: idol.SchoolIdolUserParams) -> KIDInfoResponse:
    # TODO
    util.stub("handover", "kidInfo", context.raw_request_data)
    raise idol.error.by_code(idol.error.ERROR_KLAB_ID_SERVICE_MAINTENANCE)
    # return KIDInfoResponse(auth_url=str(context.request.url))


@idol.register("handover", "kidStatus")
async def handover_kidstatus(context: idol.SchoolIdolUserParams) -> KIDStatusResponse:
    # TODO
    util.stub("handover", "kidStatus", context.raw_request_data)
    return KIDStatusResponse(has_klab_id=False)
