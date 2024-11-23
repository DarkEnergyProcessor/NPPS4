import pydantic

from . import models
from .. import idol
from .. import util
from ..system import common
from ..system import reward
from ..system import user


class PageableMixin(pydantic.BaseModel):
    page: int = 0


class RankingLiveRequest(PageableMixin):
    live_difficulty_id: int


class RankingPlayerRequest(PageableMixin):
    id: int = 0
    term: int
    daily_index: int


class RankingUserData(pydantic.BaseModel):
    user_id: int
    name: str
    level: int


class RankingData(pydantic.BaseModel):
    rank: int
    score: int
    user_data: models.UserData
    center_unit_info: models.CenterUnitInfo
    setting_award_id: int


class RankingResponse(common.TimestampMixin, PageableMixin):
    rank: int | None
    items: list[RankingData]
    total_cnt: int
    present_cnt: int


@idol.register("ranking", "live")
async def ranking_live(context: idol.SchoolIdolUserParams, request: RankingLiveRequest) -> RankingResponse:
    current_user = await user.get_current(context)
    util.stub("ranking", "live", request)
    return RankingResponse(
        page=request.page,
        rank=None,
        items=[],
        total_cnt=0,
        present_cnt=await reward.count_presentbox(context, current_user),
    )


@idol.register("ranking", "player")
async def ranking_player(context: idol.SchoolIdolUserParams, request: RankingPlayerRequest) -> RankingResponse:
    current_user = await user.get_current(context)
    util.stub("ranking", "player", request)
    return RankingResponse(
        page=request.page,
        rank=None,
        items=[],
        total_cnt=0,
        present_cnt=await reward.count_presentbox(context, current_user),
    )
