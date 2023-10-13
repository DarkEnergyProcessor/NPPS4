from .. import idol
from .. import util

import pydantic


@idol.register("/navigation/specialCutin")
async def navigation_specialcutin(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /navigation/specialCutin", severity=util.logging.WARNING)
    return pydantic.BaseModel()
