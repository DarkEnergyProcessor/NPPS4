import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class FilterCategory(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `achievement_filter_category_m` (
        `achievement_filter_category_id` INTEGER NOT NULL,
        `name` TEXT,
        `name_en` TEXT,
        `icon_asset` TEXT,
        `icon_asset_en` TEXT,
        `default_select_flag` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`achievement_filter_category_id`)
    )```
    """

    __tablename__ = "achievement_filter_category_m"
    achievement_filter_category_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, primary_key=True
    )
    name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    default_select_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class Achievement(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `achievement_m` (
        `achievement_id` INTEGER NOT NULL,
        `title` TEXT,
        `title_en` TEXT,
        `description` TEXT,
        `description_en` TEXT,
        `achievement_type` INTEGER NOT NULL,
        `reset_type` INTEGER NOT NULL,
        `reset_param` INTEGER,
        `params1` INTEGER,
        `params2` INTEGER,
        `params3` INTEGER,
        `params4` INTEGER,
        `params5` INTEGER,
        `params6` INTEGER,
        `params7` INTEGER,
        `params8` INTEGER,
        `params9` INTEGER,
        `params10` INTEGER,
        `params11` INTEGER,
        `start_date` TEXT NOT NULL,
        `end_date` TEXT,
        `default_open_flag` INTEGER NOT NULL,
        `display_flag` INTEGER NOT NULL,
        `achievement_filter_category_id` INTEGER NOT NULL,
        `achievement_filter_type_id` INTEGER NOT NULL,
        `auto_reward_flag` INTEGER NOT NULL,
        `display_start_date` TEXT,
        `open_condition_string` TEXT,
        `open_condition_string_en` TEXT,
        `term_invisible_flag` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`achievement_id`)
    )```
    """

    __tablename__ = "achievement_m"
    achievement_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    title: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    title_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    achievement_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    reset_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    reset_param: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params1: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params2: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params3: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params4: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params5: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params6: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params7: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params8: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params9: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params10: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    params11: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    start_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    end_date: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    default_open_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    display_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    achievement_filter_category_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey(FilterCategory.achievement_filter_category_id)
    )
    achievement_filter_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    auto_reward_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    display_start_date: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    open_condition_string: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    open_condition_string_en: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    term_invisible_flag: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class Story(common.GameDBBase):
    """```sql
    CREATE TABLE `achievement_story_m` (
        `achievement_id` INTEGER NOT NULL,
        `next_achievement_id` INTEGER NOT NULL,
        PRIMARY KEY (`achievement_id`,`next_achievement_id`)
    )```
    """

    __tablename__ = "achievement_story_m"
    achievement_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Achievement.achievement_id), index=True
    )
    next_achievement_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Achievement.achievement_id), index=True
    )

    __table_args__ = (sqlalchemy.PrimaryKeyConstraint(achievement_id, next_achievement_id),)


class Category(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `achievement_category_m` (
        `achievement_category_id` INTEGER NOT NULL,
        `start_date` TEXT,
        `end_date` TEXT,
        `display_flag` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`achievement_category_id`)
    )```
    """

    __tablename__ = "achievement_category_m"
    achievement_category_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, primary_key=True
    )
    start_date: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    end_date: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class Tag(common.GameDBBase):
    """```sql
    CREATE TABLE `achievement_tag_m` (
        `achievement_id` INTEGER NOT NULL,
        `achievement_category_id` INTEGER NOT NULL,
        PRIMARY KEY (`achievement_id`,`achievement_category_id`)
    )```
    """

    __tablename__ = "achievement_tag_m"
    achievement_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Achievement.achievement_id), index=True
    )
    achievement_category_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Category.achievement_category_id), index=True
    )

    __table_args__ = (sqlalchemy.PrimaryKeyConstraint(achievement_id, achievement_category_id),)


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('achievement')}?mode=ro&uri=true",
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
