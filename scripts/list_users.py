#!/usr/bin/env python -m npps4.script
import sqlalchemy

import npps4.db.main
import npps4.idol


async def run_script(args: list[str]):
    context = npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en)
    async with context:
        q = sqlalchemy.select(npps4.db.main.User)
        result = await context.db.main.execute(q)
        for user in result.scalars():
            print(f"{user.id}|{user.name}|{user.invite_code}")
