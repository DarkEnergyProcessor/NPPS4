from .. import idol
from .. import util

import pydantic


class BannerInfo(pydantic.BaseModel):
    banner_type: int
    target_id: int
    asset_path: str
    webview_url: str
    fixed_flag: bool
    back_side: bool
    banner_id: int
    start_date: str
    end_date: str


class BannerListResponse(pydantic.BaseModel):
    time_limit: str
    banner_list: list[BannerInfo]


@idol.register("/banner/bannerList")
def banner_bannerlist(context: idol.SchoolIdolUserParams) -> BannerListResponse:
    # TODO
    util.log("STUB /banner/bannerList", severity=util.logging.WARNING)
    return BannerListResponse(
        time_limit=util.timestamp_to_datetime(2147483647),
        banner_list=[
            # TenFes banner
            BannerInfo(
                banner_type=2,
                target_id=1,
                asset_path="en/assets/image/webview/wv_ba_01.png",
                webview_url=str(context.request.url),
                fixed_flag=False,
                back_side=True,
                banner_id=200001,
                start_date=util.timestamp_to_datetime(1476522000),
                end_date=util.timestamp_to_datetime(2147483647),
            )
        ],
    )
