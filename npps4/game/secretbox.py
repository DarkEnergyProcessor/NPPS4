from .. import idol
from .. import util

import pydantic


class LiveIconInfoResponse(pydantic.BaseModel):
    live_notes_icon_list: list[int]


@idol.register("secretbox", "all")
async def secretbox_all(context: idol.SchoolIdolUserParams) -> idol.core.DummyModel:
    # TODO
    util.stub("secretbox", "all")
    raise idol.error.by_code(idol.error.ERROR_CODE_LIB_ERROR)
