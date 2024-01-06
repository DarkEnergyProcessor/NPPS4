import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class MuseumContents(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `museum_contents_m` (
        `museum_contents_id` INTEGER NOT NULL,
        `museum_tab_category_id` INTEGER NOT NULL,
        `master_id` INTEGER,
        `thumbnail_asset` TEXT,
        `thumbnail_asset_en` TEXT,
        `title` TEXT NOT NULL,
        `title_en` TEXT,
        `category` TEXT NOT NULL,
        `category_en` TEXT,
        `museum_rarity` INTEGER NOT NULL,
        `attribute_id` INTEGER NOT NULL,
        `smile_buff` INTEGER NOT NULL,
        `pure_buff` INTEGER NOT NULL,
        `cool_buff` INTEGER NOT NULL,
        `sort_id` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`museum_contents_id`)
    )
    ```"""

    __tablename__ = "museum_contents_m"
    museum_contents_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    museum_tab_category_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    master_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    thumbnail_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    thumbnail_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    title: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    title_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    category: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    category_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    museum_rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    attribute_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    smile_buff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    pure_buff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cool_buff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sort_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('museum')}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
