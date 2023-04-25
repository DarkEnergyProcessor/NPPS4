from . import game
from .app import app, app_main, app_webview

app.include_router(app_main)
app.include_router(app_webview)
