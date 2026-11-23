from . import schema
from .server_data_baseline import achievement_reward
from .server_data_baseline import common_live_unit_drops
from .server_data_baseline import live_effort_drops
from .server_data_baseline import live_specific_live_unit_drops
from .server_data_baseline import secretbox_data
from .server_data_baseline import serial_codes
from .server_data_baseline import sticker_shop

server_data = schema.SerializedServerData(
    badwords=set(),
    achievement_reward=achievement_reward.achievement_reward,
    live_unit_drop_chance=schema.LiveUnitDropChance(common=9, live_specific=1),
    common_live_unit_drops=common_live_unit_drops.common_live_unit_drops,
    live_specific_live_unit_drops=live_specific_live_unit_drops.live_specific_live_unit_drops,
    live_effort_drops=live_effort_drops.live_effort_drops,
    secretbox_data=secretbox_data.secretbox_data,
    serial_codes=serial_codes.serial_codes,
    sticker_shop=sticker_shop.sticker_shop,
)
