import sqlalchemy
import sqlalchemy.orm

from . import common
from .. import config


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


class UnitAttribute(Base):
    """```sql
    CREATE TABLE `unit_attribute_m` (
        `attribute_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        PRIMARY KEY (`attribute_id`)
    )
    ```"""

    attribute_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String, nullable=True)


class UnitType(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_type_m` (
        `unit_type_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `speaker_name` TEXT NOT NULL,
        `speaker_name_en` TEXT,
        `asset_background_id` INTEGER,
        `image_button_asset` TEXT,
        `image_button_asset_en` TEXT,
        `background_color` TEXT NOT NULL,
        `background_color_en` TEXT,
        `name_image_asset` TEXT,
        `name_image_asset_en` TEXT,
        `album_series_name_image_asset` TEXT,
        `album_series_name_image_asset_en` TEXT,
        `skit_icon_asset` TEXT,
        `named_skit_icon_asset` TEXT,
        `named_skit_icon_asset_en` TEXT,
        `name_plate_icon_asset` TEXT,
        `age` TEXT NOT NULL,
        `age_en` TEXT,
        `birthday` TEXT,
        `birthday_en` TEXT,
        `school` TEXT,
        `school_en` TEXT,
        `hobby` TEXT,
        `hobby_en` TEXT,
        `blood_type` TEXT,
        `blood_type_en` TEXT,
        `height` TEXT,
        `height_en` TEXT,
        `three_size` TEXT,
        `three_size_en` TEXT,
        `member_category` INTEGER NOT NULL,
        `cv` TEXT,
        `cv_en` TEXT,
        `original_attribute_id` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_type_id`)
    )
    ```"""

    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, nullable=True)
    speaker_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    speaker_name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, nullable=True)
    asset_background_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Integer, nullable=True
    )
    image_button_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, nullable=True)
    image_button_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        common.String, nullable=True
    )
    background_color: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    background_color_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, nullable=True)
    name_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, nullable=True)
    name_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, nullable=True)
    album_series_name_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        common.String, nullable=True
    )
    album_series_name_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        common.String, nullable=True
    )


engine = sqlalchemy.create_engine(
    f"sqlite+pysqlite:///file:{config.get_data_directory()}/db/unit.db_?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
scoped_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))


def get_session():
    global scoped_session
    session = scoped_session()
    return session
