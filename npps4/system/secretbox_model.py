import pydantic

from . import common
from .. import const


class SecretboxGaugeInfo(pydantic.BaseModel):
    max_gauge_point: int = 100
    gauge_point: int = 0


class SecretboxAllAnimation2Asset(pydantic.BaseModel):
    type: const.SECRETBOX_ANIMATION_TYPE
    background_asset: str
    additional_asset_1: str
    additional_asset_2: str


class SecretboxAllAnimation3Asset(SecretboxAllAnimation2Asset):
    additional_asset_3: str


AnySecretboxAllAnimationAsset = SecretboxAllAnimation3Asset | SecretboxAllAnimation2Asset


class SecretboxAllCost(pydantic.BaseModel):
    id: int
    payable: bool
    unit_count: int
    type: const.SECRETBOX_COST_TYPE
    # Note: IF "type" above is "LOVECA", then possible item_id values:
    # * 1: Paid loveca
    # * anything else: Free loveca + paid loveca
    item_id: int | None = None
    amount: int


class SecretboxAllButton(pydantic.BaseModel):
    secret_box_button_type: const.SECRETBOX_BUTTON_TYPE
    cost_list: list[SecretboxAllCost]
    secret_box_name: str


class SecretboxAllButtonWithBaloon(SecretboxAllButton):
    balloon_asset: str | None = None


class SecretboxAllButtonShowCost(pydantic.BaseModel):
    cost_type: const.SECRETBOX_COST_TYPE
    item_id: int | None = None
    unit_count: int


class SecretboxAllButtonWithShowCost(SecretboxAllButton):
    show_cost: SecretboxAllButtonShowCost


AnySecretboxButton = SecretboxAllButton | SecretboxAllButtonWithShowCost | SecretboxAllButtonWithBaloon


class SecretboxAllSecretboxInfo(pydantic.BaseModel):
    secret_box_id: int
    # Some button naming difference:
    # DEFAULT: Uses "name" field in this class when pressing button.
    # STUB: Uses "secret_box_name" field in the button list.
    secret_box_type: const.SECRETBOX_LAYOUT_TYPE
    name: str
    description: str | None = None
    start_date: str
    end_date: str
    add_gauge: int
    always_display_flag: int
    pon_count: int
    pon_upper_limit: int = 0


class SecretboxAllSecretboxInfoWithShowEndDate(SecretboxAllSecretboxInfo):
    show_end_date: str


AnySecretboxInfo = SecretboxAllSecretboxInfo | SecretboxAllSecretboxInfoWithShowEndDate


class SecretboxAllPage(pydantic.BaseModel):
    menu_asset: str
    page_order: int
    animation_assets: AnySecretboxAllAnimationAsset
    button_list: list[AnySecretboxButton]
    secret_box_info: AnySecretboxInfo


class SecretboxAllMemberCategory(pydantic.BaseModel):
    member_category: int
    page_list: list[SecretboxAllPage]
