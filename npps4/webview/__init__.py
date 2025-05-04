import urllib.parse

import fastapi.responses
import fastapi.templating

from ..config import config

if not config.is_script_mode():
    from . import announce
    from . import helper
    from . import secretbox
    from . import serialcode
    from . import static
    from . import tos

from .. import errhand
from ..app import app


@app.core.get("/resources/maintenace/maintenance.php", response_class=fastapi.responses.HTMLResponse)
@app.core.get("/resources/maintenance/maintenance.php", response_class=fastapi.responses.HTMLResponse)
async def maintenance_page(request: fastapi.Request):
    if config.is_maintenance():
        with open("templates/maintenance.html", "rb") as f:
            return f.read()
    else:
        # Error?
        message = "No additional error message available"
        authorize = request.headers.get("authorize")
        if authorize is not None:
            authorize_decoded = dict(urllib.parse.parse_qsl(authorize))
            token = authorize_decoded.get("token")
            if token:
                exc = errhand.load_error(token.replace(" ", "+"))
                if exc:
                    message = "\n".join(exc)

        return app.templates.TemplateResponse(request, "error.html", {"error": message})
