from .. import idol
from .. import util
from ..idol.system import background
from ..idol.system import user

import pydantic


class BackgroundInfo(pydantic.BaseModel):
    background_id: int
    is_set: bool
    insert_date: str


class BackgroundInfoResponse(pydantic.BaseModel):
    background_info: list[BackgroundInfo]


@idol.register("/background/backgroundInfo")
async def background_backgroundinfo(context: idol.SchoolIdolUserParams) -> BackgroundInfoResponse:
    current_user = await user.get_current(context)
    backgrounds = await background.get_backgrounds(context, current_user)
    background_info = [
        BackgroundInfo(
            background_id=bg.background_id,
            is_set=current_user.active_background == bg.background_id,
            insert_date=util.timestamp_to_datetime(bg.insert_date),
        )
        for bg in backgrounds
    ]

    return BackgroundInfoResponse(background_info=background_info)
