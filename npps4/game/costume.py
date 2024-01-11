from .. import idol
from .. import util

import pydantic


class CustomeListResponse(pydantic.BaseModel):
    costume_list: list


@idol.register("costume", "costumeList")
async def costume_costumelist(context: idol.SchoolIdolUserParams) -> CustomeListResponse:
    # TODO
    util.stub("costume", "costumeList", context.raw_request_data)
    return CustomeListResponse(costume_list=[])
