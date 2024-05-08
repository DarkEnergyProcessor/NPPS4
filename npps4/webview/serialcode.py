import urllib.parse

import fastapi
import pydantic

from ..app import app

from typing import Annotated


class SerialCodeAPIRequest(pydantic.BaseModel):
    key: str


class SerialCodeAPIResponse(pydantic.BaseModel):
    ok: bool
    msg: str


@app.webview.get("/serialCode/index")
async def serial_code_index(request: fastapi.Request):
    token = ""
    authorize_header = request.headers.get("Authorize")
    if authorize_header is not None:
        qs = urllib.parse.parse_qs(authorize_header)
        if qs.get("token"):
            token = qs["token"][0]

    return app.templates.TemplateResponse(request, "serialcode.html", {"token": token})


@app.webview.post(
    "/serialCode/index", response_class=fastapi.responses.JSONResponse, response_model=SerialCodeAPIResponse
)
async def serial_code_index_post(authorize: Annotated[str, fastapi.Header()], key_request: SerialCodeAPIRequest):
    return SerialCodeAPIResponse(ok=False, msg="TODO")
