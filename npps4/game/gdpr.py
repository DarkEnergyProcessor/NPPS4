from .. import idol
from .. import util

import pydantic


class GDPRGetResponse(pydantic.BaseModel):
    enable_gdpr: bool
    is_eea: bool
    server_timestamp: int


@idol.register("/gdpr/get")
def gdpr_get(context: idol.SchoolIdolUserParams) -> GDPRGetResponse:
    return GDPRGetResponse(enable_gdpr=True, is_eea=False, server_timestamp=util.time())
