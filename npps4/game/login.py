import base64

from .. import idol
from .. import util
from ..idol import user
from ..idol import error

import fastapi
import pydantic


class LoginRequest(pydantic.BaseModel):
    login_key: str
    login_passwd: str
    devtoken: str | None = None


class LoginResponse(pydantic.BaseModel):
    authorize_token: str
    user_id: int
    review_version: str = ""
    server_timestamp: int
    idfa_enabled: bool = False
    skip_login_news: bool = False


class AuthkeyRequest(pydantic.BaseModel):
    dummy_token: str
    auth_data: str


class AuthkeyResponse(pydantic.BaseModel):
    authorize_token: str
    dummy_token: str


class StartupResponse(pydantic.BaseModel):
    user_id: str


@idol.register("/login/login", check_version=False, batchable=False)
def login_login(context: idol.SchoolIdolAuthParams, request: LoginRequest) -> LoginResponse:
    """Login user"""

    # Decrypt credentials
    key = util.xorbytes(context.token.client_key[:16], context.token.server_key[:16])
    loginkey = util.decrypt_aes(key, base64.b64decode(request.login_key))
    passwd = util.decrypt_aes(key, base64.b64decode(request.login_passwd))

    # Log
    util.log("Hello my key is", loginkey)
    util.log("And my passwd is", passwd)

    # Find user
    u = user.find_by_key(context, str(loginkey, "UTF-8"))
    if u is None or (not u.check_passwd(str(passwd, "UTF-8"))):
        # This will send "Your data has been transfered succesfully" message to the SIF client.
        raise error.IdolError(error_code=407, status_code=600, detail="Login not found")

    # Login
    token = util.encapsulate_token(context.token.server_key, context.token.client_key, u.id)
    return LoginResponse(authorize_token=token, user_id=u.id, server_timestamp=util.time())


@idol.register("/login/authkey", check_version=False, batchable=False, xmc_verify=idol.XMCVerifyMode.NONE)
def login_authkey(context: idol.SchoolIdolParams, request: AuthkeyRequest) -> AuthkeyResponse:
    """Generate authentication key."""

    # Decrypt client key
    client_key = util.decrypt_rsa(base64.b64decode(request.dummy_token))
    if not client_key:
        raise fastapi.HTTPException(400, "Bad client key")
    auth_data = util.decrypt_aes(client_key[:16], base64.b64decode(request.auth_data))

    # Create new token
    server_key = util.randbytes(32)
    token = util.encapsulate_token(server_key, client_key, 0)

    # Log
    util.log("My client key is", client_key)
    util.log("And my auth_data is", auth_data)

    # Return response
    return AuthkeyResponse(
        authorize_token=token,
        dummy_token=str(base64.b64encode(server_key), "UTF-8"),
    )


@idol.register("/login/startUp", check_version=False, batchable=False)
def login_startup(context: idol.SchoolIdolAuthParams, request: LoginRequest) -> StartupResponse:
    """Register new account."""
    key = util.xorbytes(context.token.client_key[:16], context.token.server_key[:16])
    loginkey = util.decrypt_aes(key, base64.b64decode(request.login_key))
    passwd = util.decrypt_aes(key, base64.b64decode(request.login_passwd))

    # Log
    util.log("Hello my key is", loginkey)
    util.log("And my passwd is", passwd)

    # Create user
    try:
        u = user.create(context, str(loginkey, "UTF-8"), str(passwd, "UTF-8"))
    except ValueError:
        raise fastapi.HTTPException(400, "Bad login key or password or client key")

    return StartupResponse(user_id=str(u.id))
