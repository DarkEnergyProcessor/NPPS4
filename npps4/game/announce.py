from .. import idol
from .. import util
from ..system import common


class AnnounceStateResponse(common.TimestampMixin):
    has_unread_announce: bool


@idol.register("announce", "checkState")
async def announce_checkstate(context: idol.SchoolIdolUserParams) -> AnnounceStateResponse:
    # TODO
    util.stub("announce", "checkState", context.raw_request_data)
    return AnnounceStateResponse(has_unread_announce=False)
