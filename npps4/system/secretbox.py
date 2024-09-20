from . import item
from . import secretbox_model
from . import user
from .. import const
from .. import data
from .. import idol
from .. import util
from ..db import main


def _determine_en_path(context: idol.BasicSchoolIdolContext, path: str, path_en: str | None, /):
    if path_en is None or context.is_lang_jp():
        return path

    if path_en == "":
        return f"en/{path}"
    else:
        return path_en


def encode_cost_id(secretbox_id: int, button_index: int, cost_index: int, /):
    return (button_index << 36) | (cost_index << 32) | secretbox_id


def decode_cost_id(cost_id: int):
    secretbox_id = cost_id & 0xFFFFFFFF
    cost_index = (cost_id >> 32) & 0xF
    button_index = cost_id >> 36
    return secretbox_id, button_index, cost_index


async def query_secretbox_button(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    button: data.schema.SecretboxButton,
    secretbox_name: str,
    ids: tuple[int, int],
):
    costs = [
        secretbox_model.SecretboxAllCost(
            id=encode_cost_id(ids[0], ids[1], j),
            payable=await get_user_currency(context, user, cost.cost_type, cost.cost_item_id) >= cost.cost_amount,
            unit_count=button.unit_count,
            type=cost.cost_type,
            item_id=cost.cost_item_id,
            amount=cost.cost_amount,
        )
        for j, cost in enumerate(button.costs, 1)
    ]

    if button.balloon_asset is not None:
        return secretbox_model.SecretboxAllButtonWithBaloon(
            secret_box_button_type=button.button_type,
            cost_list=costs,
            secret_box_name=secretbox_name,
            balloon_asset=button.balloon_asset,
        )
    else:
        return secretbox_model.SecretboxAllButton(
            secret_box_button_type=button.button_type,
            cost_list=costs,
            secret_box_name=secretbox_name,
        )


async def get_secretbox_button_response(
    context: idol.BasicSchoolIdolContext, target_user: main.User, secretbox: data.schema.SecretboxData
):
    return [
        # TODO: Free once a day scouting
        await query_secretbox_button(
            context,
            target_user,
            button,
            context.get_text(secretbox.name, secretbox.name_en),
            (secretbox.secretbox_id, i),
        )
        for i, button in enumerate(secretbox.buttons, 1)
    ]


async def get_secretbox_info_response(
    context: idol.BasicSchoolIdolContext,
    target_user: main.User,
    secretbox: data.schema.SecretboxData,
    can_do_more: bool,
):
    return secretbox_model.SecretboxAllSecretboxInfo(
        secret_box_id=secretbox.secretbox_id,
        secret_box_type=secretbox.secretbox_type,
        name=context.get_text(secretbox.name, secretbox.name_en),
        start_date=util.timestamp_to_datetime(secretbox.start_time),
        end_date=util.timestamp_to_datetime(secretbox.end_time),
        add_gauge=0,  # TODO
        always_display_flag=1,
        pon_count=can_do_more * 100,  # TODO
    )


async def get_all_secretbox_data_response(context: idol.BasicSchoolIdolContext, target_user: main.User):
    server_data = data.get()
    member_category_list: dict[int, list[secretbox_model.SecretboxAllPage]] = {}

    for secretbox in server_data.secretbox_data.values():
        if len(secretbox.animation_asset_layout) > 3:
            animation_assets = secretbox_model.SecretboxAllAnimation3Asset(
                type=secretbox.animation_layout_type,
                background_asset=_determine_en_path(
                    context, secretbox.animation_asset_layout[0], secretbox.animation_asset_layout_en[0]
                ),
                additional_asset_1=_determine_en_path(
                    context, secretbox.animation_asset_layout[1], secretbox.animation_asset_layout_en[1]
                ),
                additional_asset_2=_determine_en_path(
                    context, secretbox.animation_asset_layout[2], secretbox.animation_asset_layout_en[2]
                ),
                additional_asset_3=_determine_en_path(
                    context, secretbox.animation_asset_layout[3], secretbox.animation_asset_layout_en[3]
                ),
            )
        else:
            animation_assets = secretbox_model.SecretboxAllAnimation2Asset(
                type=secretbox.animation_layout_type,
                background_asset=_determine_en_path(
                    context, secretbox.animation_asset_layout[0], secretbox.animation_asset_layout_en[0]
                ),
                additional_asset_1=_determine_en_path(
                    context, secretbox.animation_asset_layout[1], secretbox.animation_asset_layout_en[1]
                ),
                additional_asset_2=_determine_en_path(
                    context, secretbox.animation_asset_layout[2], secretbox.animation_asset_layout_en[2]
                ),
            )
        page = secretbox_model.SecretboxAllPage(
            menu_asset=_determine_en_path(context, secretbox.menu_asset, secretbox.menu_asset_en),
            page_order=secretbox.order,
            animation_assets=animation_assets,
            button_list=await get_secretbox_button_response(context, target_user, secretbox),
            secret_box_info=await get_secretbox_info_response(context, target_user, secretbox, False),
        )
        member_category_list.setdefault(secretbox.member_category, []).append(page)

    return sorted(
        (
            secretbox_model.SecretboxAllMemberCategory(member_category=k, page_list=v)
            for k, v in member_category_list.items()
        ),
        key=lambda k: k.member_category,
    )


