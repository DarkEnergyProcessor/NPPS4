import json

import sqlalchemy

import npps4.script_dummy  # isort:skip
import npps4.const
import npps4.db.main
import npps4.idol
import npps4.system.unit

from typing import Any

import npps4.system.unit_model

revision = "3_update_incentive_unit_extra_data"
prev_revision = "2_populate_normal_live_unlock"


def intdefval[T](x: Any, defval: T, /) -> int | T:
    if x is None:
        return defval

    try:
        return int(x)
    except ValueError:
        return defval


async def main(context: npps4.idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(npps4.db.main.Incentive).where(
        npps4.db.main.Incentive.add_type == int(npps4.const.ADD_TYPE.UNIT)
    )
    with await context.db.main.execute(q) as result:
        for row in result.scalars():
            if row.extra_data is not None:
                unit_info = await npps4.system.unit.get_unit_info(context, row.item_id)
                if unit_info is not None:
                    extra_data: dict[str, Any] = json.loads(row.extra_data)
                    exp = intdefval(extra_data.get("exp"), 0)
                    skill_exp = intdefval(extra_data.get("unit_skill_exp"), 0)
                    rank = intdefval(extra_data.get("rank"), 1)
                    love = intdefval(extra_data.get("love"), 0)
                    unit_removable_skill_capacity = intdefval(
                        extra_data.get("unit_removable_skill_capacity"), unit_info.default_removable_skill_capacity
                    )
                    display_rank = intdefval(extra_data.get("display_rank"), 1)
                    is_signed = bool(extra_data.get("is_signed", False))
                    removable_skill_ids = tuple(
                        filter(None, map(lambda k: intdefval(k, 0), extra_data.get("removable_skill_ids", tuple())))
                    )

                    if rank <= unit_info.rank_min:
                        rank = 1  # to force defaults
                    if display_rank <= unit_info.rank_min:
                        display_rank = 1  # to force defaults
                    if unit_removable_skill_capacity == unit_info.default_removable_skill_capacity:
                        unit_removable_skill_capacity = None  # to force defaults

                    unit_extra_data = npps4.system.unit_model.UnitExtraData(
                        exp=exp,
                        rank=rank,
                        love=love,
                        skill_exp=skill_exp,
                        unit_removable_skill_capacity=unit_removable_skill_capacity,
                        display_rank=display_rank,
                        is_signed=is_signed,
                        removable_skill_ids=removable_skill_ids,
                    )
                    if unit_extra_data == npps4.system.unit_model.UnitExtraData.EMPTY:
                        row.extra_data = None
                    else:
                        row.extra_data = json.dumps(unit_extra_data.model_dump(mode="json"), separators=(",", ":"))
