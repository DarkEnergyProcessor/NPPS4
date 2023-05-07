from .. import idol
from .. import util

import pydantic


class BackgroundInfo(pydantic.BaseModel):
    background_id: int
    is_set: bool
    insert_date: str


class BackgroundInfoResponse(pydantic.BaseModel):
    background_info: list[BackgroundInfo]


@idol.register("/background/backgroundInfo")
def background_backgroundinfo(context: idol.SchoolIdolUserParams) -> BackgroundInfoResponse:
    # TODO
    util.log("STUB /background/backgroundInfo", severity=util.logging.WARNING)
    return BackgroundInfoResponse(
        background_info=[
            BackgroundInfo(background_id=1, is_set=True, insert_date=util.timestamp_to_datetime(1365984000))
        ]
    )
