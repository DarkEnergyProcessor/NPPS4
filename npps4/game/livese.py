from .. import idol
from .. import util

import pydantic


class LiveSEInfoResponse(pydantic.BaseModel):
    live_se_list: list[int]


@idol.register("livese", "liveseInfo")
async def livese_liveseinfo(context: idol.SchoolIdolUserParams) -> LiveSEInfoResponse:
    # TODO
    util.stub("livese", "liveseInfo", context.raw_request_data)
    return LiveSEInfoResponse(live_se_list=[1, 2, 3, 99])
