from .. import idol
from .. import util
from ..idol.system import advanced
from ..idol.system import unit
from ..idol.system import user

import pydantic


class RemovableSkillInfoResponse(pydantic.BaseModel):
    owning_info: list
    equipment_info: list


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
async def unit_removableskillinfo(context: idol.SchoolIdolUserParams) -> RemovableSkillInfoResponse:
    # TODO
    util.stub("unit", "removableSkillInfo", context.raw_request_data)
    return RemovableSkillInfoResponse(owning_info=[], equipment_info=[])


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
