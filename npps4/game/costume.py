from .. import idol
from .. import util

import pydantic


class CustomeListResponse(pydantic.BaseModel):
    costume_list: list


@idol.register("/costume/costumeList")
def custome_customelist(context: idol.SchoolIdolUserParams) -> CustomeListResponse:
    # TODO
    util.log("STUB /costume/costumeList", severity=util.logging.WARNING)
    return CustomeListResponse(costume_list=[])
