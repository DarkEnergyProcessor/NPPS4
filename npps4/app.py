import fastapi
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
