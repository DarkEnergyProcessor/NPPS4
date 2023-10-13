from .. import idol
from .. import util

import pydantic


class LiveIconInfoResponse(pydantic.BaseModel):
    live_notes_icon_list: list[int]


@idol.register("/liveicon/liveiconInfo")
async def liveicon_liveiconinfo(context: idol.SchoolIdolUserParams) -> LiveIconInfoResponse:
    # TODO
    util.log("STUB /liveicon/liveiconInfo", severity=util.logging.WARNING)
    return LiveIconInfoResponse(live_notes_icon_list=[1, 2, 3])
