import os

import fastapi

from .app import app
from .config import config


@app.core.get(
    "/server_info/{filehash}",
    responses={200: {"content": {"application/zip": {}}}},
    response_class=fastapi.responses.Response,
)
async def server_info(filehash: str):
    """
    Get zip archive containing new server_info.json for this private server.
    """
    sanitized_hash = "".join(filter(str.isalnum, filehash))
    zipfile = config.get_data_directory() + "/server_info/" + sanitized_hash + ".zip"

    if os.path.isfile(zipfile):
        with open(zipfile, "rb") as f:
            return fastapi.responses.Response(
                f.read(),
                200,
                {
                    "Content-Disposition": f'attachment; filename="{sanitized_hash}.zip"',
                },
                "application/zip",
            )
    else:
        raise fastapi.exceptions.HTTPException(404, "Not found")


@app.core.get("/capture/{capture}")
async def set_capture(capture: bool | int):
    if isinstance(capture, int):
        capture = capture > 0

    oldval = config.log_request_response(capture)
    return {"old": oldval, "new": capture}


@app.core.get("/capture")
async def get_capture():
    return {"old": config.log_request_response()}
