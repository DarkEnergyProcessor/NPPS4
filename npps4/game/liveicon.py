from .. import idol
from .. import util

import pydantic


class LiveIconInfoResponse(pydantic.BaseModel):
    live_notes_icon_list: list[int]


@idol.register("liveicon", "liveiconInfo")
async def liveicon_liveiconinfo(context: idol.SchoolIdolUserParams) -> LiveIconInfoResponse:
    # TODO
    util.stub("liveicon", "liveiconInfo", context.raw_request_data)
    return LiveIconInfoResponse(live_notes_icon_list=[1, 2, 3])
