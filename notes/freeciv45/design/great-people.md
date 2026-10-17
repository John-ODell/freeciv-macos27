# Freeciv45 great people and golden ages

Roadmap slice 11 of [freeciv45-plan.md](../../freeciv45-plan.md) made concrete: where great-person points come
from, the seven kinds under Freeciv45's own names, what each can do once, how a golden age runs, what the AI
needs so the system is not a human-only bonus, and how to test it. It builds on [mechanics.md](../mechanics.md)
2.9 (the reference behaviour, rated MUST simplified), [in-freeciv.md](../in-freeciv.md) 4.1 row 3 and 4.2 (what
Lua can read and the User Action slots), [victory.md](victory.md) (culture numbers), [units-and-upgrades.md](units-and-upgrades.md)
(the seven great-person rows of the roster and the flag budget) and [tech-tree.md](tech-tree.md) (the techs that
grant a free great person). The reference game's terms (prophet, artist, engineer and so on) are working labels in
this note only; the names that ship are in section 2. Engine paths are `refs/freeciv-S3_2/...` unless marked
`civ45/...`, which is `port/freeciv/data/civ45/...` at commit f55003f.

## 1. What the engine gives and what Lua must do

| Need | Native or Lua | Mechanism | Evidence |
|---|---|---|---|
| Points per city per turn | Native data, Lua reads | `User_Effect_3` rows with `Building ... City` reqs; `effects.city_bonus(city, "User_Effect_3")` each `turn_begin` | `User_Effect_1`/`_2` are taken by the ancient-network sandbox effects (`civ45/effects.ruleset:4912,4936`), so only 3 and 4 are free; `city_bonus` at `common/scriptcore/tolua_game.pkg:645`; `turn_begin(turn, year)` at `server/scripting/script_server.c:424` |
| Point multiplier | Native data, Lua reads | `User_Effect_4` as a percent (golden age +100) | same reader |
| Points from specialists | Not possible yet | The `Specialist` requirement is Local range only and Lua has no specialist count | in-freeciv.md 4.1 row 3; `doc/README.effects:92`; mechanics.md 2.4 rating |
| Which kind is born | Lua | A table of building rule names to kind and weight, drawn in proportion | `City:has_building` at `tolua_game.pkg:271`; `random(min, max)` from the Freeciv Lua API |
| Birth | Lua | `edit.create_unit(player, tile, utype, 0, city, 2)` | `server/scripting/tolua_server.pkg:119-122` |
| Settle in a city | Native action plus Lua | "Join City" (the unit adds 1 population) and a Lua handler on `action_started_unit_city` that adds a "Resident" building | enabler at `civ45/actions.ruleset:1376-1382`; signal at `script_server.c:546-548`; `edit.create_building` at `tolua_server.pkg:149-150`, which checks only that the building is not a space part (`api_server_edit.c:727-731`, no requirement check: observed) |
| Finish a wonder | Native action | "Help Wonder" pours the unit's full shield value into a great wonder; nothing in Lua changes shield stock (`tolua_server.pkg:118-250` has no such call) | enabler at `civ45/actions.ruleset:1099-1113`, target `BuildingGenus GreatWonder`; the -50% shield value applies only to "Disband Unit Recover" and "Upgrade Unit" (`civ45/effects.ruleset:5450-5464`) |
| Discover a tech | Lua | `edit.give_tech(player, nil, 0, true, reason)`: a nil tech lets the server pick by `free_tech_method`, which civ45 sets to "Cheapest" | `tolua_server.pkg:186`; `api_server_edit.c:870-887`; `civ45/game.ruleset:388` |
| Burst of culture | Lua | `edit.add_city_history(city, n)`; interest is 0 in civ45 so the burst stays flat | `tolua_server.pkg:241`; `civ45/game.ruleset:402` |
| Gold | Lua | `edit.change_gold(player, n)` | `tolua_server.pkg:176-177` |
| Golden age | Lua plus data | A hidden small wonder created and removed by Lua; its effects carry `Building ... Player` reqs | `edit.remove_building` at `tolua_server.pkg:151-152`; `No_Anarchy` at `doc/README.effects:512` |
| A flat output bonus for a settled great person | Native data, with a trap | `Output_Bonus_Absolute` is clamped to zero or below in 3.2 (`common/city.c:2409`, contrary to `README.effects:546-550`), so Residents use `Output_Inc_Tile` on the city centre and `Output_Bonus` percents | `README.effects:556-558`; civ45 already uses the centre-tile pattern (`civ45/effects.ruleset:3029-3032`) |
| One-off actions | Native user actions, Lua handlers | "User Action 3" and "4" are free (1 and 2 are the sandbox leftovers, `civ45/actions.ruleset:481-492`); target kinds City, Unit, Stack, Tile or Self | `doc/README.actions:1636-1650`; `action_started_unit_self(action, unit)` at `script_server.c:570-572` |
| AI use | Lua | The AI scores ruleset-defined actions 0 and never settles a unit with "Join City" (no `ACTION_JOIN_CITY` in `ai/default/`); it does use "Help Wonder" and diplomat actions natively | `ai/default/daicity.c:1275-1277`; `daicity.c:462-472`; `daiunit.c:2765-2768` |
| Persistence | Lua | Only scalar globals survive a save, so every counter below is a global named per city or player | in-freeciv.md 4.2; victory.md uses the same pattern |

