# Civ4/5 direction: what rulesets can already do vs what needs engine work

Date: 2026-10-16. Source tree: `refs/freeciv-S3_2` (3.2.6+, commit 44e6898c).
Labels per the brief: **observed** (read in the cited file), **derived**
(follows from observed facts), **inferred** (plausible, not checked),
**unknown**.

Freeciv's design splits into three layers, and the menu below is grouped by
the lowest layer a Civ4/5 feature needs:

- **Tier A, ruleset only.** `.ruleset` files under `data/<ruleset>/`
  (`game`, `units`, `buildings`, `techs`, `governments`, `effects`,
  `actions`, `terrain`, `cities`, `nations`). 133 effect types
  (`doc/README.effects`) attached to requirement vectors whose types are
  listed at `doc/README.effects:58-119`. Everything here ships as data; the
  stock `sandbox` and `civ2civ3` rulesets are the reference examples.
- **Tier B, ruleset + Lua.** Server-side Lua 5.4 (`script.lua` per ruleset)
  reacting to signals created in `server/scripting/script_server.c:424-574`
  and acting through the `edit.*` API
  (`server/scripting/api_server_edit.h`). Good for events, one-off rules and
  anything "when X happens, do Y"; bad for per-turn economy math and for
  anything the AI must understand.
- **Tier C, engine.** C changes in `common/`, `server/` and all four
  clients, plus AI (`ai/default`). Needed when the feature is a new game
  concept the data model has no slot for.

## Tier A: already expressible in a ruleset

| Civ4/5 feature | Freeciv mechanism | Citation | Label |
|---|---|---|---|
| Hex map | `topology` server setting includes `HEX`; civ2civ3 ships `ISO|HEX`; hex tilesets exist (`hexemplio`, `hex2t`, `isophex`, `toonhex`) | `server/settings.c:1557`, `data/civ2civ3/game.ruleset:804`, `data/hexemplio.tilespec:36-38` | observed |
| Culture (Civ4 city culture, Civ5 culture yield) | `History`, `National_History`, `Performance`, `National_Performance` effects; `[culture]` section with victory threshold, interest, migration weight | `doc/README.effects:406,516,520,590`, `data/civ2civ3/game.ruleset:380-393` | observed |
| Cultural victory | `culture` victory condition in `victories` bitwise setting plus `[culture] victory_min_points` | `server/settings.c:2648`, `common/fc_types.h:1275`, `data/civ2civ3/game.ruleset:380-385` | observed |
| Borders that grow with culture | `borders` setting, `Border_Strength_Pct`, `Border_Vision` | `server/settings.c:2458`, `doc/README.effects:221-228` | observed |
| Larger / tech-dependent city radius (Civ4 fat cross, Civ5 3-ring) | `init_city_radius_sq` plus `City_Radius_Sq` effect with Tech or Building reqs | `data/civ2civ3/game.ruleset:108`, `doc/README.effects:304` | observed |
| Social policies / civics sliders (Civ4 civics, Civ5 policies) | Governments (`governments.ruleset`, 9 in civ2civ3) plus **multipliers**: player-adjustable policy values that scale any effect via `multiplier = "..."` on the effect | `data/goldkeep/governments.ruleset:246-260`, `data/goldkeep/effects.ruleset:441-452` | observed |
| Unique units and buildings per civ | `Nation` / `NationGroup` requirement at Player range on unit, building or effect reqs | `doc/README.effects:79-80`, `data/alien/nation_effects.ruleset:19-28` | observed |
| Strategic and luxury resources | Extras with `Extra` requirement at `City` range on unit/building build reqs (Civ4 "needs Iron") | `doc/README.effects:70` | derived |
| Trade goods / trade routes with resource types | `[goods_*]` sections, `Establish Trade Route` and `Enter Marketplace` actions, `Max_Trade_Routes`, `Traderoute_Pct` | `data/sandbox/game.ruleset:664-698`, `doc/README.effects:488,712` | observed |
| Unit promotions (linear) | `[veteran_system]`: named levels, raise chances, power and move bonuses | `data/civ2civ3/units.ruleset:70-75` | observed |
| Ranged / bombard attacks | `Bombard` action, `bombard_rate`, `bombard_max_range` (shipped value 1), `Combat_Rounds` effect | `data/sandbox/actions.ruleset:164,1202-1232`, `data/sandbox/units.ruleset:448,1752`, `doc/README.effects:324` | observed |
| Civ5 ranged units (attack at range 2 and can kill) | `Bombard Lethal` action: "can kill target units", own `bombard_lethal_max_range`; shipped rulesets leave it at range 1 and unused | `doc/README.actions:811-820`, `data/sandbox/actions.ruleset:185` | observed; AI use unknown |
| One unit per tile (Civ5 1UPT) | `Unit Move` is an enabler-controlled action; a target req `MaxUnitsOnTile 0 Tile` blocks moves into occupied tiles (done in civ45, see "Slice 1 results"). Units built in a city still stack there | `data/sandbox/actions.ruleset:2818-2823,1675`, `doc/README.effects:106,903-910`, `patches/0003-*.patch` | observed (100-turn autogame) |
| Empire size unhappiness / expansion cost | `Empire_Size_Base`, `Empire_Size_Step`, `Unit_Slots`, `Upkeep_*` | `doc/README.effects:339-345,760` | observed |
| Health (Civ4) | `Health_Pct` effect plus `[civstyle] illness_*` settings | `doc/README.effects:403`, `data/civ2civ3/game.ruleset:209-215` | observed |
| Achievements (Civ5 style) | `[achievement_*]` sections (8 in civ2civ3/sandbox) with culture rewards | `data/civ2civ3/game.ruleset:507-580` | observed |
| Natural disasters, barbarians, animals, huts | `[disaster_*]`, barbarian nations, `Animal Kingdom` nation, hut actions | `data/civ2civ3/game.ruleset:446-482`, `data/nation/animals.ruleset:28` | observed |
| Espionage | ~20 `Spy *` / `Steal *` / `Sabotage *` actions with escape variants | `data/sandbox/actions.ruleset` (enabler list) | observed |
| Tech tree, tech cost styles, leakage, upkeep | `techs.ruleset` (87 advances in civ2civ3), `tech_cost_style`, `tech_leakage`, `tech_upkeep_style` | `data/civ2civ3/game.ruleset:339-378` | observed |
| Casus belli / diplomatic incidents | `Casus_Belli_Success`, `Casus_Belli_Caught`, `Casus_Belli_Complete` | `doc/README.effects:252,272,281` | observed |
| Counters (Civ4 "turns since X" rules) | `[counter_*]` with `Owned`, `Celebration`, `Disorder` types usable as City-range reqs | `data/sandbox/game.ruleset:823-850`, `doc/README.effects:62` | observed |

