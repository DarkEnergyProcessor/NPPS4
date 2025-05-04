import pydantic

from . import models
from .. import idol
from .. import util
from ..system import common
from ..system import ranking
from ..system import reward
from ..system import unit
from ..system import user


class PageableMixin(pydantic.BaseModel):
    page: int = 0


class RankingLiveRequest(PageableMixin):
    live_difficulty_id: int


class RankingPlayerRequest(PageableMixin):
    id: int = 0  # if nonzero, get current player position
    term: int  # Always 1
    daily_index: int  # 1 = today, 2 = yesterday


class RankingUserData(pydantic.BaseModel):
    user_id: int
    name: str
    level: int


class RankingData(pydantic.BaseModel):
    rank: int
    score: int
    user_data: models.UserData
    center_unit_info: common.CenterUnitInfo
    setting_award_id: int


class RankingResponse(common.TimestampMixin, PageableMixin):
    rank: int | None
    items: list[RankingData]
    total_cnt: int
    present_cnt: int


@idol.register("ranking", "live")
async def ranking_live(context: idol.SchoolIdolUserParams, request: RankingLiveRequest) -> RankingResponse:
    current_user = await user.get_current(context)
    total_cnt, player_scores = await ranking.get_live_ranking(context, request.live_difficulty_id, request.page)

    rank_player_scores: list[RankingData] = []
    for i, (user_id, score) in enumerate(player_scores, 1):
        # TODO: Deduplicate with partyInfo code
        target_user = await user.get(context, user_id)
        if target_user is None:
            continue

        # Get unit center info
        unit_center = await unit.get_unit_center(context, target_user)
        if unit_center is None:
            continue

        unit_data = await unit.get_unit(context, unit_center)
        unit.validate_unit(target_user, unit_data)
        unit_info = await unit.get_unit_info(context, unit_data.unit_id)
        if unit_info is None:
            continue

        removable_skills = await unit.get_unit_removable_skills(context, unit_data)
        unit_full_data, unit_stats = await unit.get_unit_data_full_info(context, unit_data)

        rank_player_scores.append(
            RankingData(
                rank=i,
                score=score,
                user_data=models.UserData(user_id=user_id, name=target_user.name, level=target_user.level),
                center_unit_info=common.CenterUnitInfo(
                    unit_id=unit_data.unit_id,
                    level=unit_full_data.level,
                    rank=unit_data.rank,
                    love=unit_data.love,
                    display_rank=unit_data.display_rank,
                    unit_skill_exp=unit_data.skill_exp,
                    unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
                    smile=unit_stats.smile,
                    cute=unit_stats.pure,
                    cool=unit_stats.cool,
                    is_love_max=unit_full_data.is_love_max,
                    is_level_max=unit_full_data.is_level_max,
                    is_rank_max=unit_full_data.is_rank_max,
                    removable_skill_ids=removable_skills,
                ),
                setting_award_id=target_user.active_award,
            )
        )

    return RankingResponse(
        page=request.page,
        rank=None,
        items=rank_player_scores,
        total_cnt=total_cnt,
        present_cnt=await reward.count_presentbox(context, current_user),
    )


@idol.register("ranking", "player")
async def ranking_player(context: idol.SchoolIdolUserParams, request: RankingPlayerRequest) -> RankingResponse:
    current_user = await user.get_current(context)

    if request.id > 0:
        util.stub("ranking", "player", request)
        raise idol.error.by_code(idol.error.ERROR_CODE_USER_NOT_EXIST)

    rankings, total_count = await ranking.get_daily_ranking(context, request.page, request.daily_index == 2)
    items: list[RankingData] = []
    current_rank: int | None = None

    for i, rank in enumerate(rankings, request.page * 20 + 1):
        target_user = await user.get(context, rank.user_id)
        if target_user is None:
            continue

        if rank.user_id == current_user.id:
            current_rank = i

        # Get unit center info
        unit_center = await unit.get_unit_center(context, target_user)
        if unit_center is None:
            continue

        unit_data = await unit.get_unit(context, unit_center)
        unit.validate_unit(target_user, unit_data)
        unit_info = await unit.get_unit_info(context, unit_data.unit_id)
        if unit_info is None:
            continue

        removable_skills = await unit.get_unit_removable_skills(context, unit_data)
        unit_full_data, unit_stats = await unit.get_unit_data_full_info(context, unit_data)

        items.append(
            RankingData(
                rank=i,
                score=rank.score,
                user_data=models.UserData(user_id=rank.user_id, name=target_user.name, level=target_user.level),
                center_unit_info=common.CenterUnitInfo(
                    unit_id=unit_data.unit_id,
                    level=unit_full_data.level,
                    rank=unit_data.rank,
                    love=unit_data.love,
                    display_rank=unit_data.display_rank,
                    unit_skill_exp=unit_data.skill_exp,
                    unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
                    smile=unit_stats.smile,
                    cute=unit_stats.pure,
                    cool=unit_stats.cool,
                    is_love_max=unit_full_data.is_love_max,
                    is_level_max=unit_full_data.is_level_max,
                    is_rank_max=unit_full_data.is_rank_max,
                    removable_skill_ids=removable_skills,
                ),
                setting_award_id=target_user.active_award,
            )
        )

    if len(items) == 0:
        raise idol.error.by_code(idol.error.ERROR_CODE_OUT_OF_RANG)

    return RankingResponse(
        page=request.page,
        rank=current_rank,
        items=items,
        total_cnt=total_count,
        present_cnt=await reward.count_presentbox(context, current_user),
    )
