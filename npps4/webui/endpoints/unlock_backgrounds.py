import urllib.parse

import fastapi
import sqlalchemy

from .. import template
from ... import idol
from ...app import webui
from ...db import item
from ...db import main
from ...idol.system import background


async def get_backgrounds(uid: str, to_unlock: list[str]) -> tuple[list[item.Background], list[item.Background]]:
    async with idol.BasicSchoolIdolContext(lang=idol.Language.en) as context:
        target_user = await context.db.main.get(main.User, uid)

        if target_user is None:
            return [], []

        q = sqlalchemy.select(item.Background)
        result = await context.db.item.execute(q)

        user_backgrounds = await background.get_backgrounds(context, target_user)
        unlocked_ids = [bg.id for bg in user_backgrounds]

        for bg_id in map(int, to_unlock):
            if bg_id not in unlocked_ids:
                await background.unlock_background(context, target_user, bg_id)
                unlocked_ids.append(bg_id)

        all_backgrounds = result.scalars().all()
        unlocked_backgrounds: list[item.Background] = [
            bg for bg in all_backgrounds if bg.background_id in unlocked_ids
        ]
        locked_backgrounds: list[item.Background] = [
            bg for bg in all_backgrounds if bg.background_id not in unlocked_ids
        ]

    return unlocked_backgrounds, locked_backgrounds


@webui.app.get("/unlock_backgrounds.html")
async def unlock_backgrounds(request: fastapi.Request):
    uid: str = request.query_params["uid"]
    gs: dict[str, list[str]] = urllib.parse.parse_qs(str(request.query_params))
    to_unlock: list[str] = "bg_id" in gs and gs["bg_id"] or []
    unlocked, locked = await get_backgrounds(uid, to_unlock)

    return template.template.TemplateResponse(
        "unlock_backgrounds.html",
        {"uid": uid, "request": request, "unlocked_backgrounds": unlocked, "locked_backgrounds": locked},
    )
