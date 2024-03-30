# import pickle

from .. import idol
from .. import util
from ..system import common
from ..system import secretbox
from ..system import secretbox_model
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
            is_unit_max=False,  # TODO
            item_list=[],  # TODO
            member_category_list=await secretbox.get_secretbox_data(context, current_user),
        )
