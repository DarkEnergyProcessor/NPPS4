import traceback
import urllib.parse

import fastapi
import fastapi.encoders
import fastapi.exceptions
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating

from .. import errhand
from .. import util
from .. import version

core = fastapi.FastAPI(title="NPPS4", version="%d.%d.%d" % version.NPPS4_VERSION, docs_url="/main.php/api")
main = fastapi.APIRouter(prefix="/main.php")
webview = fastapi.APIRouter(prefix="/webview.php", default_response_class=fastapi.responses.HTMLResponse)
templates = fastapi.templating.Jinja2Templates("templates")


# https://github.com/encode/uvicorn/discussions/1386
@core.middleware("http")
async def root_path_from_x_forwarded_prefix(request: fastapi.Request, call_next):
    prefix = request.headers.get("X-Forwarded-Prefix")
    if prefix:
        request.scope["root_path"] = prefix
    return await call_next(request)


@core.get("/")
def todo_main_page():
    return fastapi.responses.RedirectResponse("/main.php/api")


def get_token_manual(request: fastapi.Request):
    str(request.headers)  # Don't remove this line!
    authorize = request.headers.get("Authorize")
    if authorize:
        authorize_decoded = dict(urllib.parse.parse_qsl(authorize))
        return authorize_decoded.get("token")
    return None


@core.get("/docs", include_in_schema=False)
async def docs_handler():
    return fastapi.responses.RedirectResponse("/", 302)


@core.exception_handler(404)
async def handler_404(request: fastapi.Request, exc: Exception):
    dest = str(request.url)
    token = get_token_manual(request)
    if token and dest.find("main.php") != -1:
        errhand.save_error(token, ["Endpoint not found", dest])

    return fastapi.responses.JSONResponse(
        status_code=404,
        content={"detail": f"Endpoint not found: {request.url}"},
        headers={"Maintenance": "1"},
    )


@core.exception_handler(500)
async def handler_500(request: fastapi.Request, exc: Exception):
    dest = str(request.url)
    token = get_token_manual(request)
    tb = traceback.format_exception(exc)
    if token and dest.find("main.php") != -1:
        errhand.save_error(token, tb)

    return fastapi.responses.JSONResponse(
        status_code=500,
        content={"exception": type(exc).__name__, "message": str(exc), "traceback": tb},
        headers={"Maintenance": "1"},
    )


@core.exception_handler(fastapi.exceptions.RequestValidationError)
async def request_validation_exception_handler(
    request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError
) -> fastapi.responses.JSONResponse:
    jsonable = fastapi.encoders.jsonable_encoder(exc.errors())
    util.log("Error handling request", jsonable, severity=util.logging.ERROR, e=exc)
    return fastapi.responses.JSONResponse(
        status_code=422,
        content={"detail": jsonable},
    )


core.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), "static_file")
