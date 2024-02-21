import fastapi

from .. import template
from ...app import webui


@webui.app.get("/")
@webui.app.get("/index.html")
def index(request: fastapi.Request):
    return template.template.TemplateResponse("index.html", {"request": request})
