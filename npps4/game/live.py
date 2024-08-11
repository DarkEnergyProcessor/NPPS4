import copy
import math

import pydantic

from .. import const
from .. import idol
from .. import util
from ..config import config
from ..system import achievement
from ..system import advanced
from ..system import album
from ..system import class_system as class_system_module
from ..system import common
from ..system import effort
from ..system import live
from ..system import live_model
from ..system import museum
from ..system import reward
from ..system import scenario
from ..system import subscenario
from ..system import unit
from ..system import unit_model
from ..system import user


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


class LiveStatusResponse(pydantic.BaseModel):
    normal_live_status_list: list[live_model.LiveStatus]
    special_live_status_list: list[live_model.LiveStatus]
    training_live_status_list: list[live_model.LiveStatus]
    marathon_live_status_list: list
    free_live_status_list: list
    can_resume_live: bool


class LivePartyListRequest(pydantic.BaseModel):
    live_difficulty_id: int
    is_training: bool
    lp_factor: int


class LivePartyListResponse(common.TimestampMixin):
    party_list: list[advanced.PartyInfo]
    training_energy: int
    training_energy_max: int


class LivePlayRequest(pydantic.BaseModel):
    party_user_id: int
    is_training: bool
    unit_deck_id: int
    live_difficulty_id: int
    lp_factor: int


class LivePlayList(pydantic.BaseModel):
    live_info: live_model.LiveInfoWithNotes
    deck_info: advanced.LiveDeckInfo


class LivePlayRankInfo(pydantic.BaseModel):
    rank: int
    rank_min: int
    rank_max: int


class LivePlayResponse(common.TimestampMixin):
    rank_info: list[LivePlayRankInfo]
    energy_full_time: str
    over_max_energy: int
    available_live_resume: bool = True
    live_list: list[LivePlayList]
    is_marathon_event: bool = False
    marathon_event_id: int | None = None
    no_skill: bool = False
    can_activate_effect: bool = True
    auto_play: bool = False


class LiveRewardPreciseList(pydantic.BaseModel):
    effect: int
    count: int
    tap: float
    note_number: float
    position: int
    accuracy: int
    is_same: bool

    tp: bool | None = None
    tpf: bool | None = None
    first_touch: int | None = None
    release: float | None = None


class LiveRewardTriggerLog(pydantic.BaseModel):
    activation_rate: int
    position: int


# https://github.com/YumeMichi/honoka-chan/blob/6778972c1ff54a8a038ea07b676e6acdbb211f96/handler/live.go#L447
# Along with some asking from other people.
class LivePreciseScoreData(pydantic.BaseModel):
    has_record: bool
    live_info: live_model.LiveInfo
    can_replay: bool = False
    random_seed: int = pydantic.Field(default_factory=util.time)
    max_combo: int
    update_date: str
    precise_list: list[LiveRewardPreciseList] | None = None
    deck_info: advanced.LiveDeckInfo | None = None
    tap_adjust: int | None = None
    trigger_log: list[LiveRewardTriggerLog] | None = None


class LivePreciseScoreResponse(common.TimestampMixin):
    rank_info: list[LivePlayRankInfo]
    on: LivePreciseScoreData
    off: LivePreciseScoreData
    can_activate_Effect: bool = False


class LiveRewardLiveSettingIcon(pydantic.BaseModel):
    slide_id: int
    just_id: int
    normal_id: int


class LiveRewardLiveSetting(pydantic.BaseModel):
    string_size: int
    precise_score_auto_update_flag: bool
    se_id: int
    cutin_brightness: int
    random_value: int
    precise_score_update_type: int
    effect_flag: int
    notes_speed: float
    icon: LiveRewardLiveSettingIcon
    cutin_type: int


class LiveRewardPreciseScore(pydantic.BaseModel):
    live_setting: LiveRewardLiveSetting
    tap_adjust: int
    precise_list: list[LiveRewardPreciseList]
    background_score: advanced.LiveDeckUnitAttribute
    is_log_on: bool
    score_log: list[int]
    is_skill_on: bool
    trigger_log: list[LiveRewardTriggerLog]
    random_seed: int