## Tier B: ruleset plus Lua

| Civ4/5 feature | Approach | Citation | Label |
|---|---|---|---|
| Great People (Civ4) | No engine concept. Emulate: counters or `Performance` thresholds trigger `edit.create_unit` of a "Great Engineer" unit type whose only enablers are `Help Wonder` / `Join City` / a `User Action`; `building_built`, `turn_begin` signals | `server/scripting/script_server.c:424-458`, `api_server_edit.h` (create_unit, perform_action_*) | derived |
| Golden ages | Celebration (`rapture`) already exists; Lua on `turn_begin` can grant `Output_Bonus` via a temporary building and remove it later | `doc/README.effects:609` (Rapture_Grow), `edit.create_building/remove_building` | derived |
| Culture flipping (Civ4) | `Migration_Pct` (`doc/README.effects:495`) plus Lua `edit.transfer_city` when a city's `MinForeignPct` / culture test fires on `turn_begin` | `doc/README.effects:103-104`, `api_server_edit.h` (transfer_city) | derived |
| Scripted events, quests, tutorial, Civ5-style "notifications" | Signals plus `notify.event`, `tile_set_label` | `script_server.c`, `api_server_edit.h` | observed |
| City-states (Civ5), partial | Nations with an AI trait and Lua that blocks their expansion (`unit_cant_be_built`, `city_built` → `remove_city`) and hands out gifts on `turn_begin`. The diplomacy and influence mechanic has no slot | `data/nation/*.ruleset` traits, `script_server.c:444-466` | inferred |
| Promotion choice on level-up | Lua on `unit_lost`/`action_finished_*` can `unit_transform` to a chosen variant type; a UI to choose does not exist | `api_server_edit.h` (unit_transform) | derived; UI unknown |

