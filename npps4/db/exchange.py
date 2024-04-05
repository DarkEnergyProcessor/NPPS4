import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class ExchangeNoPointUnit(common.GameDBBase):
    """```sql
    CREATE TABLE `exchange_nopoint_unit_m` (
        `unit_id` INTEGER NOT NULL,
        PRIMARY KEY (`unit_id`)
    )
    ```"""

    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)


class ExchangePoint(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `exchange_point_m` (
        `exchange_point_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `small_asset` TEXT NOT NULL,
        `small_asset_en` TEXT,
        `icon_asset` TEXT NOT NULL,
        `icon_asset_en` TEXT,
        `middle_asset` TEXT,
        `middle_asset_en` TEXT,
        `r_rank_up_point` INTEGER,
        `sr_rank_up_point` INTEGER,
        `ssr_rank_up_point` INTEGER,
        `ur_rank_up_point` INTEGER,
        `sort` INTEGER NOT NULL,
        `start_date` TEXT,
        `end_date` TEXT,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`exchange_point_id`)
    )
    ```"""

    exchange_point_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    small_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    small_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    r_rank_up_point: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    sr_rank_up_point: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    ssr_rank_up_point: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    ur_rank_up_point: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    start_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    end_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('exchange')}?mode=ro&uri=true",
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
