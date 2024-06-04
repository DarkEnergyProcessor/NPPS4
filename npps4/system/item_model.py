import pydantic

from .. import const

from typing import Any


class ItemExtraData(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)


class BaseItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    add_type: const.ADD_TYPE
    item_id: int
    amount: int = 1
    extra_data: dict[str, Any] | None = None


class Item(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    add_type: const.ADD_TYPE
    item_id: int
    amount: int = 1
    item_category_id: int = 0
    reward_box_flag: bool = False
    comment: str = ""
    # rarity: int = 6  # For effort. TODO

    def get_extra_data(self) -> ItemExtraData | None:
        return None
