from .. import idol
from .. import util
from ..system import achievement
from ..system import advanced
from ..system import album
from ..system import museum
from ..system import reward
from ..system import unit
from ..system import unit_model
from ..system import user

import pydantic


class SupporterInfoResponse(pydantic.BaseModel):
    unit_id: int
    amount: int


class SupporterListInfoResponse(pydantic.BaseModel):
    unit_support_list: list[SupporterInfoResponse]


class UnitAccessoryInfoResponse(pydantic.BaseModel):
    accessory_list: list
    wearing_info: list
    especial_create_flag: bool


class UnitDeckPositionInfoResponse(pydantic.BaseModel):
    position: int
    unit_owning_user_id: int


class UnitDeckInfo(pydantic.BaseModel):
    unit_deck_id: int
    main_flag: bool
    deck_name: str
    unit_owning_user_ids: list[UnitDeckPositionInfoResponse]


class UnitAllInfoResponse(pydantic.BaseModel):
    active: list[unit_model.UnitInfoData]
    waiting: list[unit_model.UnitInfoData]


class UnitSetDisplayRankRequest(pydantic.BaseModel):
    unit_owning_user_id: int
    display_rank: int


class UnitDeckNameRequest(pydantic.BaseModel):
    unit_deck_id: int
    deck_name: str


class UnitRemovableSkillRequest(pydantic.BaseModel):
    unit_owning_user_id: int
    unit_removable_skill_id: int


class UnitRemovableSkillEquipmentRequest(pydantic.BaseModel):
    equip: list[UnitRemovableSkillRequest] | None = None
    remove: list[UnitRemovableSkillRequest] | None = None


class UnitWaitOrActivateRequest(pydantic.BaseModel):
    unit_owning_user_ids: list[int]


class UnitWaitResponse(pydantic.BaseModel):
    unit_removable_skill: unit_model.RemovableSkillOwningInfo


class UnitDeckInfoResponse(pydantic.RootModel[list[UnitDeckInfo]]):
    pass


class UnitDeckList(pydantic.BaseModel):
    unit_deck_detail: list[UnitDeckPositionInfoResponse]
    unit_deck_id: int
    main_flag: int
    deck_name: str


class UnitDeckRequest(pydantic.BaseModel):
    unit_deck_list: list[UnitDeckList]


class UnitRankUpRequest(pydantic.BaseModel):
    base_owning_unit_user_id: int
    unit_owning_user_ids: list[int]


class UnitGetExchangePoint(pydantic.BaseModel):
    rarity: int
    exchange_point: int


class UnitRankUpResponse(achievement.AchievementMixin):
    before: unit_model.UnitInfoData
    after: unit_model.UnitInfoData
    before_user_info: user.UserInfoData
    after_user_info: user.UserInfoData
    use_game_coin: int
    unlocked_subscenario_ids: list[int]
    get_exchange_point_list: list[UnitGetExchangePoint]
    unit_removable_skill: unit_model.RemovableSkillOwningInfo
    museum_info: museum.MuseumInfoData
    server_timestamp: int = pydantic.Field(default_factory=util.time)
    present_cnt: int


@idol.register("unit", "accessoryAll")
async def unit_accessoryall(context: idol.SchoolIdolUserParams) -> UnitAccessoryInfoResponse:
    # TODO
    util.stub("unit", "accessoryAll", context.raw_request_data)
    return UnitAccessoryInfoResponse(accessory_list=[], wearing_info=[], especial_create_flag=False)


@idol.register("unit", "deckInfo")
async def unit_deckinfo(context: idol.SchoolIdolUserParams) -> UnitDeckInfoResponse:
    current_user = await user.get_current(context)
    result: list[UnitDeckInfo] = []

    for i in range(1, 19):
        decklist = await unit.load_unit_deck(context, current_user, i)

        if decklist is not None:
            deckpos: list[UnitDeckPositionInfoResponse] = []
            for j, unit_id in enumerate(decklist[1], 1):
                if unit_id > 0:
                    deckpos.append(UnitDeckPositionInfoResponse(position=j, unit_owning_user_id=unit_id))

            deckinfo = UnitDeckInfo(
                unit_deck_id=i,
                main_flag=current_user.active_deck_index == i,
                deck_name=decklist[0].name,
                unit_owning_user_ids=deckpos,
            )
            result.append(deckinfo)

    return UnitDeckInfoResponse.model_validate(result)


@idol.register("unit", "removableSkillInfo")
async def unit_removableskillinfo(context: idol.SchoolIdolUserParams) -> unit_model.RemovableSkillInfoResponse:
    current_user = await user.get_current(context)
    return await unit.get_removable_skill_info_request(context, current_user)


@idol.register("unit", "supporterAll")
async def unit_supporterall(context: idol.SchoolIdolUserParams) -> SupporterListInfoResponse:
    current_user = await user.get_current(context)
    units = await unit.get_all_supporter_unit(context, current_user)

    return SupporterListInfoResponse(
        unit_support_list=[SupporterInfoResponse(unit_id=supp[0], amount=supp[1]) for supp in units]
    )


