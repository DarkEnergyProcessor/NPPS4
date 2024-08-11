import dataclasses
import html
import json

import fastapi
import sqlalchemy

from .. import idol
from ..app import app
from ..db import achievement
from ..system import achievement as achievement_system

from typing import Annotated

ACHIEVEMENT_PARAMS = (
    "title",
    "title_en",
    "description",
    "description_en",
    "achievement_type",
    "reset_type",
    "reset_param",
    "params1",
    "params2",
    "params3",
    "params4",
    "params5",
    "params6",
    "params7",
    "params8",
    "params9",
    "params10",
    "params11",
    "start_date",
    "end_date",
    "default_open_flag",
    "display_flag",
    "achievement_filter_category_id",
    "achievement_filter_type_id",
    "auto_reward_flag",
    "display_start_date",
    "open_condition_string",
    "open_condition_string_en",
    "term_invisible_flag",
)


def autoescape_null(s: int | str | None, quote: bool = True):
    if s is None:
        return "<i>null</i>"
    else:
        return html.escape(str(s), quote)


def get_achievement_name(ach: achievement.Achievement):
    # ach.achievement_id, ach.title_en or ach.title or f"Achievement #{ach.achievement_id}"
    if ach.title_en and ach.title:
        return f"{ach.title_en}/{ach.title}"
    elif ach.title_en:
        return ach.title_en
    elif ach.title:
        return ach.title
    else:
        return f"Achievement #{ach.achievement_id}"


@dataclasses.dataclass
class AchievementData:
    id: int
    params: list[tuple[str, str]]
    needs: list[tuple[int, str]]
    opens: list[tuple[int, str]]


@app.webview.get("/helper/apisplitter")
async def helper_apisplitter():
    return fastapi.responses.FileResponse("util/apicall_splitter.html", media_type="text/html")


@app.webview.get("/helper/achievement")
async def helper_achievement(
    request: fastapi.Request,
    achievement_type: Annotated[int, fastapi.Query(alias="type")] = 0,
    achievement_id: Annotated[int, fastapi.Query(alias="id")] = 0,
):
    async with idol.create_basic_context(request) as context:
        if achievement_id == 0:
            q = sqlalchemy.select(achievement.Achievement)
            if achievement_type != 0:
                q = q.where(achievement.Achievement.achievement_type == achievement_type)
            result = await context.db.achievement.execute(q)
            achievements = [(ach.achievement_id, get_achievement_name(ach)) for ach in result.scalars()]
            return app.templates.TemplateResponse(
                "helper_achievement_list.html", {"request": request, "items": achievements}
            )
        else:
            ach = await context.db.achievement.get(achievement.Achievement, achievement_id)
            if ach is None:
                raise fastapi.HTTPException(404, f"achievement {achievement_id} not found")

            # Parameters
            params: list[tuple[str, str]] = [(k, autoescape_null(getattr(ach, k, None))) for k in ACHIEVEMENT_PARAMS]

            # Prerequisite
            q = sqlalchemy.select(achievement.Story).where(achievement.Story.next_achievement_id == achievement_id)
            result = await context.db.achievement.execute(q)
            needs: list[tuple[int, str]] = []
            for story in result.scalars():
                target_ach = await context.db.achievement.get(achievement.Achievement, story.achievement_id)
                if target_ach is None:
                    raise fastapi.HTTPException(404, f"achievement {story.achievement_id} not found")

                needs.append(
                    (
                        target_ach.achievement_id,
                        get_achievement_name(target_ach),
                    )
                )

            # Unlocks
            q = sqlalchemy.select(achievement.Story).where(achievement.Story.achievement_id == achievement_id)
            result = await context.db.achievement.execute(q)
            opens: list[tuple[int, str]] = []
            for story in result.scalars():
                target_ach = await context.db.achievement.get(achievement.Achievement, story.next_achievement_id)
                if target_ach is None:
                    raise fastapi.HTTPException(404, f"achievement {story.next_achievement_id} not found")

                opens.append(
                    (
                        target_ach.achievement_id,
                        get_achievement_name(target_ach),
                    )
                )

            rewards = await achievement_system.get_achievement_rewards(context, achievement_id)
            rewards_json = json.dumps([r.model_dump() for r in rewards], ensure_ascii=False, indent="\t")
            return app.templates.TemplateResponse(
                "helper_achievement_info.html",
                {
                    "request": request,
                    "achievement": AchievementData(achievement_id, params, needs, opens),
                    "reward": autoescape_null(rewards_json, False),
                },
            )


@app.webview.get("/helper/achtranslate")
async def helper_achtranslate():
    return fastapi.responses.FileResponse("util/achtranslator.html", media_type="text/html")
