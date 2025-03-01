import npps4.script_dummy  # isort:skip

import sqlalchemy

import npps4.idol
import npps4.db.main
import npps4.db.achievement
import npps4.system.achievement


async def run_script(args: list[str]):
    async with npps4.idol.BasicSchoolIdolContext() as context:
        q = sqlalchemy.select(npps4.db.achievement.Achievement.reset_type).group_by(
            npps4.db.achievement.Achievement.reset_type
        )
        reset_types = list((await context.db.achievement.execute(q)).scalars())

        for reset_type in reset_types:
            q = sqlalchemy.select(npps4.db.achievement.Achievement.achievement_id).where(
                npps4.db.achievement.Achievement.reset_type == reset_type
            )
            ach_ids = list((await context.db.achievement.execute(q)).scalars())
            q = (
                sqlalchemy.update(npps4.db.main.Achievement)
                .values(reset_type=reset_type)
                .where(npps4.db.main.Achievement.achievement_id.in_(ach_ids))
            )
            await context.db.main.execute(q)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
