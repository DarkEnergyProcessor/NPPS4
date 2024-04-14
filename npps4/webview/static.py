import os.path

import fastapi
import fastapi.responses

from ..app import app

from typing import Annotated


@app.webview.get(path="/static/index")
async def static_index(id: Annotated[int, fastapi.Query()]):
    path = f"templates/static/{id}.html"
    if os.path.isfile(path):
        return fastapi.responses.FileResponse(path, media_type="text/html")

    return fastapi.responses.JSONResponse({"detail": "not found", "id": id}, 404)
