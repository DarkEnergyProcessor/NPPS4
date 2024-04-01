# import pickle

from .. import idol
from .. import util
from ..system import achievement
from ..system import common
from ..system import museum
from ..system import secretbox
from ..system import secretbox_model
from ..system import unit
from ..system import unit_model
from ..system import user

import pydantic


class SecretboxAllResponse(pydantic.BaseModel):
    use_cache: int
    is_unit_max: bool
    item_list: list[common.ItemCount]
    gauge_info: secretbox_model.SecretboxGaugeInfo = pydantic.Field(
        default_factory=secretbox_model.SecretboxGaugeInfo
    )  # TODO
    member_category_list: list[secretbox_model.SecretboxAllMemberCategory]


class SecretboxPonRequest(pydantic.BaseModel):
    id: int
    secret_box_id: int
    unit_type_ids: list  # TODO: list of what?


class SecretboxAddedGaugeInfo(secretbox_model.SecretboxGaugeInfo):
    added_gauge_point: int = 0


class SecretboxItems(pydantic.BaseModel):
    unit: list[unit_model.AnyUnitItem]
    item: list[common.AnyItem]


class SecretboxPonResponse(achievement.AchievementMixin, common.TimestampMixin):
    is_unit_max: bool
    item_list: list[common.ItemCount]
    gauge_info: SecretboxAddedGaugeInfo = pydantic.Field(default_factory=SecretboxAddedGaugeInfo)  # TODO
    button_list: list[secretbox_model.AnySecretboxButton]
    secret_box_info: secretbox_model.AnySecretboxInfo
    secret_box_items: SecretboxItems
    before_user_info: user.UserInfoData
    after_user_info: user.UserInfoData
    secret_box_badge_flag: bool = False
    lowest_rarity: int = 1
    promotion_performance_rate: int = 0
    secret_box_parcel_type: int = 1
    museum_info: museum.MuseumInfoData
    present_cnt: int


USE_STUB_DATA = False

if USE_STUB_DATA:
    import json

    from typing import Any

    class CustomSecretBoxResponse(pydantic.BaseModel):
        use_cache: int
        is_unit_max: bool
        item_list: list[common.ItemCount]
        gauge_info: secretbox_model.SecretboxGaugeInfo = pydantic.Field(
            default_factory=secretbox_model.SecretboxGaugeInfo
        )  # TODO
        member_category_list: list[dict[str, Any]]

    @idol.register("secretbox", "all")
    async def secretbox_all_stub(context: idol.SchoolIdolUserParams) -> CustomSecretBoxResponse:
        # TODO
        util.stub("secretbox", "all")
        with open("secretbox.json", "r", encoding="utf-8") as f:
            return CustomSecretBoxResponse(
                use_cache=1, is_unit_max=False, item_list=[], member_category_list=json.load(f)
            )

else:

    @idol.register("secretbox", "all")
    async def secretbox_all(context: idol.SchoolIdolUserParams) -> SecretboxAllResponse:
        util.stub("secretbox", "all")
        current_user = await user.get_current(context)
        return SecretboxAllResponse(
            use_cache=0,
            is_unit_max=await unit.is_unit_max(context, current_user),
            item_list=[],  # TODO
            member_category_list=await secretbox.get_all_secretbox_data_response(context, current_user),
        )


# @idol.register("secretbox", "pon", batchable=False)
async def secretbox_pon(context: idol.SchoolIdolUserParams, request: SecretboxPonRequest):
    current_user = await user.get_current(context)
    secretbox_id, button_index, cost_index = secretbox.decode_cost_id(request.id)
    secretbox_button = secretbox.get_secretbox_button(secretbox_id, button_index)
    unit_roll = secretbox.roll_units(secretbox_id, 1)
