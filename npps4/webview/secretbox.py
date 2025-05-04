import base64
import dataclasses
import html
import json

import fastapi
import pydantic
import sqlalchemy

from .. import idol
from .. import util
from ..app import app
from ..config import config
from ..db import achievement
from ..system import achievement as achievement_system
from ..system import handover
from ..system import lila
from ..system import secretbox

from typing import Annotated


@app.webview.get("/secretbox/detail")
async def secretbox_detail(request: fastapi.Request, secretbox_id: Annotated[int, fastapi.Query()]):
    async with idol.create_basic_context(request) as context:
        secretbox_data = secretbox.get_secretbox_data(secretbox_id)
        rate_count = sum(secretbox_data.rarity_rates)
        rate_data = [
            (v[0], v[1], v[1] / rate_count) for v in zip(secretbox_data.rarity_names, secretbox_data.rarity_rates)
        ]
        return app.templates.TemplateResponse(
            request,
            "secretbox_detail.html",
            {
                "secretbox_id": secretbox_id,
                "secretbox_name": context.get_text(secretbox_data.name, secretbox_data.name_en),
                "rates": rate_data,
            },
        )
