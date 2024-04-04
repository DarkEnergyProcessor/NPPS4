import pydantic

from .. import idol
from ..system import common
from ..system import item
from ..system import user


class ItemListResponse(pydantic.BaseModel):
    general_item_list: list[common.ItemCount]
    buff_item_list: list[common.ItemCount]
    reinforce_item_list: list[common.ItemCount]
    reinforce_info: list = pydantic.Field(default_factory=list)


@idol.register("item", "list")
async def item_list(context: idol.SchoolIdolUserParams) -> ItemListResponse:
    current_user = await user.get_current(context=context)
    general_item_list, buff_item_list, reinforce_item_list = await item.get_item_list(context, current_user)
    return ItemListResponse(
        general_item_list=general_item_list, buff_item_list=buff_item_list, reinforce_item_list=reinforce_item_list
    )
