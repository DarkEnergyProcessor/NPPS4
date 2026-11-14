from .stickers import award
from .stickers import background
from .stickers import updown
from .. import schema
from ... import const

sticker_shop: list[schema.StickerShop] = [
    schema.StickerShop(
        id_string="blue_ticket",
        add_type=const.ADD_TYPE.ITEM,
        item_id=5,
        name="補助チケット",
        name_en="Scouting Coupon",
        costs=[
            schema.ExchangeCost(rarity=2, cost=40),
            schema.ExchangeCost(rarity=3, cost=2),
        ],
    ),
    *updown.sticker,
    *background.sticker,
    *award.sticker,
    schema.StickerShop(
        id_string="cg?",
        add_type=const.ADD_TYPE.MUSEUM,
        item_id=1698,
        name="ささやかな幸せ",
        name_en="Small Happiness",
        costs=[schema.ExchangeCost(rarity=6, cost=5)],
    ),
]
