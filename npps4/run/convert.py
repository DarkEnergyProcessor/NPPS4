from .. import script_dummy  # type: ignore # isort:skip!

import base64
import itertools

import fastapi
import pydantic

from .. import idol
from .. import util
from ..game import album
from ..game import award
from ..game import background
from ..game import exchange
from ..game import item
from ..game import live
from ..game import museum
from ..game import scenario
from ..game import subscenario
from ..game import unit
from ..game import user
from ..system import lila
from ..system import unit_model

from typing import Any, Literal

app = fastapi.FastAPI(title="SIF2NPPS4", version="0.0.0")


class APIResponse[T: pydantic.BaseModel](pydantic.BaseModel):
    result: T
    status: Literal[200]
    timeStamp: int


class SIFResponse[T](pydantic.BaseModel):
    response_data: T
    release_info: Any
    status_code: Literal[200]


class ConvertRequest(pydantic.BaseModel):
    userinfo: SIFResponse[user.UserInfoResponse]
    api1: SIFResponse[
        tuple[
            APIResponse[live.LiveStatusResponse],  # 0
            Any,  # live/schedule
            APIResponse[unit.UnitAllInfoResponse],  # 2
            APIResponse[unit.UnitDeckInfoResponse],  # 3
            APIResponse[unit_model.SupporterListInfoResponse],  # 4
            APIResponse[unit_model.RemovableSkillInfoResponse],  # 5
            Any,  # costume/costumeList
            APIResponse[album.AlbumAllResponse],  # 7
            APIResponse[scenario.ScenarioStatusResponse],  # 8
            APIResponse[subscenario.SubScenarioStatusResponse],  # 9
            Any,  # eventscenario/status
            Any,  # multiunit/multiunitscenarioStatus
            Any,  # payment/productList
            Any,  # banner/bannerList
            Any,  # notice/noticeMarquee
            APIResponse[user.UserGetNaviResponse],  # 15
            Any,  # navigation/specialCutin
            APIResponse[award.AwardInfoResponse],  # 17
            APIResponse[background.BackgroundInfoResponse],  # 18
            Any,  # stamp/stampInfo
            APIResponse[exchange.ExchangePointResponse],  # 20
            Any,  # livese/liveseInfo
            Any,  # liveicon/liveiconInfo
            APIResponse[item.ItemListResponse],  # 23
            Any,  # marathon/marathonInfo
            Any,  # challenge/challengeInfo
        ]
    ]
    api2: SIFResponse[
        tuple[
            Any,  # login/topInfo
            Any,  # login/topInfoOnce
            Any,  # unit/accessoryAll
            APIResponse[museum.MuseumInfoResponse],
        ]
    ]
    server_key: str | None = None


class ConvertResponse(pydantic.BaseModel):
    error: str | None = None
    account_data: str | None = None
    signature: str | None = None


@app.get("/", response_class=fastapi.responses.HTMLResponse)
async def main():
    with open("templates/convert.html", "r", encoding="utf-8") as f:
        return fastapi.responses.HTMLResponse(f.read())