class LiveRewardRequest(pydantic.BaseModel):
    live_difficulty_id: int
    is_training: bool
    perfect_cnt: int
    great_cnt: int
    good_cnt: int
    bad_cnt: int
    miss_cnt: int
    remain_hp: int
    max_combo: int
    score_smile: int
    score_cute: int
    score_cool: int
    love_cnt: int
    precise_score_log: LiveRewardPreciseScore
    event_point: int
    event_id: int | None


class LiveRewardBaseInfo(common.BaseRewardInfo):
    player_exp: int
    player_exp_unit_max: common.BeforeAfter[int]
    player_exp_friend_max: common.BeforeAfter[int]
    player_exp_lp_max: common.BeforeAfter[int]
    social_point: int


class LiveRewardUnitList(pydantic.BaseModel):
    live_clear: list[common.AnyItem] = pydantic.Field(default_factory=list)
    live_rank: list[common.AnyItem] = pydantic.Field(default_factory=list)
    live_combo: list[common.AnyItem] = pydantic.Field(default_factory=list)


class LiveRewardResponseUnitList(pydantic.BaseModel):
    unit_owning_user_id: int
    unit_id: int
    position: int
    level: int
    level_limit_id: int
    display_rank: int
    unit_skill_level: int
    is_rank_max: bool
    is_love_max: bool
    is_level_max: bool
    is_signed: bool
    before_love: int
    love: int
    max_love: int

    @staticmethod
    def from_unit_data(unit_data_full: unit_model.UnitInfoData, *, position: int, before_love: int):
        return LiveRewardResponseUnitList(
            unit_owning_user_id=unit_data_full.unit_owning_user_id,
            unit_id=unit_data_full.unit_id,
            position=position,
            level=unit_data_full.level,
            level_limit_id=unit_data_full.level_limit_id,
            before_love=before_love,
            love=unit_data_full.love,
            max_love=unit_data_full.max_love,
            unit_skill_level=unit_data_full.unit_skill_level,
            display_rank=unit_data_full.display_rank,
            is_rank_max=unit_data_full.is_rank_max,
            is_love_max=unit_data_full.is_love_max,
            is_level_max=unit_data_full.is_level_max,
            is_signed=unit_data_full.is_signed,
        )


class LiveRewardGoalAccomplishedInfo(pydantic.BaseModel):
    achieved_ids: list[int]
    rewards: list[common.AnyItem]


class LiveRewardResponse(achievement.AchievementMixin, common.TimestampMixin, user.UserDiffMixin):
    live_info: list[live_model.LiveInfo]
    rank: int
    combo_rank: int
    total_love: int
    is_high_score: bool
    hi_score: int
    base_reward_info: LiveRewardBaseInfo
    reward_unit_list: LiveRewardUnitList
    unlocked_subscenario_ids: list[int]
    unlocked_multi_unit_scenario_ids: list[int] = pydantic.Field(default_factory=list)  # TODO
    effort_point: list[effort.EffortPointInfo]
    is_effort_point_visible: bool = True
    limited_effort_box: list = pydantic.Field(default_factory=list)  # TODO
    unit_list: list[LiveRewardResponseUnitList]
    next_level_info: list[user.NextLevelInfo]
    goal_accomp_info: LiveRewardGoalAccomplishedInfo
    special_reward_info: list[common.AnyItem]
    event_info: list = pydantic.Field(default_factory=list)  # TODO
    daily_reward_info: list[common.AnyItem] = pydantic.Field(default_factory=list)  # TODO
    can_send_friend_request: bool = False
    using_buff_info: list = pydantic.Field(default_factory=list)  # TODO
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    museum_info: museum.MuseumInfoData
    present_cnt: int


@idol.register("live", "liveStatus")
async def live_livestatus(context: idol.SchoolIdolUserParams) -> LiveStatusResponse:
    current_user = await user.get_current(context)
    return LiveStatusResponse(
        normal_live_status_list=await live.get_normal_live_clear_status(context, current_user),
        special_live_status_list=await live.get_special_live_status(context, current_user),
        training_live_status_list=await live.get_training_live_status(context, current_user),
        marathon_live_status_list=[],
        free_live_status_list=[],
        can_resume_live=True,
    )


