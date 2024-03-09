import fastapi

from .. import template
from ...app import webui

import sqlalchemy

import npps4.db.main
import npps4.db.item
import npps4.idol
import npps4.scriptutils.user
from npps4.db.item import Background

import npps4.idol
import npps4.idol.system.background
import npps4.db.main
import npps4.db.item
import npps4.scriptutils.user

import urllib.parse

async def get_backgrounds(uid: str, to_unlock: list[str]) -> tuple[list[Background],list[Background]]:
    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await context.db.main.get(npps4.db.main.User, uid)

        if target_user is None:
            return [], []

        q = sqlalchemy.select(npps4.db.item.Background)
        result = await context.db.item.execute(q)

        user_backgrounds = await npps4.idol.system.background.get_backgrounds(context, target_user) 
        unlocked_ids = [bg.id for bg in user_backgrounds]

        for bg_id in map(int,to_unlock):
            if bg_id not in unlocked_ids:
                await npps4.idol.system.background.unlock_background(context, target_user, bg_id)
                unlocked_ids.append(bg_id)
        
        all_backgrounds = result.scalars().all()
        unlocked_backgrounds: list[Background] = [bg for bg in all_backgrounds if bg.background_id in unlocked_ids]
        locked_backgrounds: list[Background]   = [bg for bg in all_backgrounds if bg.background_id not in unlocked_ids]

    return unlocked_backgrounds, locked_backgrounds


@webui.app.get("/unlock_backgrounds.html")
async def unlock_backgrounds(request: fastapi.Request):
    uid: str                 = request.query_params['uid']
    gs: dict[str, list[str]] = parse_qs(str(request.query_params))
    to_unlock: list[str]     = 'bg_id' in gs and gs['bg_id'] or []
    unlocked, locked         = await get_backgrounds(uid, to_unlock)
    
    return template.template.TemplateResponse("unlock_backgrounds.html",
                                              {"uid": uid,
                                               "request": request,
                                               "unlocked_backgrounds": unlocked,
                                               "locked_backgrounds": locked})