## 2. The seven kinds

Each kind is a unit type (roster rows in units-and-upgrades.md). The "label" column is the reference term, kept
for cross-reading the spec only.

| Name | Label | Points from (section 3) | Deed (section 4.2) | Resident building (section 4.1) |
|---|---|---|---|---|
| Great Sage | scientist | Library, University, Research Lab, Great Library, Copernicus' Observatory, Isaac Newton's College, Darwin's Voyage, Internet | Discover the cheapest available tech | Resident Sage: +25% science, +2 Sage points |
| Great Builder | engineer | Factory, Mfg. Plant, Pyramids, Great Wall, King Richard's Crusade, Leonardo's Workshop, Hoover Dam, Apollo Program, Manhattan Project | Help Wonder: 240 shields into a great wonder | Resident Builder: +3 shields on the centre tile, +2 Builder points |
| Great Magnate | merchant | Marketplace, Bank, Stock Exchange, Colossus, Marco Polo's Embassy, A.Smith's Trading Co., Magellan's Expedition | Trade mission: gold, doubled in a foreign city | Resident Magnate: +3 trade on the centre tile, +25% gold, +2 Magnate points |
| Great Virtuoso | artist | Amphitheater, Shakespeare's Theater, Mausoleum of Mausolos, Eiffel Tower, Guidestones | Masterwork: 400 history points to the city | Resident Virtuoso: +3 history, +25% luxury, +2 Virtuoso points |
| Great Oracle | prophet | Temple, Cathedral, Temple of Artemis, Michelangelo's Chapel, J.S. Bach's Cathedral, Altar to The Divine Ruler | Found the Sanctum (one per civ) | Resident Oracle: 2 unhappy made content, +2 Oracle points |
| Great Commander | general | Statue of Zeus, Sun Tzu's War Academy; slice 6 adds combat | Drill the stack: every own unit on the tile gains one veteran level | Resident Commander: `Veteran_Build` +1 in the city, +2 Commander points |
| Great Spymaster | spy | Courthouse, Police Station, Statue of Liberty, Women's Suffrage, United Nations | None of its own: it is a strong diplomat (embassy, investigate, incite) | Resident Spymaster: `Spy_Resistant` 50, `Incite_Cost_Pct` 100, +2 Spymaster points |

Unit data, shared by all seven: class Land, `build_cost 240`, attack 0, defense 0, hp 10, firepower 1,
`move_rate 2`, `vision_radius_sq 2`, all upkeep 0, `pop_cost 1` (what "Join City" adds), `tech_req "None"`,
flags `NonMil`, `NoVeteran`, `NoBuild`, `Unbribable`, `AddToCity`, plus the user flag `GreatPerson`; the Builder
adds `HelpWonder`, the Spymaster `Diplomat`. `NoBuild` is the engine flag the Barbarian Leader uses
(`common/unittype.h:254-255`; `civ45/units.ruleset:3055-3078` is the template). Flag budget: civ45 defines 26
user unit flags, the roster adds 8 and this note 1, and the ceiling is 50 (`common/unittype.h:331-332`).

