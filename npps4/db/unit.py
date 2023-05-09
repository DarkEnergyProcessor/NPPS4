import sqlalchemy
import sqlalchemy.orm

from . import common
from .. import download


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

    __tablename__ = "unit_attribute_m"
    attribute_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)


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

    __tablename__ = "unit_type_m"
    unit_type_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    speaker_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    speaker_name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    asset_background_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(sqlalchemy.Integer)
    image_button_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    image_button_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    background_color: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    background_color_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    name_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    name_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    album_series_name_image_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    album_series_name_image_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    skit_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    named_skit_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    named_skit_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    name_plate_icon_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    age: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    age_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    birthday: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    birthday_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    school: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    school_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    hobby: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    hobby_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    blood_type: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    blood_type_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    height: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    height_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    three_size: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    three_size_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    member_category: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    cv: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    cv_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)


class Unit(Base, common.MaybeEncrypted):
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
    eponym: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    eponym_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    normal_card_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    rank_max_card_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    normal_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    normal_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    rank_max_icon_asset: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    rank_max_icon_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
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


class MemberTag(Base, common.MaybeEncrypted):
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
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    img_asset: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    img_asset_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    display_flag: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    num_of_members: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()


class UnitTypeMemberTag(Base):
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


class UnitMemberTag(Base):
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


class UnitLevelUpPattern(Base):
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


class UnitBaseFunctionVoice(Base, _UnitVoiceCommon, _UnitFunctionVoiceCommon):
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


class UnitFunctionVoice(Base, _UnitVoiceCommon, _UnitFunctionVoiceCommon):
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


class UnitBaseRandomVoice(Base, _UnitVoiceCommon):
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


class UnitRandomVoice(Base, _UnitVoiceCommon):
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


class UnitBaseTouchVoice(Base, _UnitTouchVoiceCommon, _UnitVoiceCommon):
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


class UnitTouchVoice(Base, _UnitTouchVoiceCommon, _UnitVoiceCommon):
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


class UnitSkill(Base, common.MaybeEncrypted):
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
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String)
    name_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    max_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    skill_effect_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    discharge_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    trigger_effect_type: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
    unit_skill_level_up_pattern_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    string_key_trigger: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    string_key_effect: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    string_key_long_description: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)


engine = sqlalchemy.create_engine(
    f"sqlite+pysqlite:///file:{download.get_db_path('unit')}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)
sessionmaker = sqlalchemy.orm.sessionmaker()
sessionmaker.configure(binds={Base: engine})
scoped_session = sqlalchemy.orm.scoped_session(sessionmaker)


def get_session():
    global scoped_session
    session = scoped_session()
    return session
