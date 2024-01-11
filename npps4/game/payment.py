from .. import idol
from .. import util

import pydantic


class PaymentRestrictionInfo(pydantic.BaseModel):
    restricted: bool


class PaymentUnderAgeInfo(pydantic.BaseModel):
    birth_set: bool
    has_limit: bool
    limit_amount: int | None
    month_used: int


class PaymentProductList(pydantic.BaseModel):
    # https://github.com/DarkEnergyProcessor/NPPS/blob/v3.1.x/modules/payment/productList.php
    # TODO: Rectify if that's still correct.
    apple_product_id: str
    google_product_id: str
    name: str
    price: int
    price_tier: int
    sns_coin: int
    insert_date: str
    update_date: str
    product_id: str


class ProductListResponse(pydantic.BaseModel):
    restriction_info: PaymentRestrictionInfo
    under_age_info: PaymentUnderAgeInfo
    sns_product_list: list
    product_list: list[PaymentProductList]
    subscription_list: list
    show_point_shop: bool


@idol.register("payment", "productList")
async def payment_productlist(context: idol.SchoolIdolUserParams) -> ProductListResponse:
    # TODO
    util.stub("payment", "productList", context.raw_request_data)
    return ProductListResponse(
        restriction_info=PaymentRestrictionInfo(restricted=False),
        under_age_info=PaymentUnderAgeInfo(birth_set=False, has_limit=False, limit_amount=None, month_used=0),
        sns_product_list=[],
        product_list=[],
        subscription_list=[],
        show_point_shop=True,
    )
