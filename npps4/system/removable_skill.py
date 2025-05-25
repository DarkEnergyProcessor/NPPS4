import math

from . import unit
from . import unit_model
from .. import idol
from ..db import main


def apply_stats(
    effect_type: int, effect_value: float, fixed: bool, smile: int, pure: int, cool: int
) -> tuple[int, int, int]:
    match effect_type:
        case 1:
            if fixed:
                return int(effect_value), 0, 0
            else:
                return math.floor(smile * effect_value / 100.0), 0, 0
        case 2:
            if fixed:
                return 0, int(effect_value), 0
            else:
                return 0, math.floor(pure * effect_value / 100.0), 0
        case 3:
            if fixed:
                return 0, 0, int(effect_value)
            else:
                return 0, 0, math.floor(cool * effect_value / 100.0)

    return (0, 0, 0)


async def can_apply(
    context: idol.BasicSchoolIdolContext, trigger_reference_type: int, trigger_type: int, player_units: list[main.Unit]
):
    match trigger_reference_type:
        case 0:
            return True
        case 4:
            for unit_data in player_units:
                unit_info = await unit.get_unit_info(context, unit_data.unit_id)

                if not await unit.unit_type_has_tag(context, unit_info.unit_type_id, trigger_type):
                    return False

            return True
        case _:
            return False