The 240 shields: Pyramids cost 200, Great Library 300, Hoover Dam and Apollo Program 600 (`civ45/buildings.ruleset`,
`build_cost` of each), so one Builder finishes an ancient wonder and does a third of a modern one. With the -50%
value at Invention (units-and-upgrades.md 1) not applying to "Help Wonder", the number is exact.

## 3. Points and births

| Rule | Value | Where |
|---|---|---|
| Points per turn per city | Sum of `User_Effect_3` in the city: 1 for a tier-1 building (Temple, Library, Marketplace, Amphitheater, Courthouse), 2 for tier 2 (University, Bank, Cathedral, Factory, Police Station), 3 for tier 3 (Research Lab, Stock Exchange, Mfg. Plant), 2 for every wonder in section 2, 2 for every Resident | `effects.ruleset`, one row per building |
| Multiplier | `User_Effect_4` percent: Golden Age +100 (section 5); nothing else at first | `effects.ruleset` |
| Pool | `fc45_gp_pool_<city id>`, grows by rate × (100 + pct) / 100 each `turn_begin`; reset to 0 at a birth; dropped when the city is destroyed (`city_destroyed` is already handled at `civ45/script.lua:19-25`) | `script.lua` |
| Threshold | `150 + 75 × fc45_gp_born_<player id>`: 150, 225, 300, ... with no cap | `script.lua` constants `FC45_GP_BASE 150`, `FC45_GP_STEP 75` |
| Kind | Draw one kind with probability equal to its share of the city's points, from the Lua table `fc45_gp_sources = { ["Library"] = {"sage", 1}, ... }` that mirrors the effect rows | `script.lua` |
| Birth | `edit.create_unit(owner, city.tile, find.unit_type("Great " .. kind), 0, city, 2)` plus `notify.event(owner, city.tile, E.UNIT_BUILT, ...)` (the `E.SCRIPT` form is at `civ45/script.lua:32`) and a `fc45_gp_born` increment | `script.lua` |
| First to a tech | `tech_researched(tech, player, reason)` (`script_server.c:483-485`): if `fc45_gp_first_<tech rule name>` is unset and `reason == "researched"`, set it to the player id and create the kind: Philosophy → Sage, Theology → Oracle, Economics → Magnate, Electricity → Builder (all four in tech-tree.md, eras II, III, IV and V) | `script.lua` |
| Commander from combat | Slice 6 (roadmap row 6) adds `fc45_gp_combat_<player id>` from `action_finished_unit_units`; when it passes `FC45_GP_COMBAT 30` a Commander is born in the capital. Not part of this slice. | later |

Pace check (derived): a city with Temple and Library makes 2 a turn, so its first great person takes 75 turns; add
one wonder and it is 38; a mid-game city with Library, University, Marketplace, Bank, Temple and Amphitheater
makes 8 a turn and, with four births already behind the player, needs 450 ÷ 8 = 57 turns. Expect 3 to 6 great
people per player per game without wonders, 8 to 12 with them. The reference pace is in mechanics.md 2.9; these
numbers are Freeciv45's own and are the first thing to tune.

The effect rows and the Lua table carry the same numbers twice. The test plan (section 7) has a check that diffs
them; the alternative, a single source, is open question 1.

## 4. Uses

Every great person has three choices: settle (4.1), its deed (4.2), or pledge a golden age (5). All three
consume the unit.

### 4.1 Settle: "Join City" and the Resident buildings

The native "Join City" enabler already needs `AddToCity`, not `Foreign` and a move left
(`civ45/actions.ruleset:1376-1382`); the unit's `pop_cost 1` becomes a citizen. Seven more enablers, one per
kind, add a `target_reqs` row `"Building", "Resident <Kind>", "City", FALSE` so a city holds at most one
Resident of each kind. Lua does the rest:

