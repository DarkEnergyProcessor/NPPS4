import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class Scenario(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `scenario_m` (
        `scenario_id` INTEGER NOT NULL,
        `scenario_chapter_id` INTEGER NOT NULL,
        `title` TEXT NOT NULL,
        `title_en` TEXT,
        `title_call_asset` TEXT,
        `title_call_asset_en` TEXT,
        `title_font` INTEGER,
        `outline` TEXT,
        `outline_en` TEXT,
        `asset_bgm_id` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`scenario_id`)
    )
    ```"""

    __tablename__ = "scenario_m"
    scenario_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    scenario_chapter_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    title: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    title_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    title_call_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    title_call_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    title_font: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    outline: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    outline_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    asset_bgm_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class Chapter(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `scenario_chapter_m` (
        `scenario_chapter_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `outline` TEXT,
        `outline_en` TEXT,
        `image_asset` TEXT,
        `image_asset_en` TEXT,
        `type` INTEGER NOT NULL,
        `sort` INTEGER,
        `member_category` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`scenario_chapter_id`)
    )
    ```"""

    __tablename__ = "scenario_chapter_m"
    scenario_chapter_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    outline: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    outline_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    member_category: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('scenario')}?mode=ro&uri=true",
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
