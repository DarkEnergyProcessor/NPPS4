from .. import idol
from .. import util

import pydantic


@idol.register("/costume/costumeList")
def custome_customelist(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /costume/costumeList", severity=util.logging.WARNING)
    return pydantic.BaseModel()
