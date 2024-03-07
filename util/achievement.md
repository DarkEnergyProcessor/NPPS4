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

Below is the list of achievement types and their corresponding parameters:

### Live Clear (Type 1)

When to check: Clearing a live show.

* `params1` - Amount of live show to clear.

### Live Clear with Difficulty (Type 2)

When to check: Clearing a live show.

* `params1` - Difficulty number (1 Easy, 2 Normal, 3 Hard, 4 Expert).
* `params2` - Amount of live show to clear.

### Live Clear with Score Rank (Type 3)

When to check: Clearing a live show.

* `params1` - Score rank (1 S, 2 A, 3 B, 4 C)
* `params2` - Amount of live show to clear.

### Live Clear with Combo Rank (Type 4)

When to check: When clearing a live show.

* `params1` - Combo rank (1 S, 2 A, 3 B, 4 C)
* `params2` - Amount of live show to clear.

### UR Challenge (Type 6)

**Undocumented.**

### Live Clear with At Least 1 Specific Character (Type 7)

When to check: Clearing a live show.

* `params1` - Character `unit_type_id` in `unit_m` table.
* `params2` - Amount of live show to clear.

### Live Clear with Specific Unit (Type 9)

When to check: When clearing a live show.

Note: This is quite confusing as some achievement have mismatched description and parameters. More info needed.

* `params1` - Card `unit_id` in `unit_m` table.
* `params2` - Character `unit_type_id` in `unit_m` table.
* `params3` - Amount of live show to clear.

### Scouting (Type 10)

When to check: Scouting.

* `params1` - `secretbox_id` in the server (1 = μ's Regular, 2 = μ's Honor, 61 = Aqours Regular, 62 = Aqours Honor).
* `params2` - Amount of members to scout.

### Practice Live? (Type 11)

**Undocumented.**

* `params1` - Amount of live practice?

### Skill Level Practice (Type 13)

When to check: Practicing member.

* `params1` - Target skill level.

### Collect Different Members in Album (Type 18)

When to check: Scouting, Present Box, Clearing a live show.

* `params1` - Amount of different members to collect.

### Idolize Different Members in Album (Type 19)

When to check: Scouting, Present Box, Clearing a live show, Idolizing member.

* `params1` - Amount of different members to idolize.

### Max Bond Different Members in Album (Type 20)

When to check: Clearing a live show.

* `params1` - Amount of different members to max bond.

### Max Level Different Members in Album (Type 21)

When to check: Practicing member.

* `params1` - Amount of different members to max level after being idolized.

### Main Story (Type 23)

When to check: Clearing a main story.

* `params1` - `scenario_id` in `scenario_m` table.

### Friends (Type 26)

When to check: Anywhere

* `params1` - Amount of friends.

### Login (Type 27)

When to check: If egligible of getting login bonus.

* `params1` - Amount of login required.

### Single Login (Type 29)

When to check: Logging in.

No parameters.

### Rank Up (Type 30)

When to check: Clearing a live show.

* `params1` - Player level.

### Live Clear Once with Specific Song (Type 32)

When to check: Clearing a live show.

* `params1` - `live_track_id` in `live_m`.

### Idolize Card of Specific Character (Type 33)

When to check: Scouting, Present Box, Clearing a live show, Idolizing member.

* `params1` - Character `unit_type_id` in `unit_m` table.
* `params2` - Amount to idolize.

### Live Clear with Specific Song (Type 37)

When to check: Clearing a live show.

Note: This seems used for limited-time achievement only.

* `params1` - `live_track_id` in `live_m`.
* `params2` - Amount of live show to clear.

### Special Practice Live? (Type 38)

**Undocumented.**

* `params1` - Amount of special live practice?

### Live Clear Advanced (Type 50)

**Undocumented.**

When to check: Clearing a live show.

* `params1` - `live_track_id` in `live_m` or `null` for no live track requirement.
* `params6` - Combo rank (1 S, 2 A, 3 B, 4 C) or `null` for no combo rank requirement.
* `params7` - _Unknown_
* `params8` - `achievement_unit_type_group_id` in `achievement_unit_type_group_m` table.
* `params9` - _Unknown_
* `params10` - Amount of live show to clear.

### _Unknown_ (Type 51)

**Undocumented.**

### Login Part 2 (Type 52)

When to check: If egligible of getting login bonus.

* `params1` - Amount of login required.

### Clear Specific Amount of Achievement Category (Type 53)

When to check: When completing achievement.

* `params1` - Achievement category in `achievement_category_m`.
* `params2` - Amount of achievement to clear.
* `params3` - _Unknown_

### Collect Items (Type 55)

**Undocumented.**

When to check: Collecting item.

* `params1` - `item_id` in `kg_item_m` table.
* `params2` - _Unknown_ (always 1).
* `params3` - _Unknown_.
* `params5` - _Unknown_.

### _Unknown_ (Type 56)

**Undocumented.**

### Clearing Main Story (Type 57)

When to check: Clearing a main story.

* `params1` - Amount of main story to clear.

### Total Live Clear (Type 58)

When to check: Clearing a live show.

* `params1` - Amount of live show to clear.

### Unlock Main Story (Type 59)

When to check: Clearing a live show.

* `params1` - Amount of main story to unlock.

### _Unknown_ Login Bonus (Type 60)

**Undocumented.**