def get_secretbox_data(secretbox_id: int):
    server_data = data.get()
    return server_data.secretbox_data[secretbox_id]


def roll_units(
    secretbox_id: int,
    amount: int,
    /,
    *,
    guarantee_rarity: int = 0,
    guarantee_amount: int = 0,
    rate_modifier: list[int] | None = None,
):
    secretbox_data = get_secretbox_data(secretbox_id)
    # Calculate weighted probabilities
    rates = rate_modifier if rate_modifier is not None else secretbox_data.rarity_rates
    picked_rarity_index = util.SYSRAND.choices(range(len(secretbox_data.rarity_rates)), rates, k=amount)

    if guarantee_rarity > 0 and guarantee_amount > 0:
        rindex = guarantee_rarity - 1
        indices = range(amount)
        while sum(k >= rindex for k in picked_rarity_index) < guarantee_amount:
            random_index = util.SYSRAND.choice(indices)
            if picked_rarity_index[random_index] < rindex:
                picked_rarity_index[random_index] = rindex

    # Start rolling
    return [util.SYSRAND.choice(secretbox_data.rarity_pools[i]) for i in picked_rarity_index]


def get_secretbox_button(secretbox_data: int | data.schema.SecretboxData, button_index: int):
    if isinstance(secretbox_data, int):
        secretbox_data = get_secretbox_data(secretbox_id=secretbox_data)
    return secretbox_data.buttons[button_index - 1]


async def get_user_currency(
    context: idol.BasicSchoolIdolContext,
    target_user: main.User,
    /,
    cost_type: const.SECRETBOX_COST_TYPE,
    cost_item_id: int | None,
):
    match cost_type:
        case const.SECRETBOX_COST_TYPE.ITEM_TICKET:
            if cost_item_id is None:
                raise ValueError("Empty item_id for type 1000")
            return await item.get_item_count(context, target_user, cost_item_id)
        case const.SECRETBOX_COST_TYPE.GAME_COIN:
            return target_user.game_coin
        case const.SECRETBOX_COST_TYPE.LOVECA:
            return user.get_loveca(target_user, include_free=cost_item_id != 1)
        case const.SECRETBOX_COST_TYPE.FRIEND:
            return target_user.social_point
        case _:
            return 0


async def sub_user_currency(
    context: idol.BasicSchoolIdolContext,
    target_user: main.User,
    /,
    cost_type: const.SECRETBOX_COST_TYPE,
    cost_item_id: int | None,
    amount: int,
):
    match cost_type:
        case const.SECRETBOX_COST_TYPE.ITEM_TICKET:
            if cost_item_id is None:
                raise ValueError("Empty item_id for type 1000")
            await item.add_item(context, target_user, cost_item_id, -amount)
        case const.SECRETBOX_COST_TYPE.GAME_COIN:
            target_user.game_coin = target_user.game_coin - amount
        case const.SECRETBOX_COST_TYPE.LOVECA:
            user.sub_loveca(target_user, amount, sub_paid_only=cost_item_id == 1)
        case const.SECRETBOX_COST_TYPE.FRIEND:
            target_user.social_point = target_user.social_point - amount
