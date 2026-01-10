# Must be loaded first!
import json
import logging

import fastapi

from .. import game
from .. import webview
from .. import other
from .. import util
from ..app import app

from typing import Annotated


# 404 handler
@app.main.post("/{module}/{action}")
async def not_found_handler(module: str, action: str, request_data: Annotated[bytes, fastapi.Form()]) -> dict:
    util.log("Endpoint not found", f"{module}/{action}", json.loads(request_data), severity=logging.ERROR)
    raise fastapi.HTTPException(404)


app.core.include_router(app.main)
app.core.include_router(app.webview)
main = app.core
