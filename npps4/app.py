import fastapi
import fastapi.responses

app = fastapi.FastAPI()
app_main = fastapi.APIRouter(prefix="/main.php")
app_webview = fastapi.APIRouter(prefix="/webview.php", default_response_class=fastapi.responses.HTMLResponse)
