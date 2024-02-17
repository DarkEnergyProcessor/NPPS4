from .. import idol
from .. import util
from ..idol.system import advanced
from ..idol.system import unit
from ..idol.system import user

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


class UnitDeckInfoResponse(pydantic.BaseModel):
    unit_deck_id: int
    main_flag: bool
    deck_name: str
    unit_owning_user_ids: list[UnitDeckPositionInfoResponse]


class UnitAllInfoResponse(pydantic.BaseModel):
    active: list[unit.UnitInfoData]
    waiting: list[unit.UnitInfoData]


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
    unit_removable_skill: unit.RemovableSkillOwningInfo


@idol.register("unit", "accessoryAll")
async def unit_accessoryall(context: idol.SchoolIdolUserParams) -> UnitAccessoryInfoResponse:
    # TODO
    util.stub("unit", "accessoryAll", context.raw_request_data)
    return UnitAccessoryInfoResponse(accessory_list=[], wearing_info=[], especial_create_flag=False)


@idol.register("unit", "deckInfo")
async def unit_deckinfo(context: idol.SchoolIdolUserParams) -> list[UnitDeckInfoResponse]:
    current_user = await user.get_current(context)
    result: list[UnitDeckInfoResponse] = []

    for i in range(1, 19):
        decklist = await unit.load_unit_deck(context, current_user, i)

        if decklist is not None:
            deckpos: list[UnitDeckPositionInfoResponse] = []
            for j, unit_id in enumerate(decklist[1], 1):
                if unit_id > 0:
                    deckpos.append(UnitDeckPositionInfoResponse(position=j, unit_owning_user_id=unit_id))

            deckinfo = UnitDeckInfoResponse(
                unit_deck_id=i,
                main_flag=current_user.active_deck_index == i,
                deck_name=decklist[0].name,
                unit_owning_user_ids=deckpos,
            )
            result.append(deckinfo)

    return result


@idol.register("unit", "removableSkillInfo")
async def unit_removableskillinfo(context: idol.SchoolIdolUserParams) -> unit.RemovableSkillInfoResponse:
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

    unit_result: dict[bool, list[unit.UnitInfoData]] = {False: [], True: []}

    for unit_data in units:
        unit_serialized_data, _ = await unit.get_unit_data_full_info(context, unit_data)
        unit_result[unit_data.active].append(unit_serialized_data)

    return UnitAllInfoResponse(active=unit_result[True], waiting=unit_result[False])


@idol.register("unit", "setDisplayRank")
async def unit_setdisplayrank(
    context: idol.SchoolIdolUserParams, request: UnitSetDisplayRankRequest
) -> idol.core.DummyModel:
    current_user = await user.get_current(context)
    target_unit = await unit.get_unit(context, request.unit_owning_user_id)
    if target_unit is None or target_unit.user_id != current_user.id:
        raise idol.error.IdolError(detail="Invalid target unit")

    target_unit.display_rank = request.display_rank
    return idol.core.DummyModel()


@idol.register("unit", "deckName")
async def unit_deckname(context: idol.SchoolIdolUserParams, request: UnitDeckNameRequest) -> idol.core.DummyModel:
    current_user = await user.get_current(context)
    deck_data = await unit.load_unit_deck(context, current_user, request.unit_deck_id)
    if deck_data is None:
        raise idol.error.IdolError(detail="Invalid target deck")

    await advanced.test_name(context, request.deck_name)

    deck_data[0].name = request.deck_name
    return idol.core.DummyModel()


@idol.register("unit", "removableSkillEquipment")
async def unit_removableskillequipment(
    context: idol.SchoolIdolUserParams, request: UnitRemovableSkillEquipmentRequest
) -> idol.core.DummyModel:
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

    return idol.core.DummyModel()


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
async def unit_activate(
    context: idol.SchoolIdolUserParams, request: UnitWaitOrActivateRequest
) -> idol.core.DummyModel:
    current_user = await user.get_current(context)
    active_count = await unit.count_units(context, current_user, True)

    if (active_count + len(request.unit_owning_user_ids)) > current_user.unit_max:
        raise idol.error.IdolError(detail="active unit out of range")

    for unit_owning_user_id in request.unit_owning_user_ids:
        unit_data = await unit.get_unit(context, unit_owning_user_id)
        unit.validate_unit(current_user, unit_data)

        # Move to active room
        unit_data.active = True

    return idol.core.DummyModel()
