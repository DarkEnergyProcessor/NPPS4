import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class LiveTrack(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `live_track_m` (
        `live_track_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `name_kana` TEXT NOT NULL,
        `name_kana_en` TEXT,
        `title_asset` TEXT NOT NULL,
        `title_asset_en` TEXT,
        `sound_asset` TEXT NOT NULL,
        `member_category` INTEGER NOT NULL,
        `member_tag_id` INTEGER NOT NULL,
        `unit_type_id` INTEGER,
        PRIMARY KEY (`live_track_id`)
    )
    ```"""

    __tablename__ = "live_track_m"
    live_track_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_kana: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_kana_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    title_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    title_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    sound_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    member_category: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    member_tag_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_type_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class LiveSetting(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `live_setting_m` (
        `live_setting_id` INTEGER NOT NULL,
        `live_track_id` INTEGER NOT NULL,
        `difficulty` INTEGER NOT NULL,
        `stage_level` INTEGER NOT NULL,
        `attribute_icon_id` INTEGER NOT NULL,
        `live_icon_asset` TEXT NOT NULL,
        `live_icon_asset_en` TEXT,
        `asset_movie_id` INTEGER,
        `asset_background_id` INTEGER NOT NULL,
        `notes_setting_asset` TEXT NOT NULL,
        `notes_setting_asset_en` TEXT,
        `c_rank_score` INTEGER NOT NULL,
        `b_rank_score` INTEGER NOT NULL,
        `a_rank_score` INTEGER NOT NULL,
        `s_rank_score` INTEGER NOT NULL,
        `c_rank_combo` INTEGER NOT NULL,
        `b_rank_combo` INTEGER NOT NULL,
        `a_rank_combo` INTEGER NOT NULL,
        `s_rank_combo` INTEGER NOT NULL,
        `ac_flag` INTEGER NOT NULL,
        `swing_flag` INTEGER NOT NULL,
        `lane_count` INTEGER NOT NULL,
        PRIMARY KEY (`live_setting_id`)
    )
    ```"""

    __tablename__ = "live_setting_m"
    live_setting_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    live_track_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("live_track_m.live_track_id")
    )
    difficulty: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    stage_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    attribute_icon_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    live_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    live_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    asset_movie_id: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    asset_background_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    notes_setting_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    notes_setting_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    c_rank_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    b_rank_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    a_rank_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    s_rank_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    c_rank_combo: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    b_rank_combo: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    a_rank_combo: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    s_rank_combo: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    ac_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    swing_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    lane_count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class Live:
    live_difficulty_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    live_setting_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("live_setting_m.live_setting_id")
    )


class CommonLive:
    capital_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    capital_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    c_rank_complete: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    b_rank_complete: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    a_rank_complete: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    s_rank_complete: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class NormalLive(common.GameDBBase, CommonLive, Live):
    """```sql
    CREATE TABLE `normal_live_m` (
        `live_difficulty_id` INTEGER NOT NULL,
        `live_setting_id` INTEGER NOT NULL,
        `capital_type` INTEGER NOT NULL,
        `capital_value` INTEGER NOT NULL,
        `default_unlocked_flag` INTEGER NOT NULL,
        `c_rank_complete` INTEGER NOT NULL,
        `b_rank_complete` INTEGER NOT NULL,
        `a_rank_complete` INTEGER NOT NULL,
        `s_rank_complete` INTEGER NOT NULL,
        PRIMARY KEY (`live_difficulty_id`)
    )
    ```"""

    __tablename__ = "normal_live_m"
    default_unlocked_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class SpecialLive(common.GameDBBase, CommonLive, Live):
    """```sql
    CREATE TABLE `special_live_m` (
        `live_difficulty_id` INTEGER NOT NULL,
        `live_setting_id` INTEGER NOT NULL,
        `capital_type` INTEGER NOT NULL,
        `capital_value` INTEGER NOT NULL,
        `c_rank_complete` INTEGER NOT NULL,
        `b_rank_complete` INTEGER NOT NULL,
        `a_rank_complete` INTEGER NOT NULL,
        `s_rank_complete` INTEGER NOT NULL,
        `exclude_clear_count_flag` INTEGER NOT NULL,
        `exclude_effort_point_flag` INTEGER NOT NULL,
        `exclude_live_bonus_flag` INTEGER NOT NULL,
        PRIMARY KEY (`live_difficulty_id`)
    )
    ```"""

    __tablename__ = "special_live_m"
    exclude_clear_count_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    exclude_effort_point_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    exclude_live_bonus_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class FreeLive(common.GameDBBase, Live):
    """```sql
    CREATE TABLE `free_live_m` (
        `live_difficulty_id` INTEGER NOT NULL,
        `live_setting_id` INTEGER NOT NULL,
        `random_flag` INTEGER NOT NULL,
        PRIMARY KEY (`live_difficulty_id`)
    )
    ```"""

    __tablename__ = "free_live_m"
    random_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class LiveCombo(common.GameDBBase):
    """```sql
    CREATE TABLE `live_combo_m` (
        `combo_cnt` INTEGER NOT NULL,
        `score_rate` REAL NOT NULL,
        `add_love_cnt` INTEGER NOT NULL,
        PRIMARY KEY (`combo_cnt`)
    )
    ```"""

    __tablename__ = "live_combo_m"
    combo_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    score_rate: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    add_love_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class LiveUnitRewardLot(common.GameDBBase):
    """```sql
    CREATE TABLE `live_unit_reward_lot_m` (
        `live_unit_reward_lot_id` INTEGER NOT NULL,
        `difficulty` INTEGER NOT NULL,
        `condition_type` INTEGER NOT NULL,
        `rank` INTEGER,
        `live_unit_reward_group_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        PRIMARY KEY (`live_unit_reward_lot_id`)
    )
    ```"""

    __tablename__ = "live_unit_reward_lot_m"
    live_unit_reward_lot_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    difficulty: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    condition_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    live_unit_reward_group_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    weight: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class CommonGoalReward:
    live_goal_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    add_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    item_category_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    item_option: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class LiveGoalRewardCommon(common.GameDBBase, CommonGoalReward):
    """```sql
    CREATE TABLE `live_goal_reward_common_m` (
        `live_goal_reward_common_id` INTEGER NOT NULL,
        `live_type` INTEGER NOT NULL,
        `difficulty` INTEGER NOT NULL,
        `live_goal_type` INTEGER NOT NULL,
        `rank` INTEGER NOT NULL,
        `add_type` INTEGER NOT NULL,
        `item_id` INTEGER NOT NULL,
        `item_category_id` INTEGER,
        `amount` INTEGER NOT NULL,
        `item_option` TEXT,
        PRIMARY KEY (`live_goal_reward_common_id`)
    )
    ```"""

    __tablename__ = "live_goal_reward_common_m"
    live_goal_reward_common_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    live_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    difficulty: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class LiveGoalReward(common.GameDBBase, CommonGoalReward):
    """```sql
    CREATE TABLE `live_goal_reward_m` (
        `live_goal_reward_id` INTEGER NOT NULL,
        `live_difficulty_id` INTEGER NOT NULL,
        `live_goal_type` INTEGER NOT NULL,
        `rank` INTEGER NOT NULL,
        `add_type` INTEGER NOT NULL,
        `item_id` INTEGER NOT NULL,
        `item_category_id` INTEGER,
        `amount` INTEGER NOT NULL,
        `item_option` TEXT,
        PRIMARY KEY (`live_goal_reward_id`)
    )
    ```"""

    __tablename__ = "live_goal_reward_m"
    live_goal_reward_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    live_difficulty_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)


