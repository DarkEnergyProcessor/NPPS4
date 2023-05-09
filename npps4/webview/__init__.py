import fastapi.responses

from .. import app
from . import tos


@app.core.get("/resources/maintenace/maintenance.php", response_class=fastapi.responses.HTMLResponse)
@app.core.get("/resources/maintenance/maintenance.php", response_class=fastapi.responses.HTMLResponse)
def maintenance_page():
    with open("templates/maintenance.html", "rb") as f:
        return f.read()