## Tier C: needs engine (C) changes

| Civ4/5 feature | Why the engine is in the way | Citation | Label |
|---|---|---|---|
| Religion (Civ4 founding/spread, Civ5 beliefs) | No religion type, no per-city religion state, no spread rules; closest slots are goods (one per trade route) and extras (per tile). New common struct, netcode, savegame, client dialogs, AI | `common/` has no religion; `data/` and `doc/` have no match for "religion" (grep) | observed absence |
| Great People as a real system (points per city, named greats, specialist-driven) | Needs per-city accumulators per GP type and a player-wide pool; counters are per-city scalar only | `data/sandbox/game.ruleset:823-850` | derived |
| Civ5 global happiness and single-pool luxury | Freeciv happiness is per city (`Make_Content`, `Martial_Law_*`, `Unhappy_Factor`); a nation-wide pool changes `server/cityturn.c` and every city dialog | `doc/README.effects:453-466,724` | observed |
| Promotion trees (branching perks per unit) | `[veteran_system]` is one linear ladder per unit type | `data/civ2civ3/units.ruleset:70-75` | observed |
| Ranged combat the AI plays well, city ranged strike | Range and lethal bombard are data (Tier A row above); the AI using them and cities shooting back are not | `data/sandbox/actions.ruleset:164,185` | derived; AI inferred |
| 1UPT the AI can actually play | Rule is Tier A, but the default AI's path and stack logic assumes stacking; without AI work 1UPT games are human-only | `ai/default/` | inferred |
| City-state diplomacy, influence, quests | No minor-civ player kind, no influence score, no diplomacy UI for it | `common/player.h`, client diplomacy dialogs | derived |
| Civ5 one-building-per-tile wonders / tile improvements with yield adjacency | Extras have adjacency reqs, so partial in Tier A; wonders occupying map tiles need engine | `doc/README.effects:70-72` | derived |
| Hex-first UI (Civ5 feel: zoom, unit cycling, 1UPT movement arrows) | Client work in `client/gui-qt`; the hex rendering exists, the interaction model does not | `client/gui-qt/` | inferred |
| Vassals / Civ4 corporations | No slot at all | grep of `doc/` and `common/` | observed absence |

## Recommendation

1. **Start in Tier A as a new ruleset** (`data/civ45/` in `port/freeciv`, copied
   from `sandbox` because it already enables actions, goods, counters and
   achievements): hex topology, 3-ring culture-driven city radius,
   multiplier-based policies, unique units/buildings, strategic resources,
   bombard with range 2, culture victory. This is playable and testable
   with the existing autogame script and needs no C.
2. **Add Tier B Lua** for Great People, golden ages and culture flipping once
   the ruleset plays. Each is one signal handler.
3. **Pick one Tier C item** only after that, with religion or global happiness
   as the candidate, because both are self-contained server mechanics with a
   small client surface compared with 1UPT-aware AI.

## Slice 1 results (2026-10-16, `data/civ45`, patch 0003)

civ45 is sandbox plus: hex topology, 1UPT on regular moves, culture-driven `City_Radius_Sq`
(+4 at 300 culture, +4 at 1500), `victories` with CULTURE, `bombard_max_range = 2`, Legion needs Iron
and Armor needs Oil at City range, Aztec Jaguar Warrior, Persian Immortal, Arab Bazaar.

100-turn autogame, 10 AIs, seeds 42/42, release Qt build, data read from the source tree
(`scripts/test.sh --ruleset civ45 --no-client`, log `logs/test-qt-20261016-130853`), compared with the
default-ruleset run from the morning (`logs/test-qt-20261016-074609`). Counted with `scripts/check-stacking.py`
on the turn-101 saves; transported units are skipped.

| | default ruleset | civ45 |
|---|---|---|
| cities at T101 | 64 | 61 |
| units | 224 | 263 |
| tiles with >1 unit outside cities | 11 | **0** |
| tiles with >1 unit in cities | 18 | 19 |
| wall time | about 30 s | 30 s |

