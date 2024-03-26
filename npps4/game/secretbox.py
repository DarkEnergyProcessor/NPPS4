from .. import idol
from .. import util
from ..system import common

import pydantic


class SecretboxGaugeInfo(pydantic.BaseModel):
    max_gauge_point: int = 100
    gauge_point: int = 0


class SecretboxAllAnimationAsset(pydantic.BaseModel):
    type: int
    background_asset: str
    additional_asset_1: str
    additional_asset_2: str
    additional_asset_3: str


class SecretboxAllCost(pydantic.BaseModel):
    id: int
    payable: int
    unit_count: int
    type: int  # add_type
    item_id: int
    amount: int


class SecretboxAllButton(pydantic.BaseModel):
    secret_box_button_type: int
    cost_list: list[SecretboxAllCost]
    secret_box_name: str


class SecretboxAllSecretboxInfo(pydantic.BaseModel):
    secret_box_id: int
    secret_box_type: int
    name: str
    description: str | None = None
    start_date: str
    end_date: str
    add_gauge: int
    always_display_flag: int
    pon_count: int
    pon_upper_limit: int = 0


class SecretboxAllPage(pydantic.BaseModel):
    menu_asset: str
    page_order: int
    animation_assets: SecretboxAllAnimationAsset
    button_list: list[SecretboxAllButton]
    secret_box_info: SecretboxAllSecretboxInfo


class SecretboxAllMemberCategory(pydantic.BaseModel):
    member_category: int
    page_list: list


class SecretboxAllResponse(pydantic.BaseModel):
    use_cache: int
    is_unit_max: bool
    item_list: list[common.ItemCount]
    gauge_info: SecretboxGaugeInfo = pydantic.Field(default_factory=SecretboxGaugeInfo)  # TODO
    member_category_list: list[SecretboxAllMemberCategory]


@idol.register("secretbox", "all")
async def secretbox_all(context: idol.SchoolIdolUserParams) -> SecretboxAllResponse:
    # TODO
    util.stub("secretbox", "all")
    raise idol.error.by_code(idol.error.ERROR_CODE_LIB_ERROR)
