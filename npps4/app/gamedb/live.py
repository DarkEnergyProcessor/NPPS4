import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

from . import common

from typing import cast, Union


Base = sqlalchemy.ext.declarative.declarative_base()


class LiveTrack(Base, common.MaybeEncrypted):
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
    live_track_id: int = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    name = cast(str, sqlalchemy.Column(common.String))
    name_en = cast(Union[str, None], sqlalchemy.Column(common.String, nullable=True))
    name_kana = cast(str, sqlalchemy.Column(common.String))
    name_kana_en = cast(Union[str, None], sqlalchemy.Column(common.String, nullable=True))
    title_asset = cast(str, sqlalchemy.Column(common.String))
    title_asset_en = cast(Union[str, None], sqlalchemy.Column(common.String, nullable=True))
    sound_asset = cast(str, sqlalchemy.Column(common.String))
    member_category = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    member_tag_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    unit_type_id = cast(Union[int, None], sqlalchemy.Column(sqlalchemy.Integer, nullable=True))


class LiveSetting(Base, common.MaybeEncrypted):
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
    live_setting_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    live_track_id = cast(
        int, sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("live_track_m.live_track_id"))
    )
    difficulty = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    stage_level = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    attribute_icon_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    live_icon_asset = cast(str, sqlalchemy.Column(common.String))
    live_icon_asset_en = cast(Union[str, None], sqlalchemy.Column(common.String, nullable=True))
    asset_movie_id = cast(str, sqlalchemy.Column(common.String))
    asset_background_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    notes_setting_asset = cast(str, sqlalchemy.Column(common.String))
    notes_setting_asset_en = cast(Union[str, None], sqlalchemy.Column(common.String))
    c_rank_score = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    b_rank_score = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    a_rank_score = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    s_rank_score = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    c_rank_combo = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    b_rank_combo = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    a_rank_combo = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    s_rank_combo = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    ac_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    swing_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    lane_count = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class Live:
    live_difficulty_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    live_setting_id = cast(
        int, sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("live_setting_m.live_setting_id"))
    )


class CommonLive:
    capital_type = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    capital_value = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    c_rank_complete = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    b_rank_complete = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    a_rank_complete = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    s_rank_complete = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class NormalLive(Base, CommonLive, Live):
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
    default_unlocked_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class SpecialLive(Base, CommonLive, Live):
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
    exclude_clear_count_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    exclude_effort_point_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    exclude_live_bonus_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class FreeLive(Base, Live):
    """```sql
    CREATE TABLE `free_live_m` (
        `live_difficulty_id` INTEGER NOT NULL,
        `live_setting_id` INTEGER NOT NULL,
        `random_flag` INTEGER NOT NULL,
        PRIMARY KEY (`live_difficulty_id`)
    )
    ```"""

    __tablename__ = "free_live_m"
    random_flag = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class LiveCombo(Base):
    """```sql
    CREATE TABLE `live_combo_m` (
        `combo_cnt` INTEGER NOT NULL,
        `score_rate` REAL NOT NULL,
        `add_love_cnt` INTEGER NOT NULL,
        PRIMARY KEY (`combo_cnt`)
    )
    ```"""

    __tablename__ = "live_combo_m"
    combo_cnt = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    score_rate = cast(float, sqlalchemy.Column(common.Float))
    add_love_cnt = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class LiveUnitRewardLot(Base):
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
    live_unit_reward_lot_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    difficulty = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    condition_type = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    rank = cast(Union[int, None], sqlalchemy.Column(sqlalchemy.Integer, nullable=True))
    live_unit_reward_group_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    weight = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class CommonGoalReward:
    live_goal_type = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    rank = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    add_type = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    item_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    item_category_id = cast(Union[int, None], sqlalchemy.Column(sqlalchemy.Integer, nullable=True))
    amount = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    item_option = cast(Union[str, None], sqlalchemy.Column(common.String, nullable=True))


class LiveGoalRewardCommon(Base, CommonGoalReward):
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
    live_goal_reward_common_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    live_type = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    difficulty = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class LiveGoalReward(Base, CommonGoalReward):
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
    live_goal_reward_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    live_difficulty_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, index=True))


class LiveNoteScoreFactor(Base):
    """```sql
    CREATE TABLE `live_note_score_factor_m` (
        `effect_id` INTEGER NOT NULL,
        `difficulty` INTEGER NOT NULL,
        `score_factor` REAL NOT NULL,
        PRIMARY KEY (`effect_id`,`difficulty`)
    )
    ```"""

    __tablename__ = "live_note_score_factor_m"
    effect_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    difficulty = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    score_factor = cast(float, sqlalchemy.Column(common.Float, primary_key=True))


class LiveCutinBrightness(Base):
    """```sql
    CREATE TABLE `live_cutin_brightness_m` (
        `live_cutin_brightness_id` INTEGER NOT NULL,
        `brightness` INTEGER NOT NULL,
        PRIMARY KEY (`live_cutin_brightness_id`)
    )
    ```"""

    __tablename__ = "live_cutin_brightness_m"
    live_cutin_brightness_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    brightness = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class TrainingMode(Base):
    """```sql
    CREATE TABLE `training_mode_m` (
        `training_mode_id` INTEGER NOT NULL,
        `recovery_cost` INTEGER NOT NULL,
        `start_date` TEXT NOT NULL,
        PRIMARY KEY (`training_mode_id`)
    )
    ```"""

    __tablename__ = "training_mode_m"
    training_mode_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    recovery_cost = cast(int, sqlalchemy.Column(sqlalchemy.Integer))
    start_date = cast(str, sqlalchemy.Column(common.String, primary_key=True))


class LiveTime(Base):
    """```sql
    CREATE TABLE `live_time_m` (
        `live_track_id` INTEGER NOT NULL,
        `live_time` REAL NOT NULL,
        PRIMARY KEY (`live_track_id`)
    )
    ```"""

    __tablename__ = "live_time_m"
    live_track_id = cast(
        int,
        sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("live_track_m.live_track_id"), primary_key=True),
    )
    live_time = cast(float, sqlalchemy.Column(common.Float))


class LiveSkillIcon(Base, common.MaybeEncrypted):
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
    skill_effect_type = cast(int, sqlalchemy.Column(sqlalchemy.Integer, primary_key=True))
    icon_asset = cast(str, sqlalchemy.Column(common.String))
    icon_asset_en = cast(Union[str, None], sqlalchemy.Column(common.String, nullable=True))
    icon_order = cast(int, sqlalchemy.Column(sqlalchemy.Integer))


class LiveSession(sqlalchemy.orm.scoped_session[sqlalchemy.orm.Session]):
    pass


engine = sqlalchemy.create_engine("sqlite+pysqlite:///file:data/external/db/live/live.db_?mode=ro&uri=true")


def get_session():
    return cast(LiveSession, sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine)))
