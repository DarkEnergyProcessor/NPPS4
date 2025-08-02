import re

import pydantic

from .. import const
from .. import idol
from .. import util
from ..system import common
from ..system import item_model
from ..system import user


class PaymentRestrictionInfo(pydantic.BaseModel):
    restricted: bool


class PaymentUnderAgeInfo(pydantic.BaseModel):
    birth_set: bool
    has_limit: bool
    limit_amount: int | None = None
    month_used: int


class PaymentProductListItemList(pydantic.BaseModel):
    add_type: const.ADD_TYPE
    item_id: int
    amount: int

    @pydantic.computed_field
    def is_freebie(self) -> bool:
        return not (self.add_type == const.ADD_TYPE.LOVECA and self.item_id == 1)


class PaymentProductListLimitStatus(pydantic.BaseModel):
    term_start_date: str
    remaining_time: str = ""
    remaining_count: int = 1


class PaymentProductListLimitStatusWithEndTime(PaymentProductListLimitStatus):
    end_date: str

    @pydantic.computed_field
    def term_end_date(self) -> str:
        return self.end_date


class PaymentProductList(pydantic.BaseModel):
    product_id: str
    product_type: int
    name: str
    price: int
    can_buy: bool
    item_list: list[PaymentProductListItemList]
    confirm_url: str = ""
    announce_url: str = ""
    limit_status: pydantic.SerializeAsAny[PaymentProductListLimitStatus]
    banner_img_asset: str  # "assets/image/shop/shop_banner/shop_banner_252.png"


class PaymentProductListSNS(pydantic.BaseModel):
    product_id: str
    product_type: int
    name: str
    price: int
    can_buy: bool
    item_list: list[PaymentProductListItemList]


class PaymentProductListSubscriptionStatusUserStatus(pydantic.BaseModel):
    is_licensed: bool


class PaymentProductListSubscriptionStatusLicenseInfoItem(pydantic.BaseModel):
    seq: int
    reward_list: list[pydantic.SerializeAsAny[item_model.Item]]


class PaymentProductListSubscriptionStatusLicenseInfo(pydantic.BaseModel):
    name: str
    items: list[PaymentProductListSubscriptionStatusLicenseInfoItem]


class PaymentProductListSubscriptionStatus(pydantic.BaseModel):
    license_id: int
    user_status: PaymentProductListSubscriptionStatusUserStatus
    license_info: PaymentProductListSubscriptionStatusLicenseInfo
    license_type: int


class PaymentProductListSubscription(pydantic.BaseModel):
    name: str
    price: int
    can_buy: bool
    item_list: list[PaymentProductListItemList]
    product_id: str
    product_url: str
    limit_status: pydantic.SerializeAsAny[PaymentProductListLimitStatus]
    product_type: int
    banner_img_asset: str  # "assets/image/shop/shop_banner/shop_banner_172.png"
    subscription_status: PaymentProductListSubscriptionStatus


class PaymentProductListResponse(pydantic.BaseModel):
    restriction_info: PaymentRestrictionInfo
    under_age_info: PaymentUnderAgeInfo
    sns_product_list: list[PaymentProductListSNS]
    product_list: list[PaymentProductList]
    subscription_list: list[PaymentProductListSubscription]
    show_point_shop: bool


class PaymentReceiptRequest(pydantic.BaseModel):
    receipt_data: str
    restore_flag: int


class PaymentReceiptProduct(user.UserDiffMixin):
    product_id: str
    name: str
    product_type: str
    description: str
    price: int
    item_list: list[pydantic.SerializeAsAny[item_model.Item]]
    is_in_app_billing: bool


class PaymentReceiptResponse(common.TimestampMixin):
    status: bool
    product: PaymentReceiptProduct


@idol.register("payment", "productList")
async def payment_productlist(context: idol.SchoolIdolUserParams) -> PaymentProductListResponse:
    # TODO
    util.stub("payment", "productList", context.raw_request_data)
    return PaymentProductListResponse(
        restriction_info=PaymentRestrictionInfo(restricted=False),
        under_age_info=PaymentUnderAgeInfo(birth_set=False, has_limit=False, limit_amount=None, month_used=0),
        sns_product_list=[],
        product_list=[],
        subscription_list=[],
        show_point_shop=True,
    )


@idol.register("payment", "receipt", batchable=False)
async def payment_receipt(context: idol.SchoolIdolUserParams, request: PaymentReceiptRequest) -> PaymentReceiptResponse:
    # TODO
    util.stub("payment", "receipt", request)
    product_id = re.match(
        r"holy linus in heaven, blessed be thy name, give us our daily ([\w\.]+) as in heaven so be it on this earth\.\.\.",
        request.receipt_data,
    )
    if product_id is not None:
        util.log(f"Got holy linus request: {product_id.group(1)}")
    raise idol.error.by_code(422)