class LiveNoteScoreFactor(common.GameDBBase):
    """```sql
    CREATE TABLE `live_note_score_factor_m` (
        `effect_id` INTEGER NOT NULL,
        `difficulty` INTEGER NOT NULL,
        `score_factor` REAL NOT NULL,
        PRIMARY KEY (`effect_id`,`difficulty`)
    )
    ```"""

    __tablename__ = "live_note_score_factor_m"
    effect_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    difficulty: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    score_factor: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)


class LiveCutinBrightness(common.GameDBBase):
    """```sql
    CREATE TABLE `live_cutin_brightness_m` (
        `live_cutin_brightness_id` INTEGER NOT NULL,
        `brightness` INTEGER NOT NULL,
        PRIMARY KEY (`live_cutin_brightness_id`)
    )
    ```"""

    __tablename__ = "live_cutin_brightness_m"
    live_cutin_brightness_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    brightness: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class TrainingMode(common.GameDBBase):
    """```sql
    CREATE TABLE `training_mode_m` (
        `training_mode_id` INTEGER NOT NULL,
        `recovery_cost` INTEGER NOT NULL,
        `start_date` TEXT NOT NULL,
        PRIMARY KEY (`training_mode_id`)
    )
    ```"""

    __tablename__ = "training_mode_m"
    training_mode_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    recovery_cost: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    start_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()


class LiveTime(common.GameDBBase):
    """```sql
    CREATE TABLE `live_time_m` (
        `live_track_id` INTEGER NOT NULL,
        `live_time` REAL NOT NULL,
        PRIMARY KEY (`live_track_id`)
    )
    ```"""

    __tablename__ = "live_time_m"
    live_track_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("live_track_m.live_track_id"), primary_key=True
    )
    live_time: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()


class LiveSkillIcon(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `live_skill_icon_m` (
        `skill_effect_type` INTEGER NOT NULL,
        `icon_asset` TEXT NOT NULL,
        `icon_asset_en` TEXT,
        `icon_order` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`skill_effect_type`)
    )
    ```"""

    __tablename__ = "live_skill_icon_m"
    skill_effect_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    icon_order: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class SpecialLiveRotation(common.GameDBBase):
    """```sql
    CREATE TABLE `special_live_rotation_m` (
        `rotation_group_id` INTEGER NOT NULL,
        `live_difficulty_id` INTEGER NOT NULL,
        `base_date` TEXT NOT NULL,
        PRIMARY KEY (`rotation_group_id`,`base_date`)
    )
    ```"""

    __tablename__ = "special_live_rotation_m"
    rotation_group_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    live_difficulty_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    base_date: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('live')}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)


def get_sessionmaker():
    global sessionmaker
    return sessionmaker
