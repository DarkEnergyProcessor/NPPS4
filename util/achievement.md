Achievement
=====

Achievement (or Goals in-game) is a feature in the game that give players rewards based on their accomplished goals.
Hence, achievement.

This file will document how the achievement system works based on the database.

Achievement Type
-----

In the database, there are various kinds of achievement types, indicated by the `achievement_type` column in
`achievement_m` table. These kinds needs to be checked only at certain events (such as when scouting or clearing live
show) and they also have parameters from `params1` to `params11`.

Certain params may have additional information in parenthesis, such as:
* compare \<op\> - Checked conditionals. Let `a` is the value to be tested and `b` is the parameter value, \<op\> can be:
  * equal - Checked condition must be exact value (`a == b`).
  * less than or equal - Checked condition is less than or equal of specific value (`a <= b`).
  * greater than or equal - Checked condition is equal or greater than of specific value (`a >= b`).
* unknown - It is unknown what to do with this value.
* local track - The increment value is tracked in this achievement only. This implies "compare greater than or equal".
* global track - The value is tracked across previous achievement. This implies "compare greater than or equal".
* behavior - Changes certain behavior when comparing certain constraints.

Below is the list of achievement types and their corresponding parameters:

### Live Clear (Type 1)

When to check: Clearing a live show.

* `params1` - Amount of live show to clear (local track).

### Live Clear with Difficulty (Type 2)

When to check: Clearing a live show.

* `params1` - Difficulty number (1 Easy, 2 Normal, 3 Hard, 4 Expert) (compare equal).
* `params2` - Amount of live show to clear (local track).

### Live Clear with Score Rank (Type 3)

When to check: Clearing a live show.

* `params1` - Score rank (1 S, 2 A, 3 B, 4 C) (compare less than or equal).
* `params2` - Amount of live show to clear (local track).

### Live Clear with Combo Rank (Type 4)

When to check: When clearing a live show.

* `params1` - Combo rank (1 S, 2 A, 3 B, 4 C) (compare less than or equal).
* `params2` - Amount of live show to clear (local track).

### UR Challenge (Type 6)

**Undocumented.** 7th-anniversary related goal.

When to check: Clearing a live show.

* `params1` - Always 7 (unknown).
* `params2` - Always 2 (unknown).

### Live Clear with At Least 1 Specific Character (Type 7)

When to check: Clearing a live show.

* `params1` - Character `unit_type_id` in `unit_m` table (compare equal).
* `params2` - Amount of live show to clear (local track).

### Live Clear with Specific Song and Unit (Type 9)

When to check: When clearing a live show.

* `params1` - `live_track_id` in `live_track_m` table (compare equal).
* `params2` - `achievement_unit_type_group_id` in `achievement_unit_type_group_m` table (compare equal).
* `params3` - Amount of live show to clear (local track).

### Scouting (Type 10)

When to check: Scouting.

* `params1` - `secretbox_id` in the server (1 = μ's Regular, 2 = μ's Honor, 61 = Aqours Regular, 62 = Aqours Honor) (compare equal).
* `params3` - Amount of members to scout (global track).

### Practice (Type 11)

When to check: Practicing member.

* `params1` - Times to practice. (global track)

### Skill Level Practice (Type 13)

When to check: Practicing member.

* `params1` - Target skill level (compare greater than or equal).

### Collect Different Members in Album (Type 18)

When to check: Scouting, Present Box, Clearing a live show.

* `params1` - Amount of different members to collect (global track).

### Idolize Different Members in Album (Type 19)

When to check: Scouting, Present Box, Clearing a live show, Idolizing member.

* `params1` - Amount of different members to idolize (global track).

### Max Bond Different Members in Album (Type 20)

When to check: Clearing a live show.

* `params1` - Amount of different members to max bond (global track).

### Max Level Different Members in Album (Type 21)

When to check: Practicing member.

* `params1` - Amount of different members to max level after being idolized (global track).

### Main Story (Type 23)

When to check: Clearing a main story.

* `params1` - `scenario_id` in `scenario_m` table (compare equal).

### Friends (Type 26)

When to check: Anywhere

* `params1` - Amount of friends (global track).

### Login (Type 27)

When to check: Getting login bonus.

* `params1` - Amount of login required (local track).

### Single Login (Type 29)

When to check: Getting login bonus.

No parameters.

### Rank Up (Type 30)

When to check: Clearing a live show, Present Box (EXP-related present only).

* `params1` - Player level (global track).

### Live Clear Once with Specific Song (Type 32)

When to check: Clearing a live show.

* `params1` - `live_track_id` in `live_m` (compare equal).

### Idolize Card of Specific Character (Type 33)

When to check: Scouting, Present Box, Clearing a live show, Idolizing member.

* `params1` - Character `unit_type_id` in `unit_m` table (compare equal).
* `params2` - Amount to idolize (local track).

### Live Clear with Specific Song (Type 37)

When to check: Clearing a live show.

