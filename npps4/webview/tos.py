from ..app import app


@app.webview.get("/tos/read")
def tos_read(tos_id: int = 1):
    # TODO: TOS ID > 1?
    with open("templates/tos_read.html", "rb") as f:
        return f.read()