@idol.register("unit", "unitAll")
async def unit_unitall(context: idol.SchoolIdolUserParams) -> UnitAllInfoResponse:
    current_user = await user.get_current(context)
    units = await unit.get_all_units(context, current_user)

    unit_result: dict[bool, list[unit_model.UnitInfoData]] = {False: [], True: []}

    for unit_data in units:
        unit_serialized_data, _ = await unit.get_unit_data_full_info(context, unit_data)
        unit_result[unit_data.active].append(unit_serialized_data)

    return UnitAllInfoResponse(active=unit_result[True], waiting=unit_result[False])


@idol.register("unit", "setDisplayRank")
async def unit_setdisplayrank(context: idol.SchoolIdolUserParams, request: UnitSetDisplayRankRequest) -> None:
    current_user = await user.get_current(context)
    target_unit = await unit.get_unit(context, request.unit_owning_user_id)
    if target_unit is None or target_unit.user_id != current_user.id:
        raise idol.error.IdolError(detail="Invalid target unit")

    target_unit.display_rank = request.display_rank


@idol.register("unit", "deckName")
async def unit_deckname(context: idol.SchoolIdolUserParams, request: UnitDeckNameRequest) -> None:
    current_user = await user.get_current(context)
    deck_data = await unit.load_unit_deck(context, current_user, request.unit_deck_id)
    if deck_data is None:
        raise idol.error.IdolError(detail="Invalid target deck")

    await advanced.test_name(context, request.deck_name)

    deck_data[0].name = request.deck_name


@idol.register("unit", "removableSkillEquipment")
async def unit_removableskillequipment(
    context: idol.SchoolIdolUserParams, request: UnitRemovableSkillEquipmentRequest
) -> None:
    current_user = await user.get_current(context)

    # TODO: Optimize
    current_sis_info = await unit.get_removable_skill_info_request(context, current_user)
    unequipped_sis_amount = dict(
        (sis.unit_removable_skill_id, sis.total_amount - sis.equipped_amount) for sis in current_sis_info.owning_info
    )

    # Process "remove" list first
    if request.remove:
        for remove_info in request.remove:
            unit_data = await unit.get_unit(context, remove_info.unit_owning_user_id)
            unit.validate_unit(current_user, unit_data)

            if not await unit.detach_unit_removable_skill(
                context,
                unit_data,
                remove_info.unit_removable_skill_id,
            ):
                raise idol.error.IdolError(detail=f"no such sis {remove_info!r}")
            unequipped_sis_amount[remove_info.unit_removable_skill_id] = (
                unequipped_sis_amount[remove_info.unit_removable_skill_id] + 1
            )

    # Process "equip" list
    if request.equip:
        for equip_info in request.equip:
            if unequipped_sis_amount[equip_info.unit_removable_skill_id] > 0:
                unit_data = await unit.get_unit(context, equip_info.unit_owning_user_id)
                unit.validate_unit(current_user, unit_data)

                if unit_data.active:
                    if not await unit.attach_unit_removable_skill(
                        context,
                        unit_data,
                        equip_info.unit_removable_skill_id,
                    ):
                        raise idol.error.IdolError(detail=f"sis already exist {equip_info!r}")
                    unequipped_sis_amount[equip_info.unit_removable_skill_id] = (
                        unequipped_sis_amount[equip_info.unit_removable_skill_id] - 1
                    )
                else:
                    raise idol.error.IdolError(detail=f"unit is inactive {equip_info.unit_owning_user_id}")
            else:
                raise idol.error.IdolError(detail=f"out of SIS {equip_info.unit_removable_skill_id}")


@idol.register("unit", "wait")
async def unit_wait(context: idol.SchoolIdolUserParams, request: UnitWaitOrActivateRequest) -> UnitWaitResponse:
    current_user = await user.get_current(context)
    waiting_count = await unit.count_units(context, current_user, False)

    if (waiting_count + len(request.unit_owning_user_ids)) > current_user.waiting_unit_max:
        raise idol.error.IdolError(detail="waiting unit out of range")

    for unit_owning_user_id in request.unit_owning_user_ids:
        unit_data = await unit.get_unit(context, unit_owning_user_id)
        unit.validate_unit(current_user, unit_data)

        if unit_data.active:
            unit_sis = await unit.get_unit_removable_skills(context, unit_data)
            for removable_skill_id in unit_sis:
                await unit.detach_unit_removable_skill(context, unit_data, removable_skill_id)

            # Move to waiting room
            unit_data.active = False

    user_sis_info = await unit.get_removable_skill_info_request(context, current_user)
    return UnitWaitResponse(unit_removable_skill=user_sis_info)


