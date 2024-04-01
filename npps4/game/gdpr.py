from .. import idol
from .. import util
from ..system import common


class GDPRGetResponse(common.TimestampMixin):
    enable_gdpr: bool
    is_eea: bool


@idol.register("gdpr", "get")
async def gdpr_get(context: idol.SchoolIdolUserParams) -> GDPRGetResponse:
    # TODO
    util.stub("gdpr", "get", context.raw_request_data)
    return GDPRGetResponse(enable_gdpr=True, is_eea=False)
