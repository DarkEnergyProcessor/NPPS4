from . import game
from .app import app, main as app_main, webview as app_webview

app.include_router(app_main)
app.include_router(app_webview)
