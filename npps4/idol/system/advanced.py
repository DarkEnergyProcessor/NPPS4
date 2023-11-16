import dataclasses

from . import item
from . import unit
from ... import idol
from ... import util
from ...const import ADD_TYPE
from ...idol.system import achievement
from ...idol.system import background
from ...idol.system import scenario
from ...db import main


@dataclasses.dataclass
class AddResult:
    success: bool
    reason_unit_full: bool = False

    def __nonzero__(self):
        return self.success


async def add_item(context: idol.BasicSchoolIdolContext, user: main.User, item: item.Item):
    match item.add_type:
        case ADD_TYPE.ITEM:
            match item.item_id:
                case 2:
                    user.social_point = user.social_point + item.amount
                    return AddResult(True)
                case 3:
                    user.game_coin = user.game_coin + item.amount
                    return AddResult(True)
                case 4:
                    user.free_sns_coin = user.free_sns_coin + item.amount
                    return AddResult(True)
                case _:
                    return AddResult(True)  # TODO
        case ADD_TYPE.UNIT:
            unit_cnt = await unit.count_units(context, user, True)
            if unit_cnt < user.unit_max:
                await unit.add_unit(context, user, item.item_id, True)
                return AddResult(True)
            else:
                return AddResult(False, reason_unit_full=True)
        case ADD_TYPE.GAME_COIN:
            user.game_coin = user.game_coin + item.amount
            return AddResult(True)
        case ADD_TYPE.LOVECA:
            user.free_sns_coin = user.free_sns_coin + item.amount
            return AddResult(True)
        case ADD_TYPE.SOCIAL_POINT:
            user.social_point = user.social_point + item.amount
            return AddResult(True)
        case ADD_TYPE.BACKGROUND:
            await background.unlock_background(context, user, item.item_id)
            return AddResult(True)
        case ADD_TYPE.SCENARIO:
            await scenario.unlock(context, user, item.item_id)
            return AddResult(True)
        case _:
            return AddResult(True)  # TODO
