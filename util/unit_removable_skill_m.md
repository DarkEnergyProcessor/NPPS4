Removable Skill DB
=====

Documents information about unit removable skill a.k.a. SIS.

Fields:
* `skill_type` - SIS type. 1 = Normal. 2 = Live Arena.
* `level` - _Unknown_. Always 0 for SIS type 1.
* `size` - Amount of space it occupy.
* `effect_range` - Scope of the effect applied. 1 = Self, 2 = All Team.
* `effect_type` - Kind of effect. See below for possible values.
* `effect_value` - Value of the effect. Unit is either flat value or multiplier, depending on `fixed_value_flag` below.
* `fixed_value_flag`- If this is 1, `effect_value` applies fixed-value instead of percentage.
* `target_reference_type` - Egligible members to use this SIS. Affects `target_type` value. See below for possible values.
* `target_type` - Target type based on `target_reference_type`.
* `trigger_reference_type` - Prerequisite for the SIS to take effect. 0 = No condition. 4 = `trigger_type` is `member_tag_id`.
* `trigger_type` - Target prerequisite for `trigger_reference_type`

`effect_type` values:
* 1 = Apply to Smile directly
* 2 = Apply to Pure directly
* 3 = Apply to Cool directly
* 11 = Score boost enhance.
* 12 = Add score equal to recovery value times `effect_value` on heal.
* 13 = Increase score on timing boost skill/perfect lock active (Smile).
* 14 = Increase score on timing boost skill/perfect lock active (Pure).
* 15 = Increase score on timing boost skill/perfect lock active (Cool).

`target_reference_type` mapping:
* 0 = Any. `target_type` is unused.
* 1 = Member year. `target_type` is the required member target year.
* 2 = Specific member. `target_type` is `unit_type_id`.
* 3 = Target attribute to boost during live show. `target_type` specify attribute ID.

`trigger_type` if `trigger_reference_type` is 4:
* 4 = All myus member in team.
* 5 = All Aqours member in team.
* 60 = All Nijigasaki member in team (all unit must be different unit type).
* 143 = All Liella member in team.