from . import item
from . import unit
from ... import idol
from ... import util
from ...idol.system import achievement
from ...idol.system import background
from ...db import main


async def add_item(context: idol.BasicSchoolIdolContext, user: main.User, item: item.Item):
    match item.add_type:
        case 1000:
            match item.item_id:
                case 2:
                    user.social_point = user.social_point + item.amount
                case 3:
                    user.game_coin = user.game_coin + item.amount
                case 4:
                    user.free_sns_coin = user.free_sns_coin + item.amount
                case _:
                    pass  # TODO
        case 1001:
            unit_cnt = await unit.count_units(context, user, True)
            if unit_cnt < user.unit_max:
                await unit.add_unit(context, user, item.item_id, True)
            else:
                raise ValueError("max unit reached")  # TODO: Proper idol.error.IdolError
        case 3000:
            user.game_coin = user.game_coin + item.amount
        case 3001:
            user.free_sns_coin = user.free_sns_coin + item.amount
        case 3002:
            user.social_point = user.social_point + item.amount
        case _:
            pass
