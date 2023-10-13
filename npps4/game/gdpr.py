from .. import idol
from .. import util

import pydantic


class GDPRGetResponse(pydantic.BaseModel):
    enable_gdpr: bool
    is_eea: bool
    server_timestamp: int


@idol.register("/gdpr/get")
async def gdpr_get(context: idol.SchoolIdolUserParams) -> GDPRGetResponse:
    # TODO
    util.log("STUB /gdpr/get", severity=util.logging.WARNING)
    return GDPRGetResponse(enable_gdpr=True, is_eea=False, server_timestamp=util.time())