@app.post("/")
async def convert(request: fastapi.Request, request_data: ConvertRequest) -> ConvertResponse:
    try:
        user_data = lila.UserData(
            key=None,
            passwd=None,
            transfer_sha1=None,
            name=request_data.userinfo.response_data.user.name,
            bio="Hello!",
            exp=request_data.userinfo.response_data.user.exp,
            coin=request_data.userinfo.response_data.user.game_coin,
            sns_coin=[
                request_data.userinfo.response_data.user.free_sns_coin,
                request_data.userinfo.response_data.user.paid_sns_coin,
            ],
            friend_pts=request_data.userinfo.response_data.user.social_point,
            unit_max=request_data.userinfo.response_data.user.unit_max,
            waiting_unit_max=request_data.userinfo.response_data.user.waiting_unit_max,
            energy_max=request_data.userinfo.response_data.user.energy_max,
            energy_full_time=util.datetime_to_timestamp(request_data.userinfo.response_data.user.energy_full_time),
            license_live_energy_recoverly_time=request_data.userinfo.response_data.user.license_live_energy_recoverly_time,
            energy_full_need_time=request_data.userinfo.response_data.user.energy_full_need_time,
            over_max_energy=request_data.userinfo.response_data.user.over_max_energy,
            training_energy=request_data.userinfo.response_data.user.training_energy,
            training_energy_max=request_data.userinfo.response_data.user.training_energy_max,
            friend_max=request_data.userinfo.response_data.user.friend_max,
            tutorial_state=request_data.userinfo.response_data.user.tutorial_state,
            active_deck_index=0,  # set later
            active_background=0,  # set later
            active_award=0,  # set later
            live_effort_point_box_spec_id=1,
            limited_effort_event_id=0,
            current_live_effort_point=0,
            current_limited_effort_point=0,
        )

        # Backgrounds
        background_list: list[int] = []
        for info in request_data.api1.response_data[18].result.background_info:
            if info.is_set:
                user_data.active_background = info.background_id
            background_list.append(info.background_id)

        # Awards
        award_list: list[int] = []
        for info in request_data.api1.response_data[17].result.award_info:
            if info.is_set:
                user_data.active_award = info.award_id
            award_list.append(info.award_id)

        # Iterate all units
        unit_data_list: list[lila.UnitData] = []
        unit_owning_user_id_lookup: dict[int, int] = {}  # [unit_owning_user_id, index+1]
        for unit_list, active in (
            (request_data.api1.response_data[2].result.active, True),
            (request_data.api1.response_data[2].result.waiting, False),
        ):
            for unit_data in unit_list:
                unit_data_serialized = lila.UnitData(
                    unit_id=unit_data.unit_id,
                    # bits: 0 = active, 1 = fav. flag, 2 = signed, 3-4 = rank, 5-6 = display rank
                    flags=active
                    | (unit_data.favorite_flag << 1)
                    | (unit_data.is_signed << 2)
                    | (unit_data.rank << 3)
                    | (unit_data.display_rank << 5),
                    exp=unit_data.exp,
                    skill_exp=unit_data.unit_skill_exp,
                    max_level=unit_data.max_level,
                    love=unit_data.love,
                    level_limit_id=unit_data.level_limit_id,
                    removable_skill_capacity=unit_data.unit_removable_skill_capacity,
                    removable_skills=[],
                )
                unit_data_list.append(unit_data_serialized)
                unit_owning_user_id_lookup[unit_data.unit_owning_user_id] = len(unit_data_list)

        # Set center
        user_data.center_unit_owning_user_id = unit_owning_user_id_lookup[
            request_data.api1.response_data[15].result.user.unit_owning_user_id
        ]

        # Supporter unit
        supp_unit_list: list[lila.CommonItemData] = [
            lila.CommonItemData(id=info.unit_id, amount=info.amount)
            for info in request_data.api1.response_data[4].result.unit_support_list
        ]

        # Deck data
        deck_data_list: list[lila.DeckData] = []
        for deck in request_data.api1.response_data[3].result.root:
            positions = [0] * 9
            for position in deck.unit_owning_user_ids:
                positions[position.position - 1] = unit_owning_user_id_lookup[position.unit_owning_user_id]
            deck_data_list.append(lila.DeckData(name=deck.deck_name, index=deck.unit_deck_id, units=positions))

            if deck.main_flag:
                user_data.active_deck_index = deck.unit_deck_id

        # SIS/Removable Skill
        removable_skill_data = request_data.api1.response_data[5].result
        removable_skill_list = [
            lila.CommonItemData(id=info.unit_removable_skill_id, amount=info.total_amount)
            for info in removable_skill_data.owning_info
        ]
        for equip_info in removable_skill_data.equipment_info.values():
            unit_data = unit_data_list[unit_owning_user_id_lookup[equip_info.unit_owning_user_id] - 1]
            unit_data.removable_skills = [d.unit_removable_skill_id for d in equip_info.detail]

        # FIXME: Import main story data and somehow derive achievement from it.

        # Subscenario
        subscenario_encoded_list = [
            sc.subscenario_id * int((-1) ** sc.status)
            for sc in request_data.api1.response_data[9].result.subscenario_status_list
        ]

        # Live clear
        live_clear_data = [
            lila.LiveClearData(
                live_difficulty_id=lc.live_difficulty_id,
                hi_score=lc.hi_score,
                hi_combo_cnt=lc.hi_combo_count,
                clear_cnt=lc.clear_cnt,
            )
            for lc in itertools.chain(
                request_data.api1.response_data[0].result.normal_live_status_list,
                request_data.api1.response_data[0].result.special_live_status_list,
                request_data.api1.response_data[0].result.training_live_status_list,
            )
        ]

        # Regular items
        general_item_list = [
            lila.CommonItemData(id=info.item_id, amount=info.amount)
            for info in request_data.api1.response_data[23].result.general_item_list
            if info.amount > 0
        ]
        buff_item_list = [
            lila.CommonItemData(id=info.item_id, amount=info.amount)
            for info in request_data.api1.response_data[23].result.buff_item_list
            if info.amount > 0
        ]
        reinforce_item_list = [
            lila.CommonItemData(id=info.item_id, amount=info.amount)
            for info in request_data.api1.response_data[23].result.reinforce_item_list
            if info.amount > 0
        ]

        # Recovery items
        recovery_item_list = [
            lila.CommonItemData(id=info.item_id, amount=info.amount)
            for info in request_data.userinfo.response_data.user.lp_recovery_item
            if info.amount > 0
        ]

        # Exchange
        exchange_points = [
            lila.CommonItemData(id=info.rarity, amount=info.exchange_point)
            for info in request_data.api1.response_data[20].result.exchange_point_list
            if info.exchange_point > 0
        ]

        # TODO: Normal live unlock

        account_data = lila.AccountData(
            user=user_data,
            background=background_list,
            award=award_list,
            unit=unit_data_list,
            supp_unit=supp_unit_list,
            sis=removable_skill_list,
            deck=deck_data_list,
            achievement=[],
            login_bonus=[],
            present_box=[],
            scenario=[],
            subscenario=subscenario_encoded_list,
            museum=request_data.api2.response_data[3].result.museum_info.contents_id_list,
            live_clear=live_clear_data,
            normal_live_unlock=[],
            items=general_item_list,
            buff_items=buff_item_list,
            reinforce_items=reinforce_item_list,
            recovery_items=recovery_item_list,
            exchange=exchange_points,
        )

        payload, signature = lila.export_account_data(
            account_data,
            (
                None
                if (request_data.server_key is None or len(request_data.server_key) == 0)
                else request_data.server_key.encode("utf-8")
            ),
        )

        return ConvertResponse(
            account_data=str(base64.urlsafe_b64encode(payload), "utf-8"),
            signature=str(base64.urlsafe_b64encode(signature), "utf-8"),
        )
    except Exception as e:
        return ConvertResponse(error=str(e))