```lua
function fc45_gp_join(action, actor, city)
  if action:rule_name() ~= "Join City" or not actor.utype:has_flag("GreatPerson") then return end
  local kind = fc45_gp_kind_of_unit[actor.utype:rule_name()]      -- "Great Sage" -> "Sage"
  edit.create_building(city, find.building_type("Resident " .. kind))
end
signal.connect("action_started_unit_city", "fc45_gp_join")
```

Resident buildings: genus `Improvement`, `build_cost 1`, `upkeep 0`, `sabotage 0`, and a `reqs` row
`"MinYear", "9999", "World"` so no city can build or buy one. `edit.create_building` adds it regardless
(section 1). Whether a building whose `reqs` are not met keeps its effects is **unverified**; test 4 covers it,
and the fallback is `obsolete_by` left empty plus a `"Nation", "Barbarian", "Player"` requirement.

| Building | Effects (all `Building <name> City` reqs) |
|---|---|
| Resident Sage | `Output_Bonus` 25 science; `User_Effect_3` 2 |
| Resident Builder | `Output_Inc_Tile` 3 shield with `CityTile Center Tile`; `User_Effect_3` 2 |
| Resident Magnate | `Output_Inc_Tile` 3 trade with `CityTile Center Tile`; `Output_Bonus` 25 gold; `User_Effect_3` 2 |
| Resident Virtuoso | `History` 3; `Output_Bonus` 25 luxury; `User_Effect_3` 2 |
| Resident Oracle | `Make_Content` 2; `User_Effect_3` 2 |
| Resident Commander | `Veteran_Build` 1; `User_Effect_3` 2 |
| Resident Spymaster | `Spy_Resistant` 50; `Incite_Cost_Pct` 100; `User_Effect_3` 2 |

Each Resident feeds its own kind, so a city that settles Sages breeds Sages. Residents are lost with the city and
are not sold or captured like other buildings only if `sabotage 0` and the capture rules say so (open question 2).

### 4.2 Deeds: "User Action 3"

```
ui_name_user_action_3                = _("%sGreat Deed%s")
user_action_3_target_kind            = "Self"
user_action_3_min_range              = 0
user_action_3_max_range              = 0
user_action_3_actor_consuming_always = TRUE
```

Three enablers: (a) Sage, Virtuoso and Oracle: `UnitFlag GreatPerson`, `UnitType Great Builder FALSE`,
`UnitType Great Magnate FALSE`, `UnitType Great Commander FALSE`, `UnitType Great Spymaster FALSE`,
`CityTile Center Tile TRUE`, `DiplRel Foreign Local FALSE`, `MinMoveFrags 1`; (b) Magnate: the same without the
`Foreign` row, so a foreign city counts; (c) Commander: `UnitType Great Commander`, `MinMoveFrags 1`, anywhere.
The Builder's deed is "Help Wonder" and the Spymaster's are the diplomat actions, both native, so neither has a
"User Action 3" enabler. The handler is one dispatch:

| Kind | Handler on `action_started_unit_self` when `action:rule_name() == "User Action 3"` | Number |
|---|---|---|
| Sage | `edit.give_tech(owner, nil, 0, true, "fc45_great_sage")`: the cheapest tech the player can research (civ45 `free_tech_method`), no bulb penalty | one tech |
| Magnate | `city = actor.tile:city()`; `edit.change_gold(owner, g)` with `g = 100 + 30 × city.size`, doubled when `city.owner ~= owner` | 160 to 1,000 gold |
| Virtuoso | `edit.add_city_history(actor.tile:city(), 400)` | 400 history, 5% of the 8,000-point culture win in victory.md |
| Oracle | `edit.create_building(actor.tile:city(), find.building_type("Sanctum"))`: a `SmallWonder` with `Make_Content` 1 in every city (`Building Sanctum Player`) and `History` 3; a second Oracle moves it | one per civ |
| Commander | for each own unit `u` on `actor.tile` other than the actor: `u:transform(u.utype, -1)`; a negative loss raises the level and clamps at the type's top level (`api_server_edit.c:76-88`, observed; in-freeciv.md 4.2 row 1 uses the same call) | +1 level each |
| Builder | native "Help Wonder": full 240 shields | see section 2 |
| Spymaster | native: "Establish Embassy Stay", "Investigate City" and "Incite City" through the `Diplomat` flag (`civ45/actions.ruleset:973-981` for incite); it needs an embassy enabler row for `UnitFlag Diplomat` beside the Explorer-only one at `:681-690` | native costs |

