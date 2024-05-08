from .. import idol
from ..db import main

from typing import Awaitable, Callable

functions: dict[str, Callable[[idol.BasicSchoolIdolContext, main.User], Awaitable[str | None]]] = {}
