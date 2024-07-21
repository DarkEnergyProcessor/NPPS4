import pydantic

from .. import idol
from ..system import common
from ..system import item
from ..system import live
from ..system import reward
from ..system import user


class CommonLiveResumeRequest(pydantic.BaseModel):
    cancel: bool


class CommonRecoveryEnergyRequest(pydantic.BaseModel):
    energy_type: int
    item_id: int
    amount: int


class CommonRecoveryEnergyResponse(common.TimestampMixin):
    item_list: list[common.ItemCount]
    energy_max: int
    present_cnt: int
    after_sns_coin: int
    after_game_coin: int
    before_sns_coin: int
    over_max_energy: int
    training_energy: int
    before_game_coin: int
    energy_full_time: str
    training_energy_max: int


@idol.register("common", "liveResume")
async def common_liveresume(context: idol.SchoolIdolUserParams, request: CommonLiveResumeRequest) -> None:
    if request.cancel:
        current_user = await user.get_current(context)
        await live.clean_live_in_progress(context, current_user)


@idol.register("common", "recoveryEnergy", batchable=False)
async def common_recoveryenergy(
    context: idol.SchoolIdolUserParams, request: CommonRecoveryEnergyRequest
) -> CommonRecoveryEnergyResponse:
    current_user = await user.get_current(context)
    current_loveca = user.get_loveca(current_user)

    if request.energy_type != 1:
        # TODO
        raise idol.error.by_code(idol.error.ERROR_CODE_ENERGY_FULL)
    if request.amount < 0:
        raise idol.error.IdolError(detail="Amount out of range")

    if request.item_id == 0:
        if current_loveca >= request.amount:
            # Loveca, behave as restore 100% LP
            user.add_energy_percentage(current_user, 1.0, request.amount)
            user.sub_loveca(current_user, request.amount)
        else:
            raise idol.error.by_code(idol.error.ERROR_CODE_NOT_ENOUGH_LOVECA)
    else:
        # LP recover item
        recovery_item_info = await item.get_recovery_item_info(context, request.item_id)
        if recovery_item_info is None:
            raise idol.error.by_code(idol.error.ERROR_CODE_NO_RECOVER_ITEM)

        recovery_item_data = await item.get_recovery_item_data_guaranteed(context, current_user, request.item_id)
        if recovery_item_data.amount >= request.amount:
            match recovery_item_info.recovery_type:
                case 1:
                    # Percentage
                    user.add_energy_percentage(current_user, recovery_item_info.recovery_value / 100, request.amount)
                case 2:
                    # Exact
                    user.add_energy(current_user, recovery_item_info.recovery_value * request.amount)
                case _:
                    raise idol.error.IdolError(detail="Unknown recovery type")
            recovery_item_data.amount = recovery_item_data.amount - request.amount
        else:
            raise idol.error.by_code(idol.error.ERROR_CODE_RECOVER_ITEM_NOT_ENOUGH)

    user_info = await user.get_user_info(context, current_user)
    return CommonRecoveryEnergyResponse(
        item_list=await item.get_recovery_items(context, current_user),
        energy_max=user_info.energy_max,
        over_max_energy=user_info.over_max_energy,
        energy_full_time=user_info.energy_full_time,
        before_sns_coin=current_loveca,
        after_sns_coin=user_info.sns_coin,
        before_game_coin=user_info.game_coin,
        after_game_coin=user_info.game_coin,  # Game coin is unused in this scenario
        training_energy=user_info.training_energy,
        training_energy_max=user_info.training_energy_max,
        present_cnt=await reward.count_presentbox(context, current_user),
    )
