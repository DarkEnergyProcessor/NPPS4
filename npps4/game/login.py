import base64
import random

from .. import idol

import pydantic


SYSRAND = random.SystemRandom()


class LoginRequest(pydantic.BaseModel):
    login_key: str
    login_passwd: str


class LoginResponse(pydantic.BaseModel):
    user_id: int


class AuthkeyResponse(pydantic.BaseModel):
    authorize_token: str
    dummy_token: str


@idol.register("/login/login")
def login(context: idol.SchoolIdolAuthParams, request: LoginRequest) -> LoginResponse:
    """Login user"""
    # TODO: login
    print(context)
    print(context.client_version)
    print(context.lang)
    print(context.token)
    print(request.login_key, request.login_passwd)
    return LoginResponse(user_id=1)


@idol.register("/login/authkey")
def authkey(context: idol.SchoolIdolParams) -> AuthkeyResponse:
    """Generate authentication key."""
    global SYSRAND
    return AuthkeyResponse(
        authorize_token=base64.b64encode(SYSRAND.randbytes(16)).decode("UTF-8"),
        dummy_token=base64.b64encode(SYSRAND.randbytes(16)).decode("UTF-8"),
    )


print("registered")
