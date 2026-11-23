import dataclasses

from . import baseline
from . import schema
from .. import util
from ..system import item_model

from typing import Callable


@dataclasses.dataclass
class ServerData:
    json_schema_link: str | None
    badwords: list[str]
    achievement_reward: dict[int, list[item_model.BaseItem]]
    live_unit_drop_chance: schema.LiveUnitDropChance
    common_live_unit_drops: list[schema.LiveUnitDrop]
    live_specific_live_unit_drops: dict[int, list[schema.LiveUnitDrop]]
    live_effort_drops: dict[int, list[schema.BaseItemWithWeight]]
    secretbox_data: dict[int, schema.SecretboxData]
    serial_codes: list[schema.SerialCode]
    sticker_shop: list[schema.StickerShop]


def ensure_no_conflict[T: schema.HasIDString, E: Exception](
    items: list[T], exc_type: Callable[[str], E] = Exception, /
):
    ids: dict[int, str] = {}
    for item in items:
        item_id = item._internal_id
        if item_id in ids:
            raise exc_type(
                f"conflict item id string between '{item.id_string}' and '{ids[item_id]}' (id number is {item_id})"
            )
        ids[item_id] = item.id_string
    return items


server_data: ServerData | None = None


def get():
    global server_data

    if server_data is None:
        try:
            serialized_data = baseline.server_data.model_copy(deep=True)
            new_server_data = ServerData(
                json_schema_link=serialized_data.json_schema_link,
                badwords=serialized_data.badwords,
                achievement_reward=dict((k.achievement_id, k.rewards) for k in serialized_data.achievement_reward),
                live_unit_drop_chance=serialized_data.live_unit_drop_chance,
                common_live_unit_drops=serialized_data.common_live_unit_drops,
                live_specific_live_unit_drops=dict(
                    (d.live_setting_id, d.drops) for d in serialized_data.live_specific_live_unit_drops
                ),
                live_effort_drops=dict(
                    (d.live_effort_point_box_spec_id, d.drops) for d in serialized_data.live_effort_drops
                ),
                secretbox_data={sb.secretbox_id: sb for sb in ensure_no_conflict(serialized_data.secretbox_data)},
                serial_codes=serialized_data.serial_codes,
                sticker_shop=ensure_no_conflict(serialized_data.sticker_shop),
            )
            server_data = new_server_data
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise e from None
            elif server_data is None:
                raise
            util.log("Cannot load new data, using old data for now", util.logging.ERROR, e)
        finally:
            pass

    return server_data
