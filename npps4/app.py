import traceback

import fastapi
import fastapi.staticfiles
import fastapi.responses

core = fastapi.FastAPI()
main = fastapi.APIRouter(prefix="/main.php")
webview = fastapi.APIRouter(prefix="/webview.php", default_response_class=fastapi.responses.HTMLResponse)


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