@idol.register("live", "schedule")
async def live_schedule(context: idol.SchoolIdolUserParams) -> LiveScheduleResponse:
    ts = util.time()
    special_live_rotation = await live.get_special_live_rotation_difficulty_id(context)

    return LiveScheduleResponse(
        event_list=[],
        live_list=[
            LimitedLive(
                live_difficulty_id=live_difficulty_id,
                start_date=util.timestamp_to_datetime(util.get_next_day_timestamp(ts, ndays=0)),
                end_date=util.timestamp_to_datetime(util.get_next_day_timestamp(ts)),
                is_random=False,  # TODO
            )
            for live_difficulty_id in special_live_rotation.values()
        ],
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


DEBUG_SERVER_SCORE_CALCULATE = False
DEBUG_SERVER_CONSUME_LP = False


@idol.register("live", "partyList")
async def live_partylist(context: idol.SchoolIdolUserParams, request: LivePartyListRequest) -> LivePartyListResponse:
    current_user = await user.get_current(context)

    # Check LP
    live_info = await live.get_live_info_table(context, request.live_difficulty_id)
    if live_info is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_FOUND)
    if DEBUG_SERVER_CONSUME_LP:
        if live_info.capital_type == 2:
            # TODO
            raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_ENOUGH_EVENT_POINT)
        if live_info.capital_type == 1 and user.has_energy(current_user, live_info.capital_value * request.lp_factor):
            raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_ENOUGH_CURRENT_ENERGY)

    live_setting = await live.get_live_setting(context, live_info.live_setting_id)
    if live_setting is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_FOUND)

    beatmap_data = await live.get_live_info(context, request.live_difficulty_id, live_setting)
    if beatmap_data is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOTES_LIST_NOT_FOUND)

    party_list = [
        await advanced.get_user_guest_party_info(context, u)
        for u in await advanced.get_random_user_for_partylist(context, current_user)
    ]

    # DEBUG live score
    if DEBUG_SERVER_SCORE_CALCULATE:
        guest_center_unit_owning_user_id = await unit.get_unit_center(context, current_user)
        assert guest_center_unit_owning_user_id != 0
        museum_data = await museum.get_museum_info_data(context, current_user)

        for unit_deck_id in await unit.find_all_valid_deck_number_ids(context, current_user):
            deck_data = await unit.load_unit_deck(context, current_user, unit_deck_id)
            if deck_data is None or 0 in deck_data[1]:
                raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_UNIT_DECK)

            calculator = advanced.TeamStatCalculator(context)
            deck_units = [await unit.get_unit(context, i) for i in deck_data[1]]
            stats = await calculator.get_live_stats(
                unit_deck_id,
                deck_units,
                await unit.get_unit(context, guest_center_unit_owning_user_id),
                museum_data.parameter,
            )
            print("===== TEAM STAT CALCULATOR FOR", deck_data[0].name, "=====")
            print(stats)

    return LivePartyListResponse(
        # TODO
        party_list=party_list,
        training_energy=current_user.training_energy,
        training_energy_max=current_user.training_energy_max,
    )


@idol.register("live", "preciseScore")
async def live_precisescore(context: idol.SchoolIdolUserParams) -> LivePreciseScoreResponse:
    util.stub("live", "preciseScore", context.raw_request_data)
    raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_PRECISE_LIST_NOT_FOUND)


