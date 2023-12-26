import pydantic

from .. import idol
from ..idol.system import museum
from ..idol.system import user


class MuseumInfoResponse(pydantic.BaseModel):
    museum_info: museum.MuseumInfoData


@idol.register("/museum/info")
async def museum_info(context: idol.SchoolIdolUserParams) -> MuseumInfoResponse:
    current_user = await user.get_current(context)
    return MuseumInfoResponse(museum_info=await museum.get_museum_info_data(context, current_user))
