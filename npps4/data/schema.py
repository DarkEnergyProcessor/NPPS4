import base64
import hashlib

import Cryptodome.Cipher.AES
import Cryptodome.Hash.SHA256
import Cryptodome.Protocol.KDF
import pydantic
import pydantic.json_schema

from .. import const
from .. import util
from ..system import item_model

from typing import Literal, cast


class LiveUnitDrop(pydantic.BaseModel):
    unit_id: int
    weight: int


class LiveSpecificLiveUnitDrop(pydantic.BaseModel):
    live_setting_id: int
    drops: list[LiveUnitDrop]


class LiveUnitDropChance(pydantic.BaseModel):
    common: int
    live_specific: int


class ItemWithWeight(item_model.Item):
    weight: int


class LiveEffortRewardDrops(pydantic.BaseModel):
    live_effort_point_box_spec_id: int
    drops: list[ItemWithWeight]


class SecretboxCost(pydantic.BaseModel):
    cost_type: const.SECRETBOX_COST_TYPE
    cost_item_id: int | None = None
    cost_amount: int


class SecretboxButton(pydantic.BaseModel):
    name: str | None = None
    name_en: str | None = None
    button_type: const.SECRETBOX_BUTTON_TYPE
    costs: list[SecretboxCost]
    unit_count: int
    guarantee_specific_rarity_amount: int = 0  # 0 = no guarantee
    guaranteed_rarity: int = 0  # 0 = no guarantee, > 0 = 1-based index of rarity_pools
    rate_modifier: list[int] | None = None


class SecretboxData(pydantic.BaseModel):
    id_string: str
    name: str
    name_en: str | None
    member_category: int
    secretbox_type: const.SECRETBOX_LAYOUT_TYPE
    parcel_type: int  # 1 for regular, 2 for honor
    order: int
    start_time: int
    end_time: int

    add_gauge: int
    free_once_a_day_display: SecretboxCost | None = None  # Always scout 1. None = no free once a day.
    buttons: list[SecretboxButton]

    animation_layout_type: const.SECRETBOX_ANIMATION_TYPE
    animation_asset_layout: list[str]
    animation_asset_layout_en: list[str | None]
    menu_asset: str
    menu_asset_en: str | None

    rarity_names: list[str]
    rarity_rates: list[int]
    rarity_pools: list[list[int]]  # List of unit IDs in each pool

    @property
    def secretbox_id(self) -> int:
        return util.java_hash_code(self.id_string)


class SerialCodeHashed(pydantic.BaseModel):
    salt: pydantic.Base64UrlBytes
    hash: str


class SerialCodeGiveItem(pydantic.BaseModel):
    type: Literal["item"] = "item"
    message_en: str = "Serial Code Reward"
    message_jp: str = "Serial Code Reward"
    items: list[pydantic.SerializeAsAny[item_model.Item]]


class SerialCodeRunFunction(pydantic.BaseModel):
    type: Literal["run"] = "run"
    function: str  # Must be registered in npps4.serialcode:functions


SERIAL_CODE_ACTION_ADAPTER: pydantic.TypeAdapter[SerialCodeGiveItem | SerialCodeRunFunction] = pydantic.TypeAdapter(
    SerialCodeGiveItem | SerialCodeRunFunction
)


class SerialCode(pydantic.BaseModel):
    serial_code: str | SerialCodeHashed
    usage_limit: int = 0  # Limit per user, 0 = no limit
    start_time: int = 0  # Code valid start time
    end_time: int = 2147483647  # Code valid end time
    action: list[str] | SerialCodeGiveItem | SerialCodeRunFunction  # list of str means secure action

    def check_serial_code(self, input_code: str):
        match self.serial_code:
            case str():
                return self.serial_code == input_code
            case SerialCodeHashed():
                input_bytes = input_code.encode("utf-8")
                digest = hashlib.sha256(self.serial_code.salt + input_bytes, usedforsecurity=False)
                return digest.hexdigest().lower() == self.serial_code.hash.lower()
            case _:
                raise ValueError("invalid serial code type")

    def get_action(self, input_code: str):
        if isinstance(self.action, list):
            if not isinstance(self.serial_code, SerialCodeHashed):
                raise ValueError("cannot have secure action without secure serial code")

            # Need to decrypt
            key = Cryptodome.Protocol.KDF.PBKDF2(
                cast(str, input_code.encode("utf-8")),
                self.serial_code.salt,
                16,
                4,
                hmac_hash_module=Cryptodome.Hash.SHA256,
            )
            aes = Cryptodome.Cipher.AES.new(
                key, Cryptodome.Cipher.AES.MODE_CTR, nonce=self.serial_code.salt, initial_value=0
            )
            base64_data = base64.urlsafe_b64decode("".join(self.action))
            secure_action = aes.decrypt(base64_data)
            return SERIAL_CODE_ACTION_ADAPTER.validate_json(secure_action)

        return self.action


class SerializedServerData(pydantic.BaseModel):
    json_schema_link: pydantic.json_schema.SkipJsonSchema[str | None] = pydantic.Field(default=None, alias="$schema")
    badwords: list[str]  # Note: Badwords are Base64-encoded in the JSON file!
    live_unit_drop_chance: LiveUnitDropChance
    common_live_unit_drops: list[LiveUnitDrop]
    live_specific_live_unit_drops: list[LiveSpecificLiveUnitDrop]
    live_effort_drops: list[LiveEffortRewardDrops]
    secretbox_data: list[SecretboxData]
    serial_codes: list[SerialCode]
