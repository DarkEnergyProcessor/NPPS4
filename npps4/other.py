import copy
import io
import json
import zipfile

import fastapi
import honkypy

from . import app
from . import config
from . import idoltype
from . import util

from typing import Annotated

SERVERINFO_TEMPLATE = {
    "name": "server_information",
    "domain": "https://prod-jp.lovelive.ge.klabgames.net",
    "maintenance_uri": "https://prod-jp.lovelive.ge.klabgames.net/resources/maintenace/maintenance.php",
    "update_uri": "https://prod-jp.lovelive.ge.klabgames.net/resources/maintenace/update.php",
    "login_news_uri": "https://prod-jp.lovelive.ge.klabgames.net/webview.php/announce/index?0=",
    "locked_user_uri": "https://prod-jp.lovelive.ge.klabgames.net/webview.php/static/index?id=13",
    "server_version": "59.4",
    "end_point": "/main.php",
    "consumer_key": "lovelive_test",
    "application_id": "626776655",
    "max_connection": 10,
    "region": "392",
    "date": "1678672484",
    "application_key": "b6e6c940a93af2357ea3e0ace0b98afc",
    "api_uri": {
        "/battle/startWait": "https://prod-2-jp.lovelive.ge.klabgames.net/main.php/battle/startWait",
        "/battle/endWait": "https://prod-2-jp.lovelive.ge.klabgames.net/main.php/battle/endWait",
        "/duty/startWait": "https://prod-2-jp.lovelive.ge.klabgames.net/main.php/duty/startWait",
        "/duty/endWait": "https://prod-2-jp.lovelive.ge.klabgames.net/main.php/duty/endWait",
        "/duty/privateStartWait": "https://prod-2-jp.lovelive.ge.klabgames.net/main.php/duty/privateStartWait",
    },
}


def make_endpoint(route_prefix: str, scheme: str, request: fastapi.Request, endpoint: str = ""):
    # Get root path
    root_path: str = request.scope.get("root_path") or "/"
    if root_path[-1] != "/":
        root_path = root_path + "/"
    if root_path[0] != "/":
        root_path = "/" + root_path

    # Get main endpoint
    if route_prefix[0] == "/":
        route_prefix = route_prefix[1:]
    if route_prefix[-1] == "/":
        route_prefix = route_prefix[:-1]

    if len(endpoint) > 0 and endpoint[0] != "/":
        endpoint = "/" + endpoint

    return f"{scheme}://{request.url.netloc}{root_path}{route_prefix}{endpoint}"


@app.core.get(
    "/server_info/{version}/{platform}.zip",
    responses={200: {"content": {"application/zip": {}}}},
    response_class=fastapi.responses.Response,
)
def server_info(
    request: fastapi.Request,
    version: Annotated[tuple[int, int], fastapi.Depends(util.parse_sif_version)],
    platform: idoltype.PlatformType,
):
    """
    Create new zip archive containing new server_info.json for this private server.
    """
    # Get root path
    root_path: str = request.scope.get("root_path") or "/"
    if root_path[-1] != "/":
        root_path = root_path + "/"

    platform_type: int = int(platform)
    if platform_type == 1:
        scheme = "https"
    elif platform_type == 2:
        scheme = "http"
    else:
        raise fastapi.HTTPException(422, detail="Unknown platform type")

    ver: str = util.sif_version_string(version)
    end_point = make_endpoint(app.main.prefix, scheme, request)
    end_point = end_point[end_point.index("/", 8) :]
    server_info = copy.deepcopy(SERVERINFO_TEMPLATE)
    server_info["domain"] = f"{scheme}://{request.url.netloc}"
    # TODO: Use request.url_for for these
    server_info["maintenance_uri"] = make_endpoint("/resources/maintenance", scheme, request, "maintenance.php")
    server_info["update_uri"] = make_endpoint("/resources/maintenance", scheme, request, "update.php")
    server_info["login_news_uri"] = make_endpoint(app.webview.prefix, scheme, request, "/announce/index")
    server_info["locked_user_uri"] = make_endpoint(app.webview.prefix, scheme, request, "/static/index?id=13")
    server_info["server_version"] = ver
    server_info["end_point"] = end_point
    server_info["consumer_key"] = config.get_consumer_key()
    server_info["application_key"] = str(config.get_application_key(), "UTF-8")
    server_info["api_uri"] = dict(
        (k, make_endpoint(app.main.prefix, scheme, request, k)) for k in server_info["api_uri"].keys()
    )

    jsondata = json.dumps(server_info).encode("UTF-8")
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w") as z:
        with z.open("config/server_info.json", "w") as f:
            dctx = honkypy.encrypt_setup_by_gametype("JP", "config/server_info.json", 3)
            f.write(dctx.emit_header())
            f.write(dctx.decrypt_block(jsondata))

    print(jsondata)
    return fastapi.responses.Response(
        result.getvalue(),
        200,
        {
            "Content-Disposition": f'attachment; filename="server_info_{ver}_{platform_type}.zip"',
        },
        "application/zip",
    )
