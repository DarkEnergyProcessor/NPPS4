import fastapi

from . import error
from .core import BasicSchoolIdolContext, SchoolIdolParams, SchoolIdolAuthParams, SchoolIdolUserParams, register
from ..idoltype import Language, PlatformType, XMCVerifyMode

from typing import Annotated


def create_basic_context(request: fastapi.Request):
    try:
        lang = Language(request.headers.get("LANG", "en"))
    except ValueError:
        lang = Language.en
    return BasicSchoolIdolContext(lang)
