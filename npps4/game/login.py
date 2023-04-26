import base64
import random

from .. import idol
from .. import util

import pydantic


class LoginRequest(pydantic.BaseModel):
    login_key: str
    login_passwd: str


class LoginResponse(pydantic.BaseModel):
    user_id: int


class AuthkeyRequest(pydantic.BaseModel):
    pass


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
    print(context.token)
    print(request.login_key, request.login_passwd)
    return LoginResponse(user_id=1)


@idol.register("/login/authkey", check_version=False, batchable=False)
def authkey(context: idol.SchoolIdolParams) -> AuthkeyResponse:
    """Generate authentication key."""
    global SYSRAND
    return AuthkeyResponse(
        authorize_token=base64.b64encode(util.randbytes(16)).decode("UTF-8"),
        dummy_token=base64.b64encode(util.randbytes(16)).decode("UTF-8"),
    )


print("registered")
