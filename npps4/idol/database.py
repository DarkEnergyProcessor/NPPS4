import sqlalchemy
import sqlalchemy.ext.asyncio

from ..db import achievement
from ..db import effort
from ..db import game_mater
from ..db import item
from ..db import live
from ..db import main
from ..db import museum
from ..db import scenario
from ..db import subscenario
from ..db import unit


class Database:
    def __init__(self) -> None:
        self._mainsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._gmsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._itemsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._livesession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._unitsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._achievementsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._effortsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._subscenariosession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._museumsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._scenariosession: sqlalchemy.ext.asyncio.AsyncSession | None = None

    @property
    def main(self):
        if self._mainsession is None:
            sessionmaker = main.get_sessionmaker()
            self._mainsession = sessionmaker()
        return self._mainsession

    @property
    def game_mater(self):
        if self._gmsession is None:
            self._gmsession = game_mater.get_session()
        return self._gmsession

    @property
    def item(self):
        if self._itemsession is None:
            self._itemsession = item.get_session()
        return self._itemsession

    @property
    def live(self):
        if self._livesession is None:
            self._livesession = live.get_session()
        return self._livesession

    @property
    def unit(self):
        if self._unitsession is None:
            self._unitsession = unit.get_session()
        return self._unitsession

    @property
    def achievement(self):
        if self._achievementsession is None:
            self._achievementsession = achievement.get_session()
        return self._achievementsession

    @property
    def effort(self):
        if self._effortsession is None:
            self._effortsession = effort.get_session()
        return self._effortsession

    @property
    def subscenario(self):
        if self._subscenariosession is None:
            self._subscenariosession = subscenario.get_session()
        return self._subscenariosession

    @property
    def museum(self):
        if self._museumsession is None:
            self._museumsession = museum.get_session()
        return self._museumsession

    @property
    def scenario(self):
        if self._scenariosession is None:
            self._scenariosession = scenario.get_session()
        return self._scenariosession

    async def cleanup(self):
        if self._mainsession is not None:
            await self._mainsession.close()
            self._mainsession = None

    async def commit(self):
        if self._mainsession is not None:
            await self._mainsession.commit()

    async def rollback(self):
        if self._mainsession is not None:
            await self._mainsession.rollback()
