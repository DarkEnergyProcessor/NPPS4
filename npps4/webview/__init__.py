import traceback
import urllib.parse

import fastapi.responses
import fastapi.templating

from .. import app
from .. import config
from .. import errhand
from . import tos


@app.core.get("/resources/maintenace/maintenance.php", response_class=fastapi.responses.HTMLResponse)
@app.core.get("/resources/maintenance/maintenance.php", response_class=fastapi.responses.HTMLResponse)
def maintenance_page(request: fastapi.Request):
    if config.is_maintenance():
        with open("templates/maintenance.html", "rb") as f:
            return f.read()
    else:
        # Error?
        message = "No additional error message available"
        authorize = request.headers.get("Authorize")
        if authorize:
            authorize_decoded = dict(urllib.parse.parse_qsl(authorize))
            token = authorize_decoded.get("token")
            if token:
                exc = errhand.load_error(token)
                if exc:
                    message = "\n".join(exc)

        return app.templates.TemplateResponse("error.html", {"request": request, "error": message})
