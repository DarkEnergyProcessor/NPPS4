import copy
import datetime
import hashlib
import io
import json
import os
import zipfile

import fastapi
import honkypy
import pydantic

from . import util
from .app import app
from .config import config

from typing import Annotated, Literal

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


def get_root_path(request: fastapi.Request):
    root_path: str = request.scope.get("root_path", "")
    if len(root_path) > 0:
        if root_path[0] != "/":
            root_path = "/" + root_path
        if root_path[-1] == "/":
            root_path = root_path[:-1]
    return root_path


def make_endpoint(route_prefix: str, scheme: str, request: fastapi.Request, endpoint: str = ""):
    # Get root path
    root_path = get_root_path(request)

    # Get main endpoint
    if len(route_prefix) > 0:
        if route_prefix[0] != "/":
            route_prefix = "/" + route_prefix[1:]
        if route_prefix[-1] == "/":
            route_prefix = route_prefix[:-1]

    if len(endpoint) > 0 and endpoint[0] != "/":
        endpoint = "/" + endpoint

    return f"{scheme}://{request.url.netloc}{root_path}{route_prefix}{endpoint}"


def get_hash_key(request: fastapi.Request, version: tuple[int, int]):
    root_path = get_root_path(request)
    return (
        root_path
        + request.url.scheme
        + request.url.netloc
        + app.main.prefix
        + app.webview.prefix
        + config.get_consumer_key()
        + str(config.get_application_key(), "UTF-8")
        + util.sif_version_string(version)
    )


def build_server_info(request: fastapi.Request, version: tuple[int, int]):
    # Get root path
    root_path = get_root_path(request)
    scheme = request.url.scheme
    ver: str = util.sif_version_string(version)
    server_info = copy.deepcopy(SERVERINFO_TEMPLATE)
    server_info["domain"] = f"{scheme}://{request.url.netloc}{root_path}"
    server_info["maintenance_uri"] = make_endpoint("", scheme, request, "/resources/maintenance/maintenance.php")
    server_info["update_uri"] = make_endpoint("", scheme, request, "/resources/maintenance/update.php")
    server_info["login_news_uri"] = make_endpoint(app.webview.prefix, scheme, request, "/announce/index")
    server_info["locked_user_uri"] = make_endpoint(app.webview.prefix, scheme, request, "/static/index?id=13")
    server_info["server_version"] = ver
    server_info["end_point"] = app.main.prefix
    server_info["consumer_key"] = config.get_consumer_key()
    server_info["application_key"] = str(config.get_application_key(), "UTF-8")
    server_info["api_uri"] = dict(
        (k, make_endpoint(app.main.prefix, scheme, request, k)) for k in server_info["api_uri"].keys()
    )
    return server_info


def generate_server_info(request: fastapi.Request, version: tuple[int, int]):
    datadir = config.get_data_directory() + "/server_info/"
    key = hashlib.sha1(get_hash_key(request, version).encode("UTF-8"), usedforsecurity=False).hexdigest()

    os.makedirs(datadir, exist_ok=True)
    dest = datadir + key + ".zip"
    if os.path.isfile(dest):
        stat = os.stat(dest)
        size = stat.st_size
    else:
        server_info = build_server_info(request, version)
        jsondata = json.dumps(server_info).encode("UTF-8")

        with io.BytesIO() as result:
            with zipfile.ZipFile(result, "w") as z:
                now = datetime.datetime.now(datetime.UTC)
                info = zipfile.ZipInfo(
                    "config/server_info.json", (now.year, now.month, now.day, now.hour, now.minute, now.second)
                )
                with z.open(info, "w") as f:
                    dctx = honkypy.encrypt_setup_by_gametype("JP", "config/server_info.json", 3)
                    f.write(dctx.emit_header())
                    f.write(dctx.decrypt_block(jsondata))

            bytesresult = result.getvalue()
        with open(dest, "wb") as f:
            f.write(bytesresult)

        size = len(bytesresult)

    return key, size


@app.core.get("/server_info.json")
async def server_info_json(
    request: fastapi.Request,
    version: Annotated[str, fastapi.Query(alias="v")] = "59.0",
):
    server_info = build_server_info(request, (59, 0))
    server_info["server_version"] = version
    return fastapi.responses.JSONResponse(server_info)