@idol.register("unit", "activate")
async def unit_activate(context: idol.SchoolIdolUserParams, request: UnitWaitOrActivateRequest) -> None:
    current_user = await user.get_current(context)
    active_count = await unit.count_units(context, current_user, True)

    if (active_count + len(request.unit_owning_user_ids)) > current_user.unit_max:
        raise idol.error.IdolError(detail="active unit out of range")

    for unit_owning_user_id in request.unit_owning_user_ids:
        unit_data = await unit.get_unit(context, unit_owning_user_id)
        unit.validate_unit(current_user, unit_data)

        # Move to active room
        unit_data.active = True


ALL_DECK_POSITIONS = set(range(1, 10))


@idol.register("unit", "deck")
async def unit_deck(context: idol.SchoolIdolUserParams, request: UnitDeckRequest) -> None:
    current_user = await user.get_current(context)
    clear_deck_ids = set(unit.VALID_DECK_ID)

    # Replace/add deck
    for deck_req_info in request.unit_deck_list:
        await advanced.test_name(context, deck_req_info.deck_name)

        unit_deck, _ = await unit.load_unit_deck(context, current_user, deck_req_info.unit_deck_id, True)
        unit_deck.name = deck_req_info.deck_name

        # Replace decks
        unit_user_ids: list[int] = [0] * 9
        for detail in deck_req_info.unit_deck_detail:
            # Unit sanity check
            unit_data = await unit.get_unit(context, detail.unit_owning_user_id)
            unit.validate_unit(current_user, unit_data)
            unit_user_ids[detail.position - 1] = detail.unit_owning_user_id

        if deck_req_info.main_flag > 0:
            # Perform additional sanity check
            registered_deck_positions: set[int] = set()
            for detail in deck_req_info.unit_deck_detail:
                if detail.unit_owning_user_id > 0:
                    registered_deck_positions.add(detail.position)

            if registered_deck_positions != ALL_DECK_POSITIONS:
                raise idol.error.by_code(idol.error.ERROR_CODE_IGNORE_MAIN_DECK)

            current_user.active_deck_index = deck_req_info.unit_deck_id

        await unit.save_unit_deck(context, current_user, unit_deck, unit_user_ids)
        clear_deck_ids.remove(deck_req_info.unit_deck_id)

    # Clear deck
    for deck_id in clear_deck_ids:
        unit_deck = await unit.load_unit_deck(context, current_user, deck_id, False)
        if unit_deck is not None:
            await unit.save_unit_deck(context, current_user, unit_deck[0], [0] * 9)


@idol.register("unit", "rankUp")
async def unit_rankup(context: idol.SchoolIdolUserParams, request: UnitRankUpRequest):
    current_user = await user.get_current(context)
    source_unit = await unit.get_unit(context, request.base_owning_unit_user_id)
    unit.validate_unit(current_user, source_unit)

    # Get needed data
    source_unit_info = await unit.get_unit_info(context, source_unit.unit_id)
    assert source_unit_info is not None
    if source_unit_info.disable_rank_up > 0:
        raise idol.error.IdolError(detail="cannot idolize this unit")

    source_unit_rarity = await unit.get_unit_rarity(context, source_unit_info.rarity)
    assert source_unit_rarity is not None

    before = await unit.get_unit_data_full_info(context, source_unit)
    before_user = await user.get_user_info(context, current_user)
    use_game_coin = 0

    for unit_owning_user_id in request.unit_owning_user_ids:
        if source_unit.unit_removable_skill_capacity >= source_unit_info.max_removable_skill_capacity:
            raise idol.error.IdolError(detail="max SIS reached")

        target_unit = await unit.get_unit(context, unit_owning_user_id)
        await unit.remove_unit(context, current_user, target_unit)
        add_removable_skill_slot = 2 - await unit.idolize(context, current_user, source_unit)
        source_unit.unit_removable_skill_capacity = min(
            source_unit.unit_removable_skill_capacity + add_removable_skill_slot,
            source_unit_info.max_removable_skill_capacity,
        )
        use_game_coin = use_game_coin + source_unit_rarity.rank_up_cost

        if current_user.game_coin >= source_unit_rarity.rank_up_cost:
            current_user.game_coin = current_user.game_coin - source_unit_rarity.rank_up_cost
        else:
            raise idol.error.IdolError(detail="not enough money")

    await album.update(context, current_user, source_unit.unit_id, rank_max=True)
    achievement_list = await album.trigger_achievement(context, current_user, idolized=True)
    accomplished_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.accomplished
    ]
    unaccomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.new]
    await advanced.fixup_achievement_reward(context, current_user, accomplished_rewards)
    await advanced.fixup_achievement_reward(context, current_user, unaccomplished_rewards)
    await advanced.process_achievement_reward(
        context, current_user, achievement_list.accomplished, accomplished_rewards
    )

    after = await unit.get_unit_data_full_info(context, source_unit)
    after_user = await user.get_user_info(context, current_user)

    return UnitRankUpResponse(
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
        before=before[0],
        after=after[0],
        before_user_info=before_user,
        after_user_info=after_user,
        use_game_coin=use_game_coin,
        unlocked_subscenario_ids=[],
        get_exchange_point_list=[],
        unit_removable_skill=await unit.get_removable_skill_info_request(context, current_user),
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
    )
