import pydantic

from .. import idol
from .. import util


class NavigationSpecialCutInResponse(pydantic.BaseModel):
    special_cutin_list: list  # TODO


@idol.register("navigation", "specialCutin")
async def navigation_specialcutin(context: idol.SchoolIdolUserParams) -> NavigationSpecialCutInResponse:
    # TODO
    util.stub("navigation", "specialCutin", context.raw_request_data)
    return NavigationSpecialCutInResponse(special_cutin_list=[])
