from .. import idol
from .. import util

import pydantic


class NoticeMarquee(pydantic.BaseModel):
    # https://github.com/DarkEnergyProcessor/NPPS/blob/v3.1.x/modules/notice/noticeMarquee.php
    marquee_id: int
    text: str
    text_color: int
    display_place: int
    start_date: str
    end_date: str


class NoticeMarqueeResponse(pydantic.BaseModel):
    item_count: int
    marquee_list: list[NoticeMarquee]


@idol.register("notice", "noticeMarquee")
async def notice_noticemarquee(context: idol.SchoolIdolUserParams) -> NoticeMarqueeResponse:
    # TODO
    util.stub("notice", "noticeMarquee", context.raw_request_data)
    return NoticeMarqueeResponse(item_count=0, marquee_list=[])