@idol.register("live", "play", xmc_verify=idol.XMCVerifyMode.CROSS)
async def live_play(context: idol.SchoolIdolUserParams, request: LivePlayRequest) -> LivePlayResponse:
    current_user = await user.get_current(context)

    # Check LP
    live_info = await live.get_live_info_table(context, request.live_difficulty_id)
    if live_info is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_FOUND)
    if DEBUG_SERVER_CONSUME_LP:
        cap_value = live_info.capital_value * request.lp_factor
        if live_info.capital_type == 2:
            # TODO
            raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_ENOUGH_EVENT_POINT)
        if live_info.capital_type == 1 and user.has_energy(current_user, cap_value):
            raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_ENOUGH_CURRENT_ENERGY)
        # Consume LP
        user.sub_energy(current_user, cap_value)

    live_setting = await live.get_live_setting_from_difficulty_id(context, request.live_difficulty_id)
    if live_setting is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_FOUND)

    beatmap_data = await live.get_live_info(context, request.live_difficulty_id, live_setting)
    if beatmap_data is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOTES_LIST_NOT_FOUND)

    deck_data = await unit.load_unit_deck(context, current_user, request.unit_deck_id)
    if deck_data is None or 0 in deck_data[1]:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_UNIT_DECK)

    guest = await user.get(context, request.party_user_id)
    if guest is None:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_PARTY_USER)

    guest_center_unit_owning_user_id = await unit.get_unit_center(context, guest)
    if guest_center_unit_owning_user_id == 0:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIVE_INVALID_PARTY_USER)

    calculator = advanced.TeamStatCalculator(context)
    museum_data = await museum.get_museum_info_data(context, current_user)
    deck_units = [await unit.get_unit(context, i) for i in deck_data[1]]
    stats = await calculator.get_live_stats(
        request.unit_deck_id,
        deck_units,
        await unit.get_unit(context, guest_center_unit_owning_user_id),
        museum_data.parameter,
    )

    # Register live in progress
    await live.register_live_in_progress(context, current_user, guest, request.lp_factor, request.unit_deck_id)

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


@idol.register("live", "gameover")
async def live_gameover(context: idol.SchoolIdolUserParams) -> None:
    current_user = await user.get_current(context)
    await live.clean_live_in_progress(context, current_user)


