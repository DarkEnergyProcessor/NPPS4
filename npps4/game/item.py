import pydantic

from .. import idol
from ..system import common
from ..system import item
from ..system import user

from typing import Annotated, Any


def empty_list_is_empty_dict(value: Any):
    if isinstance(value, list) and len(value) == 0:
        return {}
    return value


class ItemListReinforceInfoUnitReinforceItem(pydantic.BaseModel):
    unit_reinforce_item_id: int
    reinforce_type: int
    addition_value: int
    target_unit_ids: list[int]


class ItemListReinforceInfo(pydantic.BaseModel):
    event_id: int
    item_list: list[ItemListReinforceInfoUnitReinforceItem]
    available_unit_list: list[dict]  # Additionally has mark_id (int) and sub_evaluation (int)


class ItemListResponse(pydantic.BaseModel):
    general_item_list: list[common.ItemCount]
    buff_item_list: list[common.ItemCount]
    reinforce_item_list: list[common.ItemCount]
    reinforce_info: Annotated[dict[str, ItemListReinforceInfo], pydantic.BeforeValidator(empty_list_is_empty_dict)] = (
        pydantic.Field(default_factory=dict)
    )


@idol.register("item", "list")
async def item_list(context: idol.SchoolIdolUserParams) -> ItemListResponse:
    current_user = await user.get_current(context=context)
    general_item_list, buff_item_list, reinforce_item_list = await item.get_item_list(context, current_user)
    return ItemListResponse(
        general_item_list=general_item_list, buff_item_list=buff_item_list, reinforce_item_list=reinforce_item_list
    )
