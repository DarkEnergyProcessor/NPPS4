from .. import idol
from .. import util

import pydantic


@idol.register("/marathon/marathonInfo")
async def marathon_marathoninfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /marathon/marathonInfo", severity=util.logging.WARNING)
    return pydantic.BaseModel()
