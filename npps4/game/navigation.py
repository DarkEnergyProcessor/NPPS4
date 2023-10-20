import pydantic

from .. import idol
from .. import util


class NavigationSpecialCutInResponse(pydantic.BaseModel):
    special_cutin_list: list  # TODO


@idol.register("/navigation/specialCutin")
async def navigation_specialcutin(context: idol.SchoolIdolUserParams) -> NavigationSpecialCutInResponse:
    # TODO
    util.log("STUB /navigation/specialCutin", severity=util.logging.WARNING)
    return NavigationSpecialCutInResponse(special_cutin_list=[])
