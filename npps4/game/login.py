import base64

from .. import idol
from .. import util

import fastapi
import pydantic


class LoginRequest(pydantic.BaseModel):
    login_key: str
    login_passwd: str
    devtoken: str


class LoginResponse(pydantic.BaseModel):
    user_id: int


class AuthkeyRequest(pydantic.BaseModel):
    dummy_token: str
    auth_data: str


class AuthkeyResponse(pydantic.BaseModel):
    authorize_token: str
    dummy_token: str


@idol.register("/login/login", check_version=False, batchable=False)
def login(context: idol.SchoolIdolAuthParams, request: LoginRequest) -> LoginResponse:
    """Login user"""
    # TODO: login
    print(context)
    print(context.client_version)
    print(context.lang)
    print(context.token_text)
    print(request.login_key, request.login_passwd)
    return LoginResponse(user_id=1)


@idol.register("/login/authkey", check_version=False, batchable=False, xmc_verify=idol.XMCVerifyMode.NONE)
def authkey(context: idol.SchoolIdolParams, request: AuthkeyRequest) -> AuthkeyResponse:
    """Generate authentication key."""
    client_key = util.decrypt_rsa(base64.b64decode(request.dummy_token))
    if client_key is None:
        raise fastapi.HTTPException(400, "Bad client key")
    auth_data = util.decrypt_aes(client_key[:16], base64.b64decode(request.auth_data))
    server_key = util.randbytes(32)
    token = util.encapsulate_token(server_key, client_key, 0)
    print("My client key is", client_key)
    print("And my auth_data is", auth_data)
    return AuthkeyResponse(
        authorize_token=token,
        dummy_token=str(base64.b64encode(server_key), "UTF-8"),
    )


print("registered")
