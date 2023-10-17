import pydantic

from .. import idol
from .. import util


class AnnounceStateResponse(pydantic.BaseModel):
    has_unread_announce: bool
    server_timestamp: int


@idol.register("/announce/checkState")
async def announce_checkstate(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /announce/checkState", severity=util.logging.WARNING)
    return AnnounceStateResponse(has_unread_announce=False, server_timestamp=util.time())
