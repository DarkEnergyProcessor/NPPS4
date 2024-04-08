import pydantic

from .. import const

from typing import Any


class Item(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    add_type: const.ADD_TYPE
    item_id: int
    amount: int = 1
    item_category_id: int = 0
    reward_box_flag: bool = False
    comment: str = ""
    # rarity: int = 6  # For effort. TODO

    def dump_extra_data(self) -> dict[str, Any]:
        dump = self.model_dump()
        for field_to_remove in Item.model_fields.keys():
            del dump[field_to_remove]

        return dump
