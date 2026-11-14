"""Baseline server data: serial_codes."""

from .. import schema
from ... import const
from ...system import item_model

serial_codes = [
    schema.SerialCode(
        serial_code="KMZWA8AWAA",
        usage_limit=schema.SerialCodeUsageLimit(id="KMZWA8AWAA", **{"global": False}, amount=1),
        action=schema.SerialCodeGiveItem(
            items=[
                item_model.BaseItem(add_type=const.ADD_TYPE.UNIT, item_id=3546, extra_data={"is_signed": True}),
                item_model.BaseItem(add_type=const.ADD_TYPE.UNIT, item_id=3547, extra_data={"is_signed": True}),
                item_model.BaseItem(add_type=const.ADD_TYPE.UNIT, item_id=3548, extra_data={"is_signed": True}),
                item_model.BaseItem(add_type=const.ADD_TYPE.UNIT, item_id=3549, extra_data={"is_signed": True}),
            ]
        ),
    ),
    schema.SerialCode(
        serial_code=schema.SerialCodeHashed(
            salt=b"snmSVeQtKlveL6hN5AeYfA==", hash="439ce0e3abe0b98db77312e06acfc1b7d786de611cfadd9b4162c38866791b2d"
        ),
        action=[
            "iuq2Sbj3tAQEXrINolyos5AKWtwwa7ZCizh3hwfMlonslRzx2_oDmo4ePqtwZ16NDHvzS7rB3EdFx5yP",
            "baQ4k7EIxJZggnv20kvZQCccmUiJu75ODufBpEfEu52pzm4fhh4-axJTctdLtJWMFX2smba3D16P54s1",
            "dojnTyh5UptPPqm7nI2IUXEQlwEemX1QX-m2n9F2ZGCAgdTmCKGcMlboHI4CbWMdFsqxC8RHEm4qmnn7",
            "rP3GZDrQGaIM8qydbJ2jvPPtC8MPKQVo",
        ],
    ),
    schema.SerialCode(
        serial_code="HESOYAM",
        action=schema.SerialCodeGiveItem(
            message_en="Health, Armour, and Money ($250,000)",
            message_jp="健康、防具、お金 ($250,000)",
            items=[
                item_model.BaseItem(add_type=const.ADD_TYPE.LOVECA, item_id=4, amount=50),
                item_model.BaseItem(add_type=const.ADD_TYPE.SOCIAL_POINT, item_id=2, amount=1000),
                item_model.BaseItem(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=250000),
            ],
        ),
        caster="upper",
    ),
    schema.SerialCode(
        serial_code="INEEDSOMEHELP",
        action=schema.SerialCodeGiveItem(
            message_en="Health, Armour, and Money ($250,000)",
            message_jp="健康、防具、お金 ($250,000)",
            items=[
                item_model.BaseItem(add_type=const.ADD_TYPE.LOVECA, item_id=4, amount=50),
                item_model.BaseItem(add_type=const.ADD_TYPE.SOCIAL_POINT, item_id=2, amount=1000),
                item_model.BaseItem(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=250000),
            ],
        ),
        caster="upper",
    ),
    schema.SerialCode(
        serial_code="ICANGOALLNIGHT",
        action=schema.SerialCodeGiveItem(
            message_en="Foo",
            message_jp="Bar",
            items=[
                item_model.BaseItem(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=777002, amount=50),
                item_model.BaseItem(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=3, amount=50),
            ],
        ),
        caster="upper",
    ),
    schema.SerialCode(
        serial_code="VKYPQCF",
        action=schema.SerialCodeGiveItem(
            message_en="Foo",
            message_jp="Bar",
            items=[
                item_model.BaseItem(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=777002, amount=50),
                item_model.BaseItem(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=3, amount=50),
            ],
        ),
        caster="upper",
    ),
    schema.SerialCode(
        serial_code="Qk4KcP1VGIc", action=schema.SerialCodeRunFunction(function="give_all_supporter_units")
    ),
    schema.SerialCode(
        serial_code="youtu.be/Qk4KcP1VGIc", action=schema.SerialCodeRunFunction(function="give_all_supporter_units")
    ),
    schema.SerialCode(
        serial_code="https://youtu.be/Qk4KcP1VGIc",
        action=schema.SerialCodeRunFunction(function="give_all_supporter_units"),
    ),
    schema.SerialCode(
        serial_code="https://www.youtube.com/watch?v=Qk4KcP1VGIc",
        action=schema.SerialCodeRunFunction(function="give_all_supporter_units"),
    ),
    schema.SerialCode(
        serial_code="PHOEBE IS CUTE",
        usage_limit=schema.SerialCodeUsageLimit(id="Phoebe", **{"global": False}, amount=50),
        action=schema.SerialCodeGiveItem(
            message_en="Phoebe is cute",
            message_jp="フィービーかわいい",
            items=[item_model.BaseItem(add_type=const.ADD_TYPE.ITEM, item_id=5, amount=25)],
        ),
        caster="upper",
    ),
]
