from . import secretbox_model
from .. import data
from .. import idol
from .. import util
from ..db import main


def _determine_en(context: idol.BasicSchoolIdolContext, text: str, text_en: str | None, /):
    if context.is_lang_jp():
        return text
    else:
        return text_en if text_en is not None else text


def _determine_en_path(context: idol.BasicSchoolIdolContext, path: str, path_en: str | None, /):
    if path_en is None or context.is_lang_jp():
        return path

    if path_en == "":
        return f"en/{path}"
    else:
        return path_en


def _encode_cost_id(secretbox_id: int, button_index: int, cost_index: int, /):
    return (button_index << 36) | (cost_index << 32) | secretbox_id


async def get_secretbox_data(context: idol.BasicSchoolIdolContext, user: main.User):
    server_data = data.get()
    member_category_list: dict[int, list[secretbox_model.SecretboxAllPage]] = {}

    for secretbox in server_data.secretbox_data.values():
        secretbox_id = secretbox.secretbox_id
        page = secretbox_model.SecretboxAllPage(
            menu_asset=_determine_en_path(context, secretbox.menu_asset, secretbox.menu_asset_en),
            page_order=secretbox.order,
            # TODO: Detect SecretboxAllAnimation2Asset
            animation_assets=secretbox_model.SecretboxAllAnimation3Asset(
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
            ),
            button_list=[
                # TODO: Free once a day scouting
                secretbox_model.SecretboxAllButton(
                    secret_box_button_type=button.button_type,
                    cost_list=[
                        secretbox_model.SecretboxAllCost(
                            id=_encode_cost_id(secretbox_id, i, j),
                            payable=False,
                            unit_count=button.unit_count,
                            type=cost.cost_type,
                            item_id=cost.cost_item_id,
                            amount=cost.cost_amount,
                        )
                        for j, cost in enumerate(button.costs, 1)
                    ],
                    secret_box_name=_determine_en(context, secretbox.name, secretbox.name_en),
                )
                for i, button in enumerate(secretbox.buttons, 1)
            ],
            secret_box_info=secretbox_model.SecretboxAllSecretboxInfo(
                secret_box_id=secretbox.secretbox_id,
                secret_box_type=secretbox.secretbox_type,
                name=_determine_en(context, secretbox.name, secretbox.name_en),
                start_date=util.timestamp_to_datetime(secretbox.start_time),
                end_date=util.timestamp_to_datetime(secretbox.end_time),
                add_gauge=0,  # TODO
                always_display_flag=1,
                pon_count=0,  # TODO
            ),
        )
        member_category_list.setdefault(secretbox.member_category, []).append(page)

    return sorted(
        (
            secretbox_model.SecretboxAllMemberCategory(member_category=k, page_list=v)
            for k, v in member_category_list.items()
        ),
        key=lambda k: k.member_category,
    )
