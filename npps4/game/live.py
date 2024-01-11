import itertools

import pydantic

from .. import idol
from .. import util
from ..idol.system import advanced
from ..idol.system import live
from ..idol.system import museum
from ..idol.system import unit
from ..idol.system import user


class EventInfo(pydantic.BaseModel):
    event_id: int
    event_category_id: int
    name: str
    open_date: str
    start_date: str
    end_date: str
    close_date: str
    banner_asset_name: str
    description: str
    member_category: int


class LimitedLive(pydantic.BaseModel):
    live_difficulty_id: int
    start_date: str
    end_date: str
    is_random: bool


class LimitedLiveBonus(pydantic.BaseModel):
    live_type: int
    limited_bonus_type: int
    limited_bonus_value: int
    start_date: str
    end_date: str


class RandomLive(pydantic.BaseModel):
    attribute_id: int
    start_date: str
    end_date: str


class TrainingLive(pydantic.BaseModel):
    live_difficulty_id: int
    start_date: str
    is_random: bool


class LiveScheduleResponse(pydantic.BaseModel):
    event_list: list[EventInfo]
    live_list: list[LimitedLive]
    limited_bonus_list: list
    limited_bonus_common_list: list[LimitedLiveBonus]
    random_live_list: list[RandomLive]
    free_live_list: list
    training_live_list: list[TrainingLive]


class LiveStatus(pydantic.BaseModel):
    live_difficulty_id: int
    status: int
    hi_score: int
    hi_combo_count: int
    clear_cnt: int
    achieved_goal_id_list: list[int]


class LiveStatusResponse(pydantic.BaseModel):
    normal_live_status_list: list
    special_live_status_list: list
    training_live_status_list: list
    marathon_live_status_list: list
    free_live_status_list: list
    can_resume_live: bool


class LivePartyListRequest(pydantic.BaseModel):
    is_training: bool
    lp_factor: int


class LivePartyListResponse(pydantic.BaseModel):
    party_list: list[advanced.PartyInfo]
    training_energy: int
    training_energy_max: int
    server_timestamp: int = pydantic.Field(default_factory=util.time)


class LivePlayRequest(pydantic.BaseModel):
    party_user_id: int
    is_training: bool
    unit_deck_id: int
    live_difficulty_id: int
    lp_factor: int


class LivePlayList(pydantic.BaseModel):
    live_info: live.LiveInfo
    deck_info: advanced.LiveDeckInfo


class LivePlayRankInfo(pydantic.BaseModel):
    rank: int
    rank_min: int
    rank_max: int


class LivePlayResponse(pydantic.BaseModel):
    rank_info: list[LivePlayRankInfo]
    energy_full_time: str
    over_max_energy: int
    available_live_resume: bool = False
    live_list: list[LivePlayList]
    is_marathon_event: bool = False
    marathon_event_id: int | None = None
    no_skill: bool = False
    can_activate_effect: bool = True
    server_timestamp: int = pydantic.Field(default_factory=util.time)


@idol.register("/live/liveStatus")
async def live_livestatus(context: idol.SchoolIdolUserParams) -> LiveStatusResponse:
    # TODO
    util.log("STUB /live/liveStatus", severity=util.logging.WARNING)
    return LiveStatusResponse(
        normal_live_status_list=[
            LiveStatus(
                live_difficulty_id=i, status=2, hi_score=0, hi_combo_count=0, clear_cnt=0, achieved_goal_id_list=[]
            )
            for i in itertools.chain(range(1, 4), (350,), range(1190, 1226))
        ],
        special_live_status_list=[],
        training_live_status_list=[],
        marathon_live_status_list=[],
        free_live_status_list=[],
        can_resume_live=False,
    )


@idol.register("/live/schedule")
async def live_schedule(context: idol.SchoolIdolUserParams) -> LiveScheduleResponse:
    # TODO
    util.log("STUB /live/schedule", severity=util.logging.WARNING)
    return LiveScheduleResponse(
        event_list=[],
        live_list=[],
        limited_bonus_list=[],
        limited_bonus_common_list=[],
        random_live_list=[
            RandomLive(
                attribute_id=i,
                start_date=util.timestamp_to_datetime(0),
                end_date=util.timestamp_to_datetime(2147483647),
            )
            for i in range(1, 4)
        ],
        free_live_list=[],
        training_live_list=[],
    )


@idol.register("/live/partyList")
async def live_partylist(context: idol.SchoolIdolUserParams, request: LivePartyListRequest):
    current_user = await user.get_current(context)
    util.stub("live", "partyList", request)

    # TODO: Check LP/token

    party_list = [await advanced.get_user_guest_party_info(context, current_user)]

    return LivePartyListResponse(
        # TODO
        party_list=party_list,
        training_energy=current_user.training_energy,
        training_energy_max=current_user.training_energy_max,
    )


@idol.register("/live/preciseScore")
async def live_precisescore(context: idol.SchoolIdolUserParams) -> idol.core.DummyModel:
    util.stub("live", "preciseScore", context.raw_request_data)
    raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_PRECISE_LIST_NOT_FOUND, 600)


@idol.register("/live/play", xmc_verify=idol.XMCVerifyMode.CROSS)
async def live_play(context: idol.SchoolIdolUserParams, request: LivePlayRequest) -> LivePlayResponse:
    current_user = await user.get_current(context)
    live_setting = await live.get_live_setting_from_difficulty_id(context, request.live_difficulty_id)
    if live_setting is None:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_NOT_FOUND, 600)

    # TODO: Check and consume LP/token

    beatmap_data = await live.get_live_info(context, request.live_difficulty_id, live_setting)
    if beatmap_data is None:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_NOTES_LIST_NOT_FOUND, 600)

    deck_data = await unit.load_unit_deck(context, current_user, request.unit_deck_id)
    if deck_data is None or 0 in deck_data[1]:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_UNIT_DECK)

    guest = await user.get(context, request.party_user_id)
    if guest is None:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_PARTY_USER)

    guest_center = await unit.get_unit_center(context, guest)
    if guest_center is None or guest_center.unit_id == 0:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_PARTY_USER)

    calculator = advanced.TeamStatCalculator(context)
    museum_data = await museum.get_museum_info_data(context, current_user)
    deck_units = [await unit.get_unit(context, i) for i in deck_data[1]]
    stats = await calculator.get_live_stats(
        request.unit_deck_id, deck_units, await unit.get_unit(context, guest_center.unit_id), museum_data.parameter
    )

    return LivePlayResponse(
        rank_info=[
            LivePlayRankInfo(rank=5, rank_min=0, rank_max=live_setting.c_rank_score - 1),
            LivePlayRankInfo(rank=4, rank_min=live_setting.c_rank_score, rank_max=live_setting.b_rank_score - 1),
            LivePlayRankInfo(rank=3, rank_min=live_setting.b_rank_score, rank_max=live_setting.a_rank_score - 1),
            LivePlayRankInfo(rank=2, rank_min=live_setting.a_rank_score, rank_max=live_setting.s_rank_score - 1),
            LivePlayRankInfo(rank=1, rank_min=live_setting.s_rank_score, rank_max=0),
        ],
        energy_full_time=util.timestamp_to_datetime(current_user.energy_full_time),
        over_max_energy=current_user.over_max_energy,
        # TODO: Medley Festival
        live_list=[LivePlayList(live_info=beatmap_data, deck_info=stats)],
    )


@idol.register("/live/gameover")
async def live_gameover(context: idol.SchoolIdolUserParams):
    util.stub("live", "gameover", context.raw_request_data)
    return idol.core.DummyModel()
