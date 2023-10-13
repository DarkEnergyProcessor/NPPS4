from .. import idol
from .. import util

import pydantic


@idol.register("/album/albumAll")
async def album_albumall(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /album/albumAll", severity=util.logging.WARNING)
    return pydantic.BaseModel()
