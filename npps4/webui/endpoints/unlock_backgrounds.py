import urllib.parse

import fastapi
import sqlalchemy

from .. import template
from ... import idol
from ...app import webui
from ...db import item
from ...db import main
from ...system import background

from typing import Annotated


async def get_backgrounds(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(item.Background)
    result = await context.db.item.execute(q)
    all_backgrounds = {k.background_id: k for k in result.scalars()}

    user_backgrounds = await background.get_backgrounds(context, user)
    unlocked_ids = set(bg.id for bg in user_backgrounds)
    locked_ids = set(all_backgrounds.keys()) - unlocked_ids

    unlocked_backgrounds = [all_backgrounds[i] for i in sorted(unlocked_ids)]
    locked_backgrounds = [all_backgrounds[i] for i in sorted(locked_ids)]

    return unlocked_backgrounds, locked_backgrounds


@webui.app.get("/unlock_backgrounds.html")
async def unlock_backgrounds(
    request: fastapi.Request, uid: int, bg_id: Annotated[list[int], fastapi.Query(default_factory=list)]
):
    async with idol.BasicSchoolIdolContext(lang=idol.Language.en) as context:
        target_user = await context.db.main.get(main.User, uid)
        if target_user is None:
            raise ValueError("invalid user_id")

        # Perform unlock first.
        for background_id in bg_id:
            await background.unlock_background(context, target_user, background_id)

        # Get locked and unlocked backgrounds
        unlocked, locked = await get_backgrounds(context, target_user)

        return template.template.TemplateResponse(
            request,
            "unlock_backgrounds.html",
            {"uid": uid, "unlocked_backgrounds": unlocked, "locked_backgrounds": locked},
        )