"Disband Unit Recover" would let any great person put 120 shields into anything; add `"UnitFlag", "GreatPerson",
"Local", FALSE` to its enabler so the Builder's deed stays the only shield use (open question 3).

## 5. Golden ages: "User Action 4" and a timed small wonder

```
ui_name_user_action_4                = _("%sPledge a Golden Age%s")
user_action_4_target_kind            = "Self"
user_action_4_min_range              = 0
user_action_4_max_range              = 0
user_action_4_actor_consuming_always = TRUE
```

One enabler: `UnitFlag GreatPerson`, `MinMoveFrags 1`. The handler adds one to `fc45_golden_pledges_<player id>`;
when pledges reach `1 + fc45_golden_count_<player id>` (the first age costs one great person, the second two, the
third three) the age starts: pledges reset, count increments, `fc45_golden_until_<player id> = turn + 10`, and
`edit.create_building(capital, find.building_type("Golden Age"))` where the capital is the first city with the
Palace (`Player:cities_iterate` at `tolua_game.pkg:733`). `turn_begin` removes the building when
`turn >= fc45_golden_until` and clears the global. If the player has no city the pledge is refused with a notice.

| "Golden Age" building | Effects, all with `Building "Golden Age" Player` |
|---|---|
| genus `SmallWonder`, `build_cost 1`, `reqs MinYear 9999 World` | `Output_Inc_Tile` 1 shield on tiles with at least 1 shield (`output_granularity 1`, `civ45/game.ruleset:203`); `Output_Inc_Tile` 1 trade on tiles with at least 1 trade; `User_Effect_4` 100; `No_Anarchy` 1 |

The reference game's rule that later ages need great people of different kinds is dropped (mechanics.md 2.9);
pledges of any kind count. A conquered capital takes the building with it, which ends the age early and is
accepted; `turn_begin` tolerates a missing building.

## 6. The AI gap and the auto-use rule

The AI never chooses "User Action 3" or "4" and never joins a city (section 1), so without help every AI great
person would stand in its birth city forever, except a Builder, which the native AI already walks to a wonder
(`daicity.c:462-472`), and a Spymaster, which `dai_manage_diplomat` runs (`daiunit.c:2765`). The mitigation is a
`turn_begin` pass over every player where `not p:is_human()`, over `p:units_iterate()` (`tolua_game.pkg:728`),
for units with the `GreatPerson` flag, calling `edit.perform_action(unit, find.action(name))`
(`tolua_server.pkg:237-238` for the self form, `:219-220` for the city form), so the AI goes through the same
enablers and handlers as a human:

| Order | Condition | Action |
|---|---|---|
| 1 | No golden age running and live great people ≥ pledges still needed | Pledge with each of them ("User Action 4") |
| 2 | Sage, Virtuoso | Deed in the birth city ("User Action 3") |
| 3 | Magnate | Deed where it stands (Lua has `edit.unit_move` at `tolua_server.pkg:210` but no pathing, so it never walks to a bigger or foreign city) |
| 4 | Oracle, Commander | Settle where it stands ("Join City") when no Resident of that kind is there, else deed |
| 5 | Builder | Leave it to the native AI for 10 turns (`fc45_gp_born_turn_<unit id>`), then settle |
| 6 | Spymaster | Leave it to `dai_manage_diplomat`; settle after 20 turns |

`perform_action` returns false when an enabler blocks the action, and the rule falls through to settling. The
rule costs the AI nothing to understand: every outcome is a building, gold, a tech or culture, which the default
AI values through effects (in-freeciv.md 4.1 valuation column). What it cannot do is plan around great people,
and that is the accepted gap (mechanics.md question 10).

## 7. Test plan

Each test runs on the stock server with civ45 loaded; Lua tests go through `/lua cmd` on a test save.

