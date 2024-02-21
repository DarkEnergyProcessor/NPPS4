import fastapi
import fastapi.responses

from .. import version

app = fastapi.FastAPI(
    title="NPPS4 WebUI",
    version="%d.%d.%d" % version.NPPS4_VERSION,
    default_response_class=fastapi.responses.HTMLResponse,
)
