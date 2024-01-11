import fastapi.responses

from .. import app
from .. import util


@app.webview.get("/announce/index")
def announce_index():
    util.stub("announce", "index", context.raw_request_data)
    return fastapi.responses.RedirectResponse("/main.php/api", 302)
