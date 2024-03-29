import pydantic

from .. import const
from .. import util
from ..system import item


class LiveUnitDrop(pydantic.BaseModel):
    unit_id: int
    weight: int


class LiveSpecificLiveUnitDrop(pydantic.BaseModel):
    live_setting_id: int
    drops: list[LiveUnitDrop]


class LiveUnitDropChance(pydantic.BaseModel):
    common: int
    live_specific: int


class ItemWithWeight(item.item_model.Item):
    weight: int


class LiveEffortRewardDrops(pydantic.BaseModel):
    live_effort_point_box_spec_id: int
    drops: list[ItemWithWeight]


class SecretboxCost(pydantic.BaseModel):
    cost_type: const.SECRETBOX_COST_TYPE
    cost_item_id: int | None
    cost_amount: int


class SecretboxButton(pydantic.BaseModel):
    button_type: const.SECRETBOX_BUTTON_TYPE
    costs: list[SecretboxCost]
    unit_count: int
    guarantee_specific_rarity_amount: int  # 0 = no guarantee
    guaranteed_rarity: int  # 0 = no guarantee


class SecretboxData(pydantic.BaseModel):
    id_string: str
    name: str
    name_en: str | None
    member_category: int
    secretbox_type: const.SECRETBOX_LAYOUT_TYPE
    order: int
    start_time: int
    end_time: int

    add_gauge: int
    free_once_a_day_display: SecretboxCost | None  # Always scout 1. None = no free once a day.
    buttons: list[SecretboxButton]

    animation_layout_type: const.SECRETBOX_LAYOUT_TYPE
    animation_asset_layout: list[str]
    animation_asset_layout_en: list[str | None]
    menu_asset: str
    menu_asset_en: str | None

    rarity_rates: list[int]

    @property
    def secretbox_id(self) -> int:
        return util.java_hash_code(self.id_string)


class SerializedServerData(pydantic.BaseModel):
    badwords: list[str]  # Note: Badwords are Base64-encoded in the JSON file!
    live_unit_drop_chance: LiveUnitDropChance
    common_live_unit_drops: list[LiveUnitDrop]
    live_specific_live_unit_drops: list[LiveSpecificLiveUnitDrop]
    live_effort_drops: list[LiveEffortRewardDrops]