Observed: the move rule holds for every unit on the map, including boats, and the AI still founds cities at the
same rate and ends the game with more units. Units stack inside cities because production places them there and
nothing moves them out; Civ5 handles that with a city garrison slot, which Freeciv lacks (Tier C if wanted).
Not observed: how often the AI's chosen moves were rejected (the server does not log it), AI behaviour in wars
past turn 100, and whether the extra units are defenders the AI cannot route. One foreign Settlers sat inside
another player's city at T101; cause not investigated.

## Slice 2 results (2026-10-16, patch 0004): one unit per tile in cities too

Slice 1 left units stacking inside cities, because production places units there (issue 25). Slice 2:

- `script.lua` resolves a unit built in an occupied city at once: the better defender stays (city owner's
  unit, then military, then `DefendGood`/`DefendOk` role, then build cost, then veterancy, then age), the
  other unit moves to the nearest free tile. A sweep at every turn start does the same for anything else
  (start units, huts, barbarians, captures, airlifts, paradrops, units unloaded in port).
- Search order for a free tile: own or unowned land within 3 tiles, then within 7, then foreign land
  within 3 that the server's teleport check accepts (it refuses peace-treaty territory and non-allied
  cities, `common/movement.c:818-881`).
- New unit flags: `StacksAnywhere` on aircraft, helicopters and missiles (never counted, may move onto
  occupied tiles); `StacksInPort` on ships (not counted on city tiles, may enter occupied cities).
  Landing from a transport now needs an empty tile like any other move.
- Known limit: the move rule's `MaxUnitsOnTile` counts every unit, so a parked ship or aircraft keeps a
  land unit out of its city. Units built there still appear inside. A class-aware tile limit is engine work.

Autogames, 10 AIs, seeds 42/42, data from the source tree, counted with
`scripts/check-stacking.py --ruleset port/freeciv/data/civ45` (exemptions applied) on the final save:

| | default ruleset T101 | civ45 slice 1 T101 | civ45 slice 2 T101 | civ45 slice 2 T201 |
|---|---|---|---|---|
| cities | 64 | 61 | 64 | 99 |
| units | 224 | 263 | 259 | 412 |
| stacked tiles outside cities | 11 | 0 | 0 | 0 |
| stacked city tiles | 18 | 16 | 0 | 1 |

Logs: `logs/test-qt-20261016-143625` (100 turns, 28 s) and `logs/test-qt-20261016-144233` (200 turns, 98 s).
Over the 200 turns the production handler relocated 216 units and found no room once; the turn sweep
relocated 20 start units on turn 1 and later found no room 11 times, all from turn 190, all in the
crowded interior of one AI (the T201 stack is a Diplomat beside a Phalanx in its city). A first version
that searched only own land within 3 tiles found no room 545 times and left 5 city stacks at T201.
No Lua errors in either log.

The autogames never reach aircraft and have no human player, so `scripts/civ45-rules-test.sh` checks the
rest directly (observed, `logs/civ45-rules-20261016-150*`): a 40-turn game with one human-controlled player,
and at turn 12, at a coastal city, eleven cases through the real `Unit Move` enablers and the sweep. A land
unit is kept out of an occupied city; a Fighter and a Destroyer may enter; a Destroyer is kept off an
occupied ocean tile; the sweep keeps one land unit, the fighter, the ship and the better defender; a human
player's stacked unit is relocated with its message. All 11 pass. A copy of civ45 without the two exemption
enablers fails the four aircraft and ship cases, so the test discriminates. The human case found a bug no
autogame could: the message called `link()`, which the 3.2 Lua API does not have (it is `link_text()`,
`common/scriptcore/tolua_game.pkg:326-327,385-386`), so each relocation of a human player's unit raised a
Lua error and cut that turn's sweep short. Fixed in patch 0004 (fork commit 7913d4b).

## Not checked

- AI move rejections under 1UPT are not logged by the server, so the count asked for in issue 20 is
  not available without a server patch; the autogame outcome above is the evidence.
- Multiplier UI in the Qt client (sliders exist in 3.2 per the
  `goldkeep` ruleset shipping them): unverified on our build.
- Lua performance with per-turn handlers over all cities: unverified.
