import math

from . import unit
from .. import idol
from ..db import main
from ..db import unit as unit_db


def apply_stats(
    effect_type: int, effect_value: float, fixed: bool, smile: int, pure: int, cool: int
) -> tuple[int, int, int]:
    match effect_type:
        case 1:
            if fixed:
                return int(effect_value), 0, 0
            else:
                return math.ceil(smile * effect_value / 100.0), 0, 0
        case 2:
            if fixed:
                return 0, int(effect_value), 0
            else:
                return 0, math.ceil(pure * effect_value / 100.0), 0
        case 3:
            if fixed:
                return 0, 0, int(effect_value)
            else:
                return 0, 0, math.ceil(cool * effect_value / 100.0)

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


async def can_apply_to_unit(
    context: idol.BasicSchoolIdolContext, removable_skill: unit_db.RemovableSkill, unit_info: unit_db.Unit
):
    match removable_skill.target_reference_type:
        case 0:
            return True
        case 1:
            return await unit.unit_type_has_tag(context, unit_info.unit_type_id, removable_skill.target_type)
        case 2:
            return unit_info.unit_type_id == removable_skill.target_type
        case 3:
            return unit_info.attribute_id == removable_skill.target_type
        case _:
            return False
