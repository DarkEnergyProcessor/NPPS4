from .. import idol
from .. import util

import pydantic


class MuseumParameter(pydantic.BaseModel):
    smile: int
    pure: int
    cool: int


class MuseumInfo(pydantic.BaseModel):
    parameter: MuseumParameter
    contents_id_list: list[int]


class MuseumInfoResponse(pydantic.BaseModel):
    museum_info: MuseumInfo


@idol.register("/museum/info")
async def museum_info(context: idol.SchoolIdolUserParams) -> MuseumInfoResponse:
    # TODO
    util.log("STUB /museum/info", severity=util.logging.WARNING)
    return MuseumInfoResponse(
        museum_info=MuseumInfo(parameter=MuseumParameter(smile=0, pure=0, cool=0), contents_id_list=[])
    )
