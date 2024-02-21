import os.path

import fastapi.staticfiles

from . import endpoints
from ..app import webui

current_dir = os.path.dirname(__file__)

webui.app.mount(
    "/static", fastapi.staticfiles.StaticFiles(directory=os.path.join(current_dir, "static")), "static_file"
)