@idol.register("live", "reward")
async def live_reward(context: idol.SchoolIdolUserParams, request: LiveRewardRequest) -> LiveRewardResponse:
    # FIXME: Perform validation to keep cheaters away?
    # FIXME: Modularize this thing for MedFes, ChaFest, Score Match, etc.

    current_user = await user.get_current(context)
    live_in_progress = await live.get_live_in_progress(context, current_user)
    if live_in_progress is None:
        raise idol.error.IdolError(detail="attempt to finish live show without playing", http_code=403)

    live_difficulty_info = await live.get_live_info_table(context, request.live_difficulty_id)
    if live_difficulty_info is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_FOUND)

    live_setting = await live.get_live_setting_from_difficulty_id(context, request.live_difficulty_id)
    if live_setting is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_LIVE_NOT_FOUND)

    # Get old data
    live_clear_data = await live.get_live_clear_data(context, current_user, request.live_difficulty_id, True)
    old_live_clear_data = copy.copy(live_clear_data)
    old_user_info = await user.get_user_info(context, current_user)

    # Update live clear data
    score = request.score_smile + request.score_cute + request.score_cool
    live_clear_data.hi_score = max(live_clear_data.hi_score, score)
    live_clear_data.hi_combo_cnt = max(live_clear_data.hi_combo_cnt, request.max_combo)
    live_clear_data.clear_cnt = live_clear_data.clear_cnt + 1

    # Get accomplished live goals
    old_live_goals = set(await live.get_achieved_goal_id_list(context, old_live_clear_data))
    new_live_goals = set(await live.get_achieved_goal_id_list(context, live_clear_data))
    accomplished_live_goals = sorted(new_live_goals - old_live_goals)
    live_goal_rewards = await live.get_goal_rewards(context, accomplished_live_goals)
    score_rank, combo_rank, clear_rank = live.get_live_ranks(
        live_difficulty_info, live_setting, score, request.max_combo, live_clear_data.clear_cnt
    )

    # Give live goal rewards
    for reward_data in live_goal_rewards:
        await advanced.add_item(context, current_user, reward_data)

    # This is the intended EXP and G drop
    target_difficulty_index = min(max(live_setting.difficulty, 1), 4) - 1
    given_exp = const.LIVE_EXP_DROP[target_difficulty_index]
    given_g = const.LIVE_GOLD_DROP[target_difficulty_index][score_rank - 1]

    # Roll unit for live clear
    live_unit_drop_protocol = config.get_live_unit_drop_protocol()
    unit_id = await live_unit_drop_protocol.get_live_drop_unit(live_setting.live_setting_id, context)

    # FIXME: Drop different kinds of levels. Currently it's fixed at level 1.
    # FIXME: It does not show a new character screen. There must be a flag for it.
    live_clear_drop = await unit.quick_create_by_unit_add(context, current_user, unit_id)
    if request.max_combo >= live_setting.c_rank_combo:
        unit_id = await live_unit_drop_protocol.get_live_drop_unit(live_setting.live_setting_id, context)
        live_combo_drop = await unit.quick_create_by_unit_add(context, current_user, unit_id)
    else:
        live_combo_drop = None
    if score >= live_setting.c_rank_score:
        unit_id = await live_unit_drop_protocol.get_live_drop_unit(live_setting.live_setting_id, context)
        live_score_drop = await unit.quick_create_by_unit_add(context, current_user, unit_id)
    else:
        live_score_drop = None
        given_exp = math.ceil(given_exp / 2)

    # Add user EXP
    given_exp = given_exp * live_in_progress.lp_factor
    next_level_info = await user.add_exp(context, current_user, given_exp)
    current_user.game_coin = current_user.game_coin + given_g

    # Add units
    current_unit_count = await unit.count_units(context, current_user, True)
    for reward_data in (live_clear_drop, live_combo_drop, live_score_drop):
        if reward_data is not None:
            current_unit_count = await unit.process_quick_add(
                context,
                current_user,
                reward_data,
                current_unit_count=current_unit_count,
                reason_jp="FIXME live show reward JP text",
                reason_en="Live Show! Reward",
            )

    # Add bond
    love_count = request.love_cnt * live_in_progress.lp_factor
    before_after_loves = await unit.add_love_by_deck(context, current_user, live_in_progress.unit_deck_id, love_count)

    # Add live effort
    effort_result, offer_limited_effort = await effort.add_effort(
        context, current_user, score * live_in_progress.lp_factor
    )
    for eff in effort_result:
        for r in eff.rewards:
            add_result = await advanced.add_item(context, current_user, r)
            if not add_result.success:
                # TODO: Message
                await reward.add_item(
                    context, current_user, r, "FIXME: Live Show! Clear message for JP", "Live Show! Clear"
                )
                r.reward_box_flag = True

    # Get current deck
    current_deck = await unit.load_unit_deck(context, current_user, live_in_progress.unit_deck_id)
    subscenario_unlocks: list[int] = []
    assert current_deck is not None
    unit_types_in_deck: set[int] = set()
    unit_deck_full_info: list[unit_model.UnitInfoData] = []
    unit_deck_unit_ids: list[int] = []
    for unit_owning_user_id in current_deck[1]:
        unit_data = await unit.get_unit(context, unit_owning_user_id)
        unit.validate_unit(current_user, unit_data)

        unit_info = await unit.get_unit_info(context, unit_data.unit_id)
        if unit_info is None:
            raise ValueError("invalid unit_info (is db corrupt?)")
        unit_types_in_deck.add(unit_info.unit_type_id)

        # Try to unlock subscenario
        unit_rarity = await unit.get_unit_rarity(context, unit_info.rarity)
        if unit_rarity is None:
            raise ValueError("invalid unit_rarity (is db corrupt?)")

        if unit_data.love >= unit_rarity.after_love_max:
            subscenario_id = await subscenario.get_subscenario_id_of_unit_id(context, unit_data.unit_id)
            if subscenario_id > 0 and await subscenario.unlock(context, current_user, subscenario_id):
                subscenario_unlocks.append(subscenario_id)

        unit_deck_unit_ids.append(unit_data.unit_id)
        unit_deck_full_info.append((await unit.get_unit_data_full_info(context, unit_data))[0])

    # Check achievement
    accomplished_achievement = (
        await achievement.check_type_1(context, current_user, True)
        + await achievement.check_type_2(context, current_user, live_setting.difficulty, True)
        # album.trigger_achievement call below checks type 18 through 22.
        + await album.trigger_achievement(context, current_user, obtained=True, idolized=True, max_love=True)
        + await achievement.check_type_30(context, current_user)
        + await achievement.check_type_32(context, current_user, live_setting.live_track_id)
        # TODO: Check type 33
        + await achievement.check_type_37(context, current_user, live_setting.live_track_id, True)
        + await achievement.check_type_50(
            context, current_user, live_setting.live_track_id, combo_rank, unit_deck_unit_ids, True
        )
        + await achievement.check_type_58(context, current_user, True)
    )
    if score_rank < 5:
        accomplished_achievement.extend(await achievement.check_type_3(context, current_user, score_rank, True))
    if combo_rank < 5:
        accomplished_achievement.extend(await achievement.check_type_4(context, current_user, combo_rank, True))
    for unit_type_id in unit_types_in_deck:
        accomplished_achievement.extend(await achievement.check_type_7(context, current_user, unit_type_id, True))
    accomplished_achievement.extend(await achievement.check_type_53_recursive(context, current_user))
    accomplished_achievement.fix()

    # Process achievement rewards part 1
    accomplished_achievement_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in accomplished_achievement.accomplished
    ]
    temp_achievement_rewards = await advanced.fixup_achievement_reward(
        context, current_user, accomplished_achievement_rewards
    )

    # Check achievement part 2
    unlocked_scenario = await scenario.count(context, current_user)
    for reward_list in temp_achievement_rewards:
        for reward_data in reward_list:
            if reward_data.add_type == const.ADD_TYPE.SCENARIO:
                unlocked_scenario = unlocked_scenario + 1
    accomplished_achievement.extend(await achievement.check_type_59(context, current_user, unlocked_scenario))

    # Process achievement rewards part 2
    accomplished_achievement_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in accomplished_achievement.accomplished
    ]
    new_achievement_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in accomplished_achievement.new
    ]
    accomplished_achievement_rewards = await advanced.fixup_achievement_reward(
        context, current_user, accomplished_achievement_rewards
    )
    new_achievement_rewards = await advanced.fixup_achievement_reward(context, current_user, new_achievement_rewards)

    # Give achievement rewards
    await achievement.process_achievement_reward(
        context, current_user, accomplished_achievement.accomplished, accomplished_achievement_rewards
    )

    # Clean live in progress
    context.db.main.expunge(live_in_progress)
    await live.clean_live_in_progress(context, current_user)

    # Create response
    reward_unit_list = LiveRewardUnitList()
    reward_unit_list.live_clear.append(live_clear_drop.as_item_reward)
    if live_combo_drop is not None:
        reward_unit_list.live_combo.append(live_combo_drop.as_item_reward)
    if live_score_drop is not None:
        reward_unit_list.live_rank.append(live_score_drop.as_item_reward)
    user_info = await user.get_user_info(context, current_user)

    return LiveRewardResponse(
        live_info=[await live.get_live_info_without_notes(context, request.live_difficulty_id, live_setting)],
        rank=score_rank,
        combo_rank=combo_rank,
        total_love=love_count,
        is_high_score=live_clear_data.hi_score > old_live_clear_data.hi_score,
        hi_score=live_clear_data.hi_score,
        base_reward_info=LiveRewardBaseInfo(
            player_exp=given_exp,
            player_exp_unit_max=common.BeforeAfter[int](before=old_user_info.unit_max, after=user_info.unit_max),
            player_exp_friend_max=common.BeforeAfter[int](before=old_user_info.friend_max, after=user_info.friend_max),
            player_exp_lp_max=common.BeforeAfter[int](before=old_user_info.energy_max, after=user_info.energy_max),
            game_coin=given_g,
            game_coin_reward_box_flag=False,
            social_point=0,  # TODO: Add actual social point
        ),
        reward_unit_list=reward_unit_list,
        unlocked_subscenario_ids=subscenario_unlocks,
        effort_point=effort_result,
        unit_list=[
            LiveRewardResponseUnitList.from_unit_data(
                unit_data_full, position=i + 1, before_love=before_after_loves.before[i]
            )
            for i, unit_data_full in enumerate(unit_deck_full_info)
        ],
        before_user_info=old_user_info,
        after_user_info=await user.get_user_info(context, current_user),
        next_level_info=next_level_info,
        goal_accomp_info=LiveRewardGoalAccomplishedInfo(
            achieved_ids=accomplished_live_goals, rewards=live_goal_rewards
        ),
        special_reward_info=[],  # TODO: Give 1 loveca on clearing this track for the first time.
        accomplished_achievement_list=await achievement.to_game_representation(
            context, accomplished_achievement.accomplished, accomplished_achievement_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        added_achievement_list=await achievement.to_game_representation(
            context, accomplished_achievement.new, new_achievement_rewards
        ),
        new_achievement_cnt=len(accomplished_achievement.new),
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
    )
