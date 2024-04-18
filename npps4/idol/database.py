import sqlalchemy
import sqlalchemy.ext.asyncio

from ..db import achievement
from ..db import effort
from ..db import exchange
from ..db import game_mater
from ..db import item
from ..db import live
from ..db import main
from ..db import museum
from ..db import scenario
from ..db import subscenario
from ..db import unit


class Database:
    __slots__ = (
        "_mainsession",
        "_gmsession",
        "_itemsession",
        "_livesession",
        "_unitsession",
        "_achievementsession",
        "_effortsession",
        "_subscenariosession",
        "_museumsession",
        "_scenariosession",
        "_exchangesession",
    )

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
        self._exchangesession: sqlalchemy.ext.asyncio.AsyncSession | None = None

    @property
    def main(self):
        if self._mainsession is None:
            sessionmaker = main.get_sessionmaker()
            self._mainsession = sessionmaker()
        return self._mainsession

    @property
    def game_mater(self):
        if self._gmsession is None:
            sessionmaker = game_mater.get_sessionmaker()
            self._gmsession = sessionmaker()
        return self._gmsession

    @property
    def item(self):
        if self._itemsession is None:
            sessionmaker = item.get_sessionmaker()
            self._itemsession = sessionmaker()
        return self._itemsession

    @property
    def live(self):
        if self._livesession is None:
            sessionmaker = live.get_sessionmaker()
            self._livesession = sessionmaker()
        return self._livesession

    @property
    def unit(self):
        if self._unitsession is None:
            sessionmaker = unit.get_sessionmaker()
            self._unitsession = sessionmaker()
        return self._unitsession

    @property
    def achievement(self):
        if self._achievementsession is None:
            sessionmaker = achievement.get_sessionmaker()
            self._achievementsession = sessionmaker()
        return self._achievementsession

    @property
    def effort(self):
        if self._effortsession is None:
            sessionmaker = effort.get_sessionmaker()
            self._effortsession = sessionmaker()
        return self._effortsession

    @property
    def subscenario(self):
        if self._subscenariosession is None:
            sessionmaker = subscenario.get_sessionmaker()
            self._subscenariosession = sessionmaker()
        return self._subscenariosession

    @property
    def museum(self):
        if self._museumsession is None:
            sessionmaker = museum.get_sessionmaker()
            self._museumsession = sessionmaker()
        return self._museumsession

    @property
    def scenario(self):
        if self._scenariosession is None:
            sessionmaker = scenario.get_sessionmaker()
            self._scenariosession = sessionmaker()
        return self._scenariosession

    @property
    def exchange(self):
        if self._exchangesession is None:
            sessionmaker = exchange.get_sessionmaker()
            self._exchangesession = sessionmaker()
        return self._exchangesession

    async def cleanup(self):
        if self._mainsession is not None:
            await self._mainsession.close()
            self._mainsession = None
        if self._gmsession is not None:
            await self._gmsession.close()
            self._gmsession = None
        if self._itemsession is not None:
            await self._itemsession.close()
            self._itemsession = None
        if self._livesession is not None:
            await self._livesession.close()
            self._livesession = None
        if self._unitsession is not None:
            await self._unitsession.close()
            self._unitsession = None
        if self._achievementsession is not None:
            await self._achievementsession.close()
            self._achievementsession = None
        if self._effortsession is not None:
            await self._effortsession.close()
            self._effortsession = None
        if self._subscenariosession is not None:
            await self._subscenariosession.close()
            self._subscenariosession = None
        if self._museumsession is not None:
            await self._museumsession.close()
            self._museumsession = None
        if self._scenariosession is not None:
            await self._scenariosession.close()
            self._scenariosession = None
        if self._exchangesession is not None:
            await self._exchangesession.close()
            self._exchangesession = None

    async def commit(self):
        if self._mainsession is not None:
            await self._mainsession.commit()

    async def rollback(self):
        if self._mainsession is not None:
            await self._mainsession.rollback()
