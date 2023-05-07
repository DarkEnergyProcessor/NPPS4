import traceback

import fastapi
import fastapi.staticfiles
import fastapi.responses

NPPS4_VERSION = (0, 0, 1)

core = fastapi.FastAPI(title="NPPS4", version="%d.%d.%d" % NPPS4_VERSION, docs_url="/")
main = fastapi.APIRouter(prefix="/main.php")
webview = fastapi.APIRouter(prefix="/webview.php", default_response_class=fastapi.responses.HTMLResponse)


@core.get("/docs", include_in_schema=False)
def docs_handler():
    return fastapi.responses.RedirectResponse("/", 302)


@core.exception_handler(404)
def handler_404(request: fastapi.Request, exc: Exception):
    return fastapi.responses.JSONResponse(
        status_code=404,
        content={"detail": f"Endpoint not found: {request.url}"},
    )


@core.exception_handler(500)
def handler_500(request: fastapi.Request, exc: Exception):
    return fastapi.responses.JSONResponse(
        status_code=500,
        content={"exception": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exception(exc)},
    )


core.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), "static_file")
