import sqlalchemy
import sqlalchemy.orm

from . import common
from .. import download


class Base(sqlalchemy.orm.DeclarativeBase):
    type_annotation_map = common.type_map_override


class KGItem(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `kg_item_m` (
        `item_id` INTEGER NOT NULL,
        `item_tab_id` INTEGER NOT NULL,
        `name` TEXT,
        `name_en` TEXT,
        `item_category_id` INTEGER,
        `item_sub_category_id` INTEGER,
        `effect_value` INTEGER,
        `image_asset` TEXT,
        `image_asset_en` TEXT,
        `icon_image_asset` TEXT,
        `icon_image_asset_en` TEXT,
        `description` TEXT,
        `description_en` TEXT,
        `rank` INTEGER,
        `enhancement_exp_id` INTEGER,
        `enhancement_pattern_id` INTEGER,
        `merchandise_group_id` INTEGER,
        `merchandise_flag` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "kg_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    item_tab_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    item_category_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(index=True)
    item_sub_category_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    effect_value: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    icon_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    icon_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    rank: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    enhancement_exp_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    enhancement_pattern_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    mechandise_group_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    merchandise_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class Award(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `award_m` (
        `award_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `description` TEXT NOT NULL,
        `description_en` TEXT,
        `img_asset` TEXT NOT NULL,
        `img_asset_en` TEXT,
        `sort` INTEGER NOT NULL,
        `di_asset_display_flag` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`award_id`)
    )
    ```"""

    __tablename__ = "award_m"
    award_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    img_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    img_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    di_asset_display_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class Background(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `background_m` (
        `background_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `description` TEXT NOT NULL,
        `description_en` TEXT,
        `img_asset` TEXT NOT NULL,
        `thumbnail_asset` TEXT NOT NULL,
        `sort` INTEGER NOT NULL,
        `background_shader_param_id` INTEGER,
        `background_flash_param_id` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`background_id`)
    )
    ```"""

    __tablename__ = "background_m"
    background_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    img_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    thumbnail_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    background_shader_param_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    background_flash_param_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


# TODO: background_shader_param_m
# TODO: background_flash_m


class LiveSE(Base):
    """```sql
    CREATE TABLE `live_se_m` (
        `live_se_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `description` TEXT NOT NULL,
        `description_en` TEXT,
        `sort` INTEGER NOT NULL,
        PRIMARY KEY (`live_se_id`)
    )
    ```"""

    __tablename__ = "live_se_m"
    live_se_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


# TODO: live_se_group_m


class LiveNotesIcon(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `live_notes_icon_m` (
        `live_notes_icon_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `sort` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`live_notes_icon_id`)
    )
    ```"""

    __tablename__ = "live_notes_icon_m"
    live_notes_icon_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


# TODO: live_notes_icon_asset_m


class RecoveryItem(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `recovery_item_m` (
        `recovery_item_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `recovery_type` INTEGER NOT NULL,
        `recovery_value` INTEGER NOT NULL,
        `small_asset` TEXT,
        `small_asset_en` TEXT,
        `middle_asset` TEXT,
        `middle_asset_en` TEXT,
        `large_asset` TEXT,
        `large_asset_en` TEXT,
        `description` TEXT NOT NULL,
        `description_en` TEXT,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`recovery_item_id`)
    )
    ```"""

    __tablename__ = "recovery_item_m"
    recovery_item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    recovery_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    recovery_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    small_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    small_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    large_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    large_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class ChangeDelegateItem(Base):
    """```sql
    CREATE TABLE `change_delegate_item_m` (
        `item_id` INTEGER NOT NULL,
        `unit_type_id` INTEGER NOT NULL,
        `rarity` INTEGER NOT NULL,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "change_delegate_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class ChangeDelegateItemAmount(Base):
    """```sql
    CREATE TABLE `change_delegate_item_amount_m` (
        `unit_rarity` INTEGER NOT NULL,
        `item_rarity` INTEGER NOT NULL,
        `amount` INTEGER NOT NULL,
        `cost_game_coin_amount` INTEGER NOT NULL,
        PRIMARY KEY (`unit_rarity`,`item_rarity`)
    )
    ```"""

    __tablename__ = "change_delegate_item_amount_m"
    unit_rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    item_rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cost_game_coin_amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class BuffItem(Base):
    """```sql
    CREATE TABLE `buff_item_m` (
        `item_id` INTEGER NOT NULL,
        `buff_type` INTEGER NOT NULL,
        `buff_logic` INTEGER NOT NULL,
        `buff_amount` INTEGER NOT NULL,
        `limit_logic` INTEGER NOT NULL,
        `limit_amount` INTEGER NOT NULL,
        `event_id` INTEGER,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "buff_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    buff_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    buff_logic: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    buff_amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    limit_logic: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    limit_amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    event_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class UnitEnhanceItem(Base):
    """```sql
    CREATE TABLE `unit_enhance_item_m` (
        `item_id` INTEGER NOT NULL,
        `unit_id` INTEGER,
        `rarity` INTEGER,
        `enhance_type` INTEGER NOT NULL,
        `enhance_amount` INTEGER NOT NULL,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "unit_enhance_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    rarity: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    enhance_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    enhance_amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class LotteryTicket(Base):
    """```sql
    CREATE TABLE `lottery_ticket_item_m` (
        `item_id` INTEGER NOT NULL,
        `lottery_ticket_id` INTEGER NOT NULL,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "lottery_ticket_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    lottery_ticket_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitReinforceItem(Base):
    """```sql
    CREATE TABLE `unit_reinforce_item_m` (
        `item_id` INTEGER NOT NULL,
        `reinforce_type` INTEGER NOT NULL,
        `addition_value` INTEGER NOT NULL,
        `event_id` INTEGER,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "unit_reinforce_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    reinforce_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    addition_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    event_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class UnitReinforceItemTargetUnit(Base):
    """```sql
    CREATE TABLE `unit_reinforce_item_target_unit_m` (
        `item_id` INTEGER NOT NULL,
        `unit_id` INTEGER NOT NULL,
        PRIMARY KEY (`item_id`,`unit_id`)
    )
    ```"""

    __tablename__ = "unit_reinforce_item_target_unit_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)


class ItemExchange(Base):
    """```sql
    CREATE TABLE `item_exchange_m` (
        `item_id` INTEGER NOT NULL,
        `next_item_id` INTEGER NOT NULL,
        `amount` INTEGER NOT NULL,
        `game_coin_amount` INTEGER NOT NULL,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "item_exchange_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    next_item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    game_coin_amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UserRankUpItem(Base):
    """```sql
    CREATE TABLE `user_rank_up_item_m` (
        `item_id` INTEGER NOT NULL,
        `use_limit_rank` INTEGER,
        `use_limit_rank_min` INTEGER,
        PRIMARY KEY (`item_id`)
    )
    ```"""

    __tablename__ = "user_rank_up_item_m"
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    use_limit_rank: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    use_limit_rank_min: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class BuffItemUseLimitTime(Base):
    """```sql
    CREATE TABLE `buff_item_use_limit_time_m` (
        `buff_item_use_limit_time_id` INTEGER NOT NULL,
        `start_time` TEXT NOT NULL,
        `end_time` TEXT NOT NULL,
        PRIMARY KEY (`buff_item_use_limit_time_id`)
    )
    ```"""

    __tablename__ = "buff_item_use_limit_time_m"
    buff_item_use_limit_time_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    start_time: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    end_time: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()


class ItemExpire(Base):
    """```sql
    CREATE TABLE `item_expire_m` (
        `add_type` INTEGER NOT NULL,
        `item_id` INTEGER NOT NULL,
        `expire_date` TEXT NOT NULL,
        PRIMARY KEY (`add_type`,`item_id`)
    )
    ```"""

    __tablename__ = "item_expire_m"
    add_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    expire_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()


class Memories(Base, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `memories_m` (
        `memories_id` INTEGER NOT NULL,
        `img_asset` TEXT NOT NULL,
        `background_shader_param_id` INTEGER,
        `background_flash_param_id` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`memories_id`)
    )
    ```"""

    __tablename__ = "memories_m"
    memories_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    img_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    background_shader_param_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    background_flash_param_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.create_engine(
    f"sqlite+pysqlite:///file:{download.get_db_path('item')}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
sessionmaker = sqlalchemy.orm.sessionmaker()
sessionmaker.configure(binds={Base: engine})
scoped_session = sqlalchemy.orm.scoped_session(sessionmaker)


def get_session():
    global scoped_session
    session = scoped_session()
    return session
