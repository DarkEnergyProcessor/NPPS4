import fastapi.responses

from .. import util
from ..app import app


@app.webview.get("/announce/index")
def announce_index():
    util.stub("announce", "index")
    return fastapi.responses.RedirectResponse("/main.php/api", 302)
