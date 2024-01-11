import pydantic

from .. import idol
from .. import util


class PersonalNoticeGetResponse(pydantic.BaseModel):
    has_notice: bool
    notice_id: int
    type: int
    title: str
    contents: str


@idol.register("personalnotice", "get")
async def personalnotice_get(context: idol.SchoolIdolUserParams) -> PersonalNoticeGetResponse:
    # https://github.com/DarkEnergyProcessor/NPPS/blob/v3.1.x/modules/personalnotice/get.php
    # TODO
    util.stub("personalnotice", "get", context.raw_request_data)
    return PersonalNoticeGetResponse(has_notice=False, notice_id=0, type=0, title="", contents="")
