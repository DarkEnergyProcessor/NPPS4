import npps4.script_dummy  # Must be first

import sqlalchemy

import npps4.idol
import npps4.db.main
import npps4.system.user
import npps4.scriptutils.user


async def run_script(arg: list[str]):
    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        q = sqlalchemy.select(npps4.db.main.User.id).where(
            npps4.db.main.User.key == None, npps4.db.main.User.passwd == None, npps4.db.main.User.transfer_sha1 == None
        )
        user_ids = list((await context.db.main.execute(q)).scalars())
        print("Deleting users:", ", ".join(map(str, user_ids)))
        for user_id in user_ids:
            await npps4.system.user.delete_user(context, user_id)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
