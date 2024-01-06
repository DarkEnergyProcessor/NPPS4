import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class SubScenario(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `subscenario_m` (
        `subscenario_id` INTEGER NOT NULL,
        `unit_id` INTEGER NOT NULL,
        `title` TEXT NOT NULL,
        `title_en` TEXT,
        `asset_bgm_id` INTEGER NOT NULL,
        `scenario_char_asset_id` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`subscenario_id`)
    )
    ```"""

    __tablename__ = "subscenario_m"
    subscenario_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    title: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    title_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    asset_bgm_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    scenario_char_asset_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('subscenario')}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
