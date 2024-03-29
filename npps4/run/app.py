# This license applies to all source files in this directory and subdirectories.
#
# Copyright (c) 2024 Dark Energy Processor
#
# This software is provided 'as-is', without any express or implied warranty. In
# no event will the authors be held liable for any damages arising from the use of
# this software.
#
# Permission is granted to anyone to use this software for any purpose, including
# commercial applications, and to alter it and redistribute it freely, subject to
# the following restrictions:
#
# 1.  The origin of this software must not be misrepresented; you must not claim
#     that you wrote the original software. If you use this software in a product,
#     an acknowledgment in the product documentation would be appreciated but is
#     not required.
# 2.  Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
# 3.  This notice may not be removed or altered from any source distribution.

# Must be loaded first!
import json
import logging

import fastapi

from .. import setup  # Needs to be first!
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
