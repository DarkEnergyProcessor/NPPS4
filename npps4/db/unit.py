import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from ..download import download


class UnitAttribute(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_attribute_m` (
        `attribute_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        PRIMARY KEY (`attribute_id`)
    )
    ```"""

    __tablename__ = "unit_attribute_m"
    attribute_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()


class UnitType(common.GameDBBase, common.MaybeEncrypted):
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

    __tablename__ = "unit_type_m"
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    speaker_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    speaker_name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    asset_background_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(sqlalchemy.Integer)
    image_button_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    image_button_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    background_color: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    background_color_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    album_series_name_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    album_series_name_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    skit_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    named_skit_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    named_skit_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_plate_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    age: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    age_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    birthday: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    birthday_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    school: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    school_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    hobby: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    hobby_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    blood_type: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    blood_type_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    height: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    height_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    three_size: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    three_size_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    member_category: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cv: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    cv_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class Unit(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_m` (
        `unit_id` INTEGER NOT NULL,
        `unit_number` INTEGER NOT NULL,
        `unit_type_id` INTEGER NOT NULL,
        `album_series_id` INTEGER,
        `eponym` TEXT,
        `eponym_en` TEXT,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `normal_card_id` INTEGER NOT NULL,
        `rank_max_card_id` INTEGER NOT NULL,
        `normal_icon_asset` TEXT NOT NULL,
        `normal_icon_asset_en` TEXT,
        `rank_max_icon_asset` TEXT NOT NULL,
        `rank_max_icon_asset_en` TEXT,
        `normal_unit_navi_asset_id` INTEGER NOT NULL,
        `rank_max_unit_navi_asset_id` INTEGER NOT NULL,
        `rarity` INTEGER NOT NULL,
        `attribute_id` INTEGER NOT NULL,
        `default_unit_skill_id` INTEGER,
        `skill_asset_voice_id` INTEGER,
        `default_leader_skill_id` INTEGER,
        `default_removable_skill_capacity` INTEGER NOT NULL,
        `max_removable_skill_capacity` INTEGER NOT NULL,
        `disable_rank_up` INTEGER NOT NULL,
        `rank_min` INTEGER NOT NULL,
        `rank_max` INTEGER NOT NULL,
        `unit_level_up_pattern_id` INTEGER NOT NULL,
        `hp_max` INTEGER NOT NULL,
        `smile_max` INTEGER NOT NULL,
        `pure_max` INTEGER NOT NULL,
        `cool_max` INTEGER NOT NULL,
        `reinforce_item_rank_up_cost` INTEGER,
        `sub_unit_type_id` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_id`)
    )
    ```"""

    __tablename__ = "unit_m"
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_number: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    album_series_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    eponym: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    eponym_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    normal_card_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_max_card_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    normal_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    normal_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    rank_max_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    rank_max_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    normal_unit_navi_asset_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_max_unit_navi_asset_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    attribute_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    default_unit_skill_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    skill_asset_voice_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    default_leader_skill_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    default_removable_skill_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    max_removable_skill_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    disable_rank_up: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_min: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_level_up_pattern_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    hp_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    smile_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    pure_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cool_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    reinforce_item_rank_up_cost: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    sub_unit_type_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class MemberTag(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `member_tag_m` (
        `member_tag_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `img_asset` TEXT,
        `img_asset_en` TEXT,
        `display_flag` INTEGER NOT NULL,
        `num_of_members` INTEGER,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`member_tag_id`)
    )
    ```"""

    __tablename__ = "member_tag_m"
    member_tag_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    img_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    img_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    display_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    num_of_members: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class Rarity(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_rarity_m` (
        `rarity` INTEGER NOT NULL,
        `before_love_max` INTEGER NOT NULL,
        `after_love_max` INTEGER NOT NULL,
        `before_level_max` INTEGER NOT NULL,
        `after_level_max` INTEGER NOT NULL,
        `rank_up_cost` INTEGER NOT NULL,
        `exchange_point_rank_up_cost` INTEGER NOT NULL,
        `sort` INTEGER NOT NULL,
        `costume_level_limit` INTEGER NOT NULL,
        PRIMARY KEY (`rarity`)
    )```"""

    __tablename__ = "unit_rarity_m"
    rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    before_love_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    after_love_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    before_level_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    after_level_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_up_cost: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    exchange_point_rank_up_cost: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sort: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    costume_level_limit: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitTypeMemberTag(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_type_member_tag_m` (
        `unit_type_id` INTEGER NOT NULL,
        `member_tag_id` INTEGER NOT NULL,
        PRIMARY KEY (`unit_type_id`,`member_tag_id`)
    )
    ```"""

    __tablename__ = "unit_type_member_tag_m"
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    member_tag_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)


class UnitMemberTag(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_member_tag_m` (
        `unit_id` INTEGER NOT NULL,
        `member_tag_id` INTEGER NOT NULL,
        PRIMARY KEY (`unit_id`,`member_tag_id`)
    )
    ```"""

    __tablename__ = "unit_member_tag_m"
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    member_tag_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)


class UnitLevelUpPattern(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_level_up_pattern_m` (
        `unit_level_up_pattern_id` INTEGER NOT NULL,
        `unit_level` INTEGER NOT NULL,
        `next_exp` INTEGER NOT NULL,
        `hp_diff` INTEGER NOT NULL,
        `smile_diff` INTEGER NOT NULL,
        `pure_diff` INTEGER NOT NULL,
        `cool_diff` INTEGER NOT NULL,
        `merge_exp` INTEGER NOT NULL,
        `merge_cost` INTEGER NOT NULL,
        `sale_price` INTEGER NOT NULL,
        PRIMARY KEY (`unit_level_up_pattern_id`,`unit_level`)
    )
    ```"""

    __tablename__ = "unit_level_up_pattern_m"
    unit_level_up_pattern_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    hp_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    smile_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    pure_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cool_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    merge_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    merge_cost: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sale_price: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class _UnitVoiceCommon:
    unit_status: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    asset_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    weight: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class _UnitFunctionVoiceCommon:
    function_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    function_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitBaseFunctionVoice(common.GameDBBase, _UnitVoiceCommon, _UnitFunctionVoiceCommon):
    """```sql
    CREATE TABLE `unit_base_function_voice_m` (
        `unit_base_function_voice_id` INTEGER NOT NULL,
        `unit_type_id` INTEGER NOT NULL,
        `unit_status` INTEGER NOT NULL,
        `function_id` INTEGER NOT NULL,
        `function_type` INTEGER NOT NULL,
        `asset_voice_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        PRIMARY KEY (`unit_base_function_voice_id`)
    )
    ```"""

    __tablename__ = "unit_base_function_voice_m"
    unit_base_function_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitFunctionVoice(common.GameDBBase, _UnitVoiceCommon, _UnitFunctionVoiceCommon):
    """```sql
    CREATE TABLE `unit_function_voice_m` (
        `unit_function_voice_id` INTEGER NOT NULL,
        `unit_id` INTEGER NOT NULL,
        `unit_status` INTEGER NOT NULL,
        `function_id` INTEGER NOT NULL,
        `function_type` INTEGER NOT NULL,
        `asset_voice_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        PRIMARY KEY (`unit_function_voice_id`)
    )
    ```"""

    __tablename__ = "unit_function_voice_m"
    unit_function_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitBaseRandomVoice(common.GameDBBase, _UnitVoiceCommon):
    """```sql
    CREATE TABLE `unit_base_random_voice_m` (
        `unit_base_random_voice_id` INTEGER NOT NULL,
        `unit_type_id` INTEGER NOT NULL,
        `unit_status` INTEGER NOT NULL,
        `asset_voice_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        PRIMARY KEY (`unit_base_random_voice_id`)
    )
    ```"""

    __tablename__ = "unit_base_random_voice_m"
    unit_base_random_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitRandomVoice(common.GameDBBase, _UnitVoiceCommon):
    """```sql
    CREATE TABLE `unit_random_voice_m` (
        `unit_random_voice_id` INTEGER NOT NULL,
        `unit_id` INTEGER NOT NULL,
        `unit_status` INTEGER NOT NULL,
        `asset_voice_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        PRIMARY KEY (`unit_random_voice_id`)
    )
    ```"""

    __tablename__ = "unit_random_voice_m"
    unit_random_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class _UnitTouchVoiceCommon:
    from_x: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    from_y: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    to_x: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    to_y: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitBaseTouchVoice(common.GameDBBase, _UnitTouchVoiceCommon, _UnitVoiceCommon):
    """```sql
    CREATE TABLE `unit_base_touch_voice_m` (
        `unit_base_touch_voice_id` INTEGER NOT NULL,
        `unit_type_id` INTEGER NOT NULL,
        `unit_status` INTEGER NOT NULL,
        `from_x` INTEGER NOT NULL,
        `from_y` INTEGER NOT NULL,
        `to_x` INTEGER NOT NULL,
        `to_y` INTEGER NOT NULL,
        `asset_voice_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        `min_rarity` INTEGER NOT NULL,
        PRIMARY KEY (`unit_base_touch_voice_id`)
    )
    ```"""

    __tablename__ = "unit_base_touch_voice_m"
    unit_base_touch_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    min_rarity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitTouchVoice(common.GameDBBase, _UnitTouchVoiceCommon, _UnitVoiceCommon):
    """```sql
    CREATE TABLE `unit_touch_voice_m` (
        `unit_touch_voice_id` INTEGER NOT NULL,
        `unit_id` INTEGER NOT NULL,
        `unit_status` INTEGER NOT NULL,
        `from_x` INTEGER NOT NULL,
        `from_y` INTEGER NOT NULL,
        `to_x` INTEGER NOT NULL,
        `to_y` INTEGER NOT NULL,
        `asset_voice_id` INTEGER NOT NULL,
        `weight` INTEGER NOT NULL,
        PRIMARY KEY (`unit_touch_voice_id`)
    )
    ```"""

    __tablename__ = "unit_touch_voice_m"
    unit_touch_voice_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


# TODO: unit_base_time_voice_m
# TODO: unit_time_voice_m
# TODO: unit_period_voice_m
# TODO: unit_birthday_voice_m


class UnitSkill(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_skill_m` (
        `unit_skill_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `max_level` INTEGER NOT NULL,
        `skill_effect_type` INTEGER NOT NULL,
        `discharge_type` INTEGER NOT NULL,
        `trigger_type` INTEGER NOT NULL,
        `trigger_effect_type` INTEGER,
        `unit_skill_level_up_pattern_id` INTEGER NOT NULL,
        `string_key_trigger` TEXT,
        `string_key_effect` TEXT,
        `string_key_long_description` TEXT,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_skill_id`)
    )
    ```"""

    __tablename__ = "unit_skill_m"
    unit_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    max_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    skill_effect_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    discharge_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_effect_type: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    unit_skill_level_up_pattern_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    string_key_trigger: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    string_key_effect: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    string_key_long_description: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class UnitSkillLevelUpPattern(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_skill_level_up_pattern_m` (
        `unit_skill_level_up_pattern_id` INTEGER NOT NULL,
        `skill_level` INTEGER NOT NULL,
        `next_exp` INTEGER NOT NULL,
        PRIMARY KEY (`unit_skill_level_up_pattern_id`,`skill_level`)
    )
    ```"""

    __tablename__ = "unit_skill_level_up_pattern_m"
    unit_skill_level_up_pattern_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    skill_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitSkillLevel(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_skill_level_m` (
        `unit_skill_id` INTEGER NOT NULL,
        `skill_level` INTEGER NOT NULL,
        `effect_range` INTEGER,
        `effect_value` REAL NOT NULL,
        `discharge_time` REAL NOT NULL,
        `trigger_value` INTEGER NOT NULL,
        `trigger_limit` INTEGER,
        `activation_rate` INTEGER NOT NULL,
        `unit_skill_combo_pattern_id` INTEGER,
        `spark_count_limit` INTEGER,
        `grant_exp` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_skill_id`,`skill_level`)
    )
    ```"""

    __tablename__ = "unit_skill_level_m"
    unit_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    skill_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    effect_range: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    effect_value: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    discharge_time: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    trigger_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_limit: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    activation_rate: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_skill_combo_pattern_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    spark_count_limit: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    grant_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class AlbumSeries(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `album_series_m` (
        `album_series_id` INTEGER NOT NULL,
        `album_group_id` INTEGER NOT NULL,
        `album_tab_id` INTEGER NOT NULL,
        `order_num` INTEGER NOT NULL,
        `name` TEXT,
        `name_en` TEXT,
        `layout_type` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`album_series_id`)
    )
    ```"""

    __tablename__ = "album_series_m"
    album_series_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    album_group_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    album_tab_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    order_num: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    layout_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class RemovableSkill(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_removable_skill_m` (
        `unit_removable_skill_id` INTEGER NOT NULL,
        `name` TEXT NOT NULL,
        `name_en` TEXT,
        `skill_type` INTEGER NOT NULL,
        `unit_rarity` INTEGER,
        `level` INTEGER NOT NULL,
        `icon_asset` TEXT NOT NULL,
        `icon_asset_en` TEXT,
        `small_icon_asset` TEXT,
        `small_icon_asset_en` TEXT,
        `middle_icon_asset` TEXT,
        `middle_icon_asset_en` TEXT,
        `bond_asset` TEXT NOT NULL,
        `bond_asset_en` TEXT,
        `size` INTEGER NOT NULL,
        `description` TEXT,
        `description_en` TEXT,
        `effect_range` INTEGER NOT NULL,
        `effect_type` INTEGER NOT NULL,
        `effect_value` REAL NOT NULL,
        `fixed_value_flag` INTEGER NOT NULL,
        `target_reference_type` INTEGER NOT NULL,
        `target_type` INTEGER NOT NULL,
        `trigger_reference_type` INTEGER NOT NULL,
        `trigger_type` INTEGER NOT NULL,
        `sub_skill_id` INTEGER,
        `selling_price` INTEGER NOT NULL,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_removable_skill_id`)
    )
    ```"""

    __tablename__ = "unit_removable_skill_m"
    unit_removable_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    skill_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_rarity: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    small_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    small_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    middle_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    bond_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    bond_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    size: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    description: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    description_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    effect_range: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    effect_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    effect_value: sqlalchemy.orm.Mapped[float] = sqlalchemy.orm.mapped_column()
    fixed_value_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    target_reference_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    target_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_reference_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sub_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    selling_price: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class LeaderSkill(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_leader_skill_m` (
        `unit_leader_skill_id` INTEGER NOT NULL,
        `leader_skill_effect_type` INTEGER NOT NULL,
        `effect_value` INTEGER NOT NULL,
        `name_string_key` TEXT,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_leader_skill_id`)
    )
    ```"""

    __tablename__ = "unit_leader_skill_m"
    unit_leader_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    leader_skill_effect_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    effect_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    name_string_key: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


class ExtraLeaderSkill(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_leader_skill_extra_m` (
        `unit_leader_skill_id` INTEGER NOT NULL,
        `member_tag_id` INTEGER NOT NULL,
        `leader_skill_effect_type` INTEGER NOT NULL,
        `effect_value` INTEGER NOT NULL,
        PRIMARY KEY (`unit_leader_skill_id`)
    )
    ```"""

    __tablename__ = "unit_leader_skill_extra_m"
    unit_leader_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    member_tag_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    leader_skill_effect_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    effect_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class LevelLimitPattern(common.GameDBBase):
    """```sql
    CREATE TABLE `unit_level_limit_pattern_m` (
        `unit_level_limit_id` INTEGER NOT NULL,
        `unit_level` INTEGER NOT NULL,
        `next_exp` INTEGER NOT NULL,
        `hp_diff` INTEGER NOT NULL,
        `smile_diff` INTEGER NOT NULL,
        `pure_diff` INTEGER NOT NULL,
        `cool_diff` INTEGER NOT NULL,
        `merge_exp` INTEGER NOT NULL,
        `merge_cost` INTEGER NOT NULL,
        `sale_price` INTEGER NOT NULL,
        PRIMARY KEY (`unit_level_limit_id`,`unit_level`)
    )
    ```"""

    __tablename__ = "unit_level_limit_m"
    unit_level_limit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    unit_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    hp_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    smile_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    pure_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cool_diff: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    merge_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    merge_cost: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    sale_price: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class SignAsset(common.GameDBBase, common.MaybeEncrypted):
    """```sql
    CREATE TABLE `unit_sign_asset_m` (
        `unit_id` INTEGER NOT NULL,
        `normal_card_id` INTEGER NOT NULL,
        `rank_max_card_id` INTEGER NOT NULL,
        `normal_icon_asset` TEXT NOT NULL,
        `normal_icon_asset_en` TEXT,
        `rank_max_icon_asset` TEXT NOT NULL,
        `rank_max_icon_asset_en` TEXT,
        `release_tag` TEXT, `_encryption_release_id` INTEGER NULL,
        PRIMARY KEY (`unit_id`)
    )
    ```"""

    __tablename__ = "unit_sign_asset_m"
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    normal_card_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_max_card_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    normal_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    normal_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    rank_max_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    rank_max_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()


engine = sqlalchemy.ext.asyncio.create_async_engine(
    f"sqlite+aiosqlite:///file:{download.get_db_path('unit')}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)


def get_sessionmaker():
    global sessionmaker
    return sessionmaker
