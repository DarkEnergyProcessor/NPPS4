from .. import idol
from .. import util

import pydantic


class LiveSEInfoResponse(pydantic.BaseModel):
    live_se_list: list[int]


@idol.register("/livese/liveseInfo")
def livese_liveseinfo(context: idol.SchoolIdolUserParams) -> LiveSEInfoResponse:
    # TODO
    util.log("STUB /livese/liveseInfo", severity=util.logging.WARNING)
    return LiveSEInfoResponse(live_se_list=[1, 2, 3])