| # | Checks | How | Expect |
|---|---|---|---|
| 1 | Points mirror | A 20-line Python check that parses the `User_Effect_3` rows of `effects.ruleset` and the `fc45_gp_sources` table of `script.lua` and diffs building names and values | identical sets |
| 2 | Rate | Found a city, `/lua cmd edit.create_building(c, find.building_type("Library"))`, read `effects.city_bonus(c, "User_Effect_3")` | 1; 3 after a University |
| 3 | Birth | Set `fc45_gp_pool_<id>` to 149, end turn | a Great Sage on the city tile, pool 0, `fc45_gp_born_<pid>` 1, next threshold 225 |
| 4 | Settle | "Join City" with the Sage | city size +1, Resident Sage present, +25% science in the city dialog, a second Sage cannot join (enabler) but can do its deed |
| 5 | Deeds | One of each kind in a size-5 city: Sage, Magnate, Virtuoso, Oracle | a new tech with bulbs unchanged; 250 gold (500 in a foreign city); city history +400 in `city:culture()`; Sanctum present and +1 content in a second city |
| 6 | Builder | A Builder next to a city building Pyramids with stock 0: "Help Wonder" | stock 240, wonder completes next turn |
| 7 | Commander | Two Warriors on a tile with the Commander, deed | both one level higher; a Veteran-top unit unchanged |
| 8 | Golden age | Pledge once | "Golden Age" in the capital, a mined hill shows +1 shield, `fc45_golden_until` = turn + 10; removed 10 turns later; second age needs two pledges |
| 9 | Persistence | Save and load mid-pool and mid-age | pools, counts and `until` survive (scalars only) |
| 10 | AI | A 100-turn autogame with two AI players and a `log` call in the auto-use rule | every AI great person is spent within 20 turns of birth; no Lua error in the server log |
| 11 | Regression | Existing sandbox User Actions 1 and 2 and their `User_Effect_1`/`_2` rows still fire (the slot numbers do not collide) | `civ45/script.lua:474-528` handlers unchanged |

## 8. Open questions for John

1. The point numbers live twice, in effect rows and in the Lua table. Keep both with the diff check, or make
   Lua the single source and drop `User_Effect_3` (then the plan's "through the blank User_Effect slots" is only
   true of the multiplier)?
2. Residents: lost on capture like other buildings, or should Lua re-create them for the new owner (a settled
   Sage would then change sides)?
3. Should great people keep "Disband Unit Recover" (120 shields into anything, for every kind) as a weak fourth
   use, or is the Builder's "Help Wonder" the only shield use?
4. Golden age pledges count any kind. Keep that, or require different kinds as the reference game does (needs
   seven more scalar globals per player)?
5. The Spymaster has no deed of its own and leans on native diplomat actions. Accept that, or spend the slot on
   a Lua deed such as revealing every rival's capital (which needs an API call this note has not found)?

## 9. Implementation order

1. `units.ruleset`: user flag `GreatPerson`; seven unit types from the section 2 block.
2. `buildings.ruleset`: seven Residents, Sanctum, Golden Age (section 4.1, 4.2 Oracle row, section 5).
3. `effects.ruleset`: `User_Effect_3` rows for every building in section 2 and every Resident; `User_Effect_4`
   100 and the three Golden Age rows; the Resident and Sanctum effects.
4. `actions.ruleset`: "User Action 3" and "4" definitions; the three deed enablers and the pledge enabler; seven
   "Join City" enablers; the embassy enabler row for `UnitFlag Diplomat`; the "Disband Unit Recover" exclusion.
5. `script.lua`: `fc45_gp_sources`, `fc45_gp_kind_of_unit`, `fc45_gp_turn(turn, year)` (pools, births, golden
   age expiry, AI auto-use), `fc45_gp_join`, `fc45_gp_deed(action, actor)`, `fc45_gp_pledge`, `fc45_gp_tech(tech,
   player, reason)`; `signal.connect` for `turn_begin`, `action_started_unit_city`, `action_started_unit_self`,
   `tech_researched`; the `city_destroyed` handler at `civ45/script.lua:19` clears the pool.
6. `scripts/gp-points-check.py` for test 1; `README.civ45` entry; `patches/` entry for the slice.
