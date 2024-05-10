import json
import npps4.script_dummy  # Must be first

import sqlalchemy

import npps4.const
import npps4.db.main
import npps4.idol
import npps4.system.unit


async def run_script(args: list[str]):
    unit_cache_attribute: dict[int, tuple[int, int]] = {}

    async with npps4.idol.BasicSchoolIdolContext(npps4.idol.Language.en) as context:
        q = sqlalchemy.select(npps4.db.main.Incentive).where(
            npps4.db.main.Incentive.add_type == int(npps4.const.ADD_TYPE.UNIT)
        )
        with await context.db.main.execute(q) as result:
            for row in result.scalars():
                hitit = False
                if row.item_id not in unit_cache_attribute:
                    unit_info = await npps4.system.unit.get_unit_info(context, row.item_id)
                    if unit_info is not None:
                        unit_cache_attribute[row.item_id] = (unit_info.rarity, unit_info.attribute_id)

                row.unit_rarity, row.unit_attribute = unit_cache_attribute[row.item_id]
                if row.extra_data is not None:
                    extra_data = json.loads(row.extra_data)
                    if "is_support_member" in extra_data and (not extra_data["is_support_member"]):
                        extra_data["attribute"] = row.unit_attribute
                        row.extra_data = json.dumps(extra_data)

                if hitit:
                    await context.db.main.flush()


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
