# Must be loaded first!
from . import setup

from . import game
from . import webview
from . import other
from . import app

app.core.include_router(app.main)
app.core.include_router(app.webview)

uvicorn_main = app.core
