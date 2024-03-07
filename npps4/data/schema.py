import pydantic

from ..idol.system import item


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


class SerializedServerData(pydantic.BaseModel):
    badwords: list[str]  # Note: Badwords are Base64-encoded in the JSON file!
    live_unit_drop_chance: LiveUnitDropChance
    common_live_unit_drops: list[LiveUnitDrop]
    live_specific_live_unit_drops: list[LiveSpecificLiveUnitDrop]
    live_effort_drops: list[LiveEffortRewardDrops]
