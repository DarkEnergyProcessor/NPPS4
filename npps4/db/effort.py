import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from .. import download


class LiveEffortPointBoxSpec(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `live_effort_point_box_spec_m` (
        `live_effort_point_box_spec_id` INTEGER NOT NULL,
        `capacity` INTEGER NOT NULL,
        `limited_capacity` INTEGER NOT NULL,
        `num_rewards` INTEGER NOT NULL,
        `closed_asset` TEXT NOT NULL,
        `closed_asset_en` TEXT,
        `opened_asset` TEXT NOT NULL,
        `opened_asset_en` TEXT,
        `box_asset` TEXT NOT NULL,
        `box_asset_en` TEXT,
        `login_box_asset` TEXT NOT NULL,
        `login_box_asset_en` TEXT,
        `movie_name` TEXT NOT NULL,
        `movie_name_en` TEXT,
        `asset_se_id` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`live_effort_point_box_spec_id`)
    )```
    """

    __tablename__ = "live_effort_point_box_spec_m"
    live_effort_point_box_spec_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, primary_key=True
    )
    capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    limited_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    num_rewards: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    closed_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    closed_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    opened_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    opened_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    box_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    box_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    login_box_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    login_box_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    movie_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    movie_name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    asset_se_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('effort')}?mode=ro&uri=true",
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