Note: This seems used for limited-time achievement only.

* `params1` - `live_track_id` in `live_m` (compare equal).
* `params2` - Amount of live show to clear (local track).

### Special Practice Live? (Type 38)

**Undocumented.** This achievement is ambiguous for 2 reasons:
1. "Special Practice" can mean "idolize a club member"; or
2. Performing a live show, the "special" in here is it's unlocked by something else.

* `params1` - Amount of special live practice? (local track)

### Live Clear Advanced (Type 50)

**Partially Documented.**

When to check: Clearing a live show.

* `params1` - `live_track_id` in `live_m` or `null` for no live track requirement (compare equal).
* `params2` - Difficulty (1 = Easy, 2 = Normal, 3 = Hard, 4 = Expert, 6 = Master), or `null` for no difficulty requirement (compare equal).
* `params3` - Song attribute (1 = Smile, 2 = Pure, 3 = Cool) or `null` for no song attribute requirement (compare equal).
* `params4` - _Unknown_ (event-specific) (unknown)
* `params5` - Score rank (1 S, 2 A, 3 B, 4 C) or `null` for no score rank requirement (compare less than or equal).
* `params6` - Combo rank (1 S, 2 A, 3 B, 4 C) or `null` for no combo rank requirement (compare less than or equal).
* `params7` - Controls `param8` behavior. 1 = Team must only consist of speicifc units. 2 = At least one of each units present. (behavior)
* `params8` - `achievement_unit_type_group_id` in `achievement_unit_type_group_m` table or `null` if no unit group requirement (compare equal).
* `params9` - Controls `param8` behavior. 1 = All team unit type, 2 = At least one unit type in team. (behavior)
* `params10` - Amount of live show to clear (local track).

To explain `params7` more, consider an achievement that requires Printemps member. Now consider these teams in no
particular order (Printemps members marked in bold):
* **Honoka**
* Riko
* Chika
* **Hanayo**
* Ayumu
* **Kotori**
* Rin
* Kanata
* Kanon

If the value of `params7` is 1, the achievement condition is **not** satisfied because it requires the whole team to
consist of Printemps member (subject to `params9` control). However, if the value of `params7` is 2, the achievement
condition **is satisfied** because the team contains all Printemps members but the team is not necessarily
Printemps-only.

As in how `params7` and `params9` interact, considering the Printemps achievement example again:
* If both `params7` and `params9` is 1: The **whole team must only** (`params7`) consist of Honoka, Hanayo, **and** (`params9`) Kotori.
  Example valid team: **3x**Honoka, **3x**Kotori, and **3x**Hanayo.  
* If `params7`and `params9` is 2: The team must **have at least** (`params7`) contain Honoka, Hanayo, **or** (`params9`) Kotori.  
  Example valid team: Honoka + any member you like.
* If `params7` is 1 and `params9` is 2: The **whole team must only** (`params7`) consist of Honoka, Hanayo, Kotori, **or** (`params9`) combination inbetween.  
  Example valid teams: All Honoka; Kotori + **8x**Honoka.
* If `params7` is 2 and `params9` is 1: The team must **at least** (`params7`) contain Honoka, Hanayo, **and** (`params9`) Kotori.  
  Example valid team: **Honoka**, Riko, Chika, **Hanayo**, Ayumu, **Kotori**, Rin, Kanata, Kanon.

### _Unknown_ (Type 51)

**Partially Documented.**

When to check: Clearing a live show.

* `params1` - Always 1. (unknown)
* `params2` - Character `unit_type_id` in `unit_m` table. (compare equal)
* `params3` - Amount of live show to clear. (local track)

### Login Part 2 (Type 52)

When to check: Getting login bonus.

* `params1` - Amount of login required. (global track)

### Clear Specific Achievement Category (Type 53)

When to check: When completing achievement.

* `params1` - Achievement category in `achievement_category_m`. (compare equal)
* `params2` - Amount of achievement to clear. (global track)
* `params3` - _Unknown_ (unknown)

### Collect Items (Type 55)

**Undocumented.**

When to check: Collecting item (implies Present Box and Clearing a live show).

* `params1` - `item_id` in `kg_item_m` table (compare equal).
* `params2` - _Unknown_ (always 1). (unknown)
* `params3` - _Unknown_. (unknown)
* `params5` - _Unknown_. (unknown)

### _Unknown_ (Type 56)

**Undocumented.**

### Clearing Main Story (Type 57)

When to check: Clearing a main story.

* `params1` - Amount of main story to clear. (global track)

### Total Live Clear (Type 58)

When to check: Clearing a live show.

* `params1` - Amount of live show to clear. (global track)

### Unlock Main Story (Type 59)

When to check: Clearing a live show.

* `params1` - Amount of main story to unlock. (global track)

### _Unknown_ Login Bonus (Type 60)

**Undocumented.**

* `params1` - Month. (compare equal)
* `params2` - Day. (compare equal)
* `params3` - Always 0. (unknown)
