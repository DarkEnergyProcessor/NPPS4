import pydantic

from .. import idol
from .. import util
from ..system import user


class BannerInfo(pydantic.BaseModel):
    banner_type: int
    target_id: int
    asset_path: str
    webview_url: str | None = None
    is_registered: bool | None = None
    fixed_flag: bool
    back_side: bool
    banner_id: int
    start_date: str
    end_date: str


class BannerListResponse(pydantic.BaseModel):
    time_limit: str
    banner_list: list[BannerInfo]


@idol.register("banner", "bannerList", exclude_none=True)
async def banner_bannerlist(context: idol.SchoolIdolUserParams) -> BannerListResponse:
    current_user = await user.get_current(context)
    # TODO
    util.stub("banner", "bannerList", context.raw_request_data)

    return BannerListResponse(
        time_limit=util.timestamp_to_datetime(2147483647),
        banner_list=[
            # SIF2 transfer banner
            BannerInfo(
                banner_type=18,
                target_id=1,
                asset_path=(
                    "en/assets/image/handover/banner/banner_01.png"
                    if context.lang == idol.Language.en
                    else "assets/image/handover/banner/banner_01.png"
                ),
                is_registered=current_user.transfer_sha1 is not None,
                fixed_flag=False,
                back_side=False,
                banner_id=1800002,
                start_date=util.timestamp_to_datetime(1476522000),
                end_date=util.timestamp_to_datetime(2147483647),
            ),
            # TenFes banner
            BannerInfo(
                banner_type=2,
                target_id=1,
                asset_path=(
                    "en/assets/image/webview/wv_ba_01.png"
                    if context.lang == idol.Language.en
                    else "assets/image/webview/wv_ba_01.png"
                ),
                webview_url="/",
                fixed_flag=False,
                back_side=True,
                banner_id=200001,
                start_date=util.timestamp_to_datetime(1476522000),
                end_date=util.timestamp_to_datetime(2147483647),
            ),
        ],
    )
