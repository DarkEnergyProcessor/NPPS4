import base64
import dataclasses
import json
import os
import time

from . import schema
from ..config import config


@dataclasses.dataclass
class ServerData:
    json_schema_link: str | None
    badwords: list[str]
    live_unit_drop_chance: schema.LiveUnitDropChance
    common_live_unit_drops: list[schema.LiveUnitDrop]
    live_specific_live_unit_drops: dict[int, list[schema.LiveUnitDrop]]
    live_effort_drops: dict[int, list[schema.BaseItemWithWeight]]
    secretbox_data: dict[int, schema.SecretboxData]
    serial_codes: list[schema.SerialCode]


SERVER_DATA_PATH = config.get_server_data_path()
server_data: ServerData | None = None
last_server_data_timestamp: int = 0


def get():
    global server_data, last_server_data_timestamp

    stat = os.stat(SERVER_DATA_PATH)
    if server_data is None or stat.st_mtime_ns > last_server_data_timestamp:
        try:
            with open(SERVER_DATA_PATH, "r", encoding="utf-8", newline="") as f:
                serialized_data = schema.SerializedServerData.model_validate(json.load(f))

                server_data = ServerData(
                    json_schema_link=serialized_data.json_schema_link,
                    badwords=[str(base64.urlsafe_b64decode(s), "utf-8") for s in serialized_data.badwords],
                    live_unit_drop_chance=serialized_data.live_unit_drop_chance,
                    common_live_unit_drops=serialized_data.common_live_unit_drops,
                    live_specific_live_unit_drops=dict(
                        (d.live_setting_id, d.drops) for d in serialized_data.live_specific_live_unit_drops
                    ),
                    live_effort_drops=dict(
                        (d.live_effort_point_box_spec_id, d.drops) for d in serialized_data.live_effort_drops
                    ),
                    secretbox_data={sb.secretbox_id: sb for sb in serialized_data.secretbox_data},
                    serial_codes=serialized_data.serial_codes,
                )
                last_server_data_timestamp = stat.st_mtime_ns
        except json.JSONDecodeError as e:
            if server_data is None:
                raise e from None
            # Return old data
            return server_data

    return server_data


def update():
    global last_server_data_timestamp
    server_data = get()  # ensure not None
    serialized_data = schema.SerializedServerData(
        badwords=[str(base64.urlsafe_b64encode(s.encode("utf-8")), "utf-8") for s in server_data.badwords],
        live_unit_drop_chance=server_data.live_unit_drop_chance,
        common_live_unit_drops=server_data.common_live_unit_drops,
        live_specific_live_unit_drops=[
            schema.LiveSpecificLiveUnitDrop(live_setting_id=live_setting_id, drops=drops)
            for live_setting_id, drops in server_data.live_specific_live_unit_drops.items()
        ],
        live_effort_drops=[
            schema.LiveEffortRewardDrops(live_effort_point_box_spec_id=live_effort_point_box_spec_id, drops=drops)
            for live_effort_point_box_spec_id, drops in server_data.live_effort_drops.items()
        ],
        secretbox_data=list(server_data.secretbox_data.values()),
        serial_codes=server_data.serial_codes,
    )
    serialized_data.json_schema_link = server_data.json_schema_link

    json_dict = serialized_data.model_dump(mode="json", exclude_defaults=True, by_alias=True)
    json_encoded = json.dumps(json_dict, ensure_ascii=False, indent="\t")

    t = time.time_ns()
    temp_filename = SERVER_DATA_PATH + f"temp_{t}.json"
    with open(temp_filename, "w", encoding="utf-8", newline="\n") as f:
        f.write(json_encoded)
    os.replace(temp_filename, SERVER_DATA_PATH)

    server_data = dataclasses.replace(server_data)  # Create new copy
    last_server_data_timestamp = time.time_ns()
