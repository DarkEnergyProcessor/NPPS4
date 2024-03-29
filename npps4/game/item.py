from .. import idol
from .. import util

import pydantic


class ItemListResponse(pydantic.BaseModel):
    general_item_list: list
    buff_item_list: list
    reinforce_item_list: list
    reinforce_info: list


@idol.register("item", "list")
async def item_list(context: idol.SchoolIdolUserParams) -> ItemListResponse:
    # TODO
    util.stub("item", "list", context.raw_request_data)
    return ItemListResponse(general_item_list=[], buff_item_list=[], reinforce_item_list=[], reinforce_info=[])
