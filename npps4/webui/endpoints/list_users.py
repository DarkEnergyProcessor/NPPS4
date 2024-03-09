import fastapi
import asyncio

from .. import template
from ...app import webui

import sqlalchemy

from ... import idol
from ...db import main


@webui.app.get("/list_users.html")
async def list_users(request: fastapi.Request):
    async with idol.BasicSchoolIdolContext(lang=idol.Language.en):
        q = sqlalchemy.select(main.User)
        result = await context.db.main.execute(q)
        users = [ {'name':user.name, 'id':user.id} for user in result.scalars()]

    return template.template.TemplateResponse("list_users.html", {"request": request, "users": users})

    return template.template.TemplateResponse("list_users.html", {"request": request, "users": users})
