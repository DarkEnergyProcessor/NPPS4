import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from .. import download


class GameSetting(common.GameDBBase):
    """```sql
    CREATE TABLE `game_setting_m` (
        `game_setting_id` INTEGER NOT NULL,
        `live_loveca_for_energy` INTEGER NOT NULL,
        `live_energy_recoverly_time` INTEGER NOT NULL,
        `live_social_point_for_others` INTEGER NOT NULL,
        `live_social_point_for_friend` INTEGER NOT NULL,
        `live_social_point_for_alliance` INTEGER NOT NULL,
        `live_loveca_for_continue` INTEGER NOT NULL,
        `live_attribute_bonus_rate` REAL NOT NULL,
        `live_notes_touch_voice_rate` REAL NOT NULL,
        `live_gameover_card_cnt` INTEGER NOT NULL,
        `live_skill_gauge_cnt` INTEGER NOT NULL,
        `live_skill_need_score` INTEGER NOT NULL,
        `live_other_count` INTEGER NOT NULL,
        `live_other_level_range` INTEGER NOT NULL,
        `live_unclear_love_minus` INTEGER NOT NULL,
        `reward_available_term` INTEGER NOT NULL,
        `navigation_replacement_rate` INTEGER NOT NULL,
        `navigation_speak_time` INTEGER NOT NULL,
        `friend_invite_message` TEXT NOT NULL,
        `friend_invite_message_en` TEXT,
        `scenario_ending_message` TEXT NOT NULL,
        `scenario_ending_message_en` TEXT,
        `alliance_level_for_making` INTEGER NOT NULL,
        `alliance_game_coin_for_making` INTEGER NOT NULL,
        `deck_max` INTEGER NOT NULL,
        `nextday_time` TEXT NOT NULL,
        `card_ranking_cnt` INTEGER NOT NULL,
        `coin_alert_min_value` INTEGER NOT NULL,
        `evolution_attribute_bonus` REAL NOT NULL,
        `evolution_rankup_coin_rate` REAL NOT NULL,
        `deck_unit_max` INTEGER NOT NULL,
        `social_point_max` INTEGER NOT NULL,
        `sns_coin_max` INTEGER NOT NULL,
        `game_coin_max` INTEGER NOT NULL,
        `item_max` INTEGER NOT NULL,
        `initial_game_coin` INTEGER NOT NULL,
        `shop_loveca_for_unit_max` INTEGER NOT NULL,
        `shop_unit_max_gain` INTEGER NOT NULL,
        `unit_max` INTEGER NOT NULL,
        `waiting_unit_max` INTEGER NOT NULL,
        `shop_loveca_for_friend_max` INTEGER NOT NULL,
        `shop_friend_max_gain` INTEGER NOT NULL,
        `friend_max` INTEGER NOT NULL,
        `shop_unit_max_limit_cnt` INTEGER NOT NULL,
        `shop_friend_max_limit_cnt` INTEGER NOT NULL,
        `festival_material_max` INTEGER NOT NULL,
        `klab_id_task_start_date` TEXT NOT NULL,
        `exchange_flag` INTEGER NOT NULL,
        PRIMARY KEY (`game_setting_id`)
    )
    ```"""

    __tablename__ = "game_setting_m"
    game_setting_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    live_loveca_for_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_energy_recoverly_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_social_point_for_others: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_social_point_for_friend: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_social_point_for_alliance: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_loveca_for_continue: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_attribute_bonus_rate: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    live_notes_touch_voice_rate: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    live_gameover_card_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_skill_gauge_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_skill_need_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_other_count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_other_level_range: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_unclear_love_minus: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    reward_available_term: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    navigation_replacement_rate: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    navigation_speak_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    friend_invite_message: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    friend_invite_message_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    scenario_ending_message: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    scenario_ending_message_en: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    alliance_level_for_making: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    alliance_game_coin_for_making: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    deck_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    nextday_time: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    card_ranking_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    coin_alert_min_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    evolution_attribute_bonus: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    evolution_rankup_coin_rate: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    deck_unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    social_point_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sns_coin_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    game_coin_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    item_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    initial_game_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    shop_loveca_for_unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    shop_unit_max_gain: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    waiting_unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    shop_loveca_for_friend_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    shop_friend_max_gain: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    friend_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    shop_unit_max_limit_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    shop_friend_max_limit_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    festival_material_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    klab_id_task_start_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    exchange_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class SortCondition(common.GameDBBase):
    """```sql
    CREATE TABLE `sort_condition_m` (
        `sort_condition_id` INTEGER NOT NULL,
        `screen_id` INTEGER NOT NULL,
        `sort_condition_type` INTEGER NOT NULL,
        `sort_condition_sub_type` INTEGER,
        `sort_label` TEXT NOT NULL,
        `sort_label_en` TEXT,
        PRIMARY KEY (`sort_condition_id`)
    )
    ```"""

    __tablename__ = "sort_condition_m"
    sort_condition_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    screen_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sort_condition_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sort_condition_sub_type: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    sort_label: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    sort_label_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class AddType(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `add_type_m` (
        `add_type` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `small_asset` TEXT,
        `small_asset_en` TEXT,
        `middle_asset` TEXT,
        `middle_asset_en` TEXT,
        `large_asset` TEXT,
        `large_asset_en` TEXT,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`add_type`)
    )
    ```"""

    __tablename__ = "add_type_m"
    add_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    small_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    small_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    large_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    large_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


game_mater = download.get_db_path("game_mater")


def load_client_setting():
    sync_engine = sqlalchemy.create_engine(f"sqlite+pysqlite:///file:{game_mater}?mode=ro&uri=true")
    sync_sessionmaker = sqlalchemy.orm.sessionmaker(sync_engine)
    with sync_sessionmaker() as session:
        q = sqlalchemy.select(GameSetting).limit(1)
        result = session.execute(q)
        setting = result.scalar()
        if setting is None:
            raise RuntimeError("unable to load client setting")

        session.expunge(setting)
        return setting


GAME_SETTING = load_client_setting()

engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{game_mater}?mode=ro&uri=true",
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)
session = sessionmaker()


def get_session():
    global session
    return session
