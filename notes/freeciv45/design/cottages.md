# Freeciv45 cottages, first version

Roadmap slice 5 of [freeciv45-plan.md](../../freeciv45-plan.md) ("Cottages") and part 4, third slice, of
[standalone.md](../standalone.md) (issue 275), made concrete. The reference behaviour is
[mechanics.md](../mechanics.md) 2.3: a cottage grows only while worked, into a hamlet, a village and a town, from 1
to 4 commerce after about 10, 20 and 40 turns of work; Printing and some civics add to grown towns; the choice
between cottage, farm and mine decides what a city is for. mechanics.md already found the two engine pieces this
needs (an extra that appears by itself with a set chance, and "worked by a city" as a tile requirement), so this
slice is ruleset data only: no Lua and no engine change. Engine paths are the patched tree at patch 0052;
`civ45/...` is `data/civ45/...`.

## 1. What it does in play

- Workers can build a **Cottage** on grassland or plains once the nation knows Pottery: +1 trade.
- While a city works the tile, the cottage grows: a **Hamlet** (+2 trade in all) after about 10 turns, a
  **Village** (+3) after about 20 more, a **Town** (+4) after about 40 more. An unworked cottage waits.
- **Printing** adds 1 trade to villages and towns; **Democracy** adds 1 shield to towns.
- A cottage excludes irrigation, farmland and mines. Pillage takes away one stage at a time, top first.

Grassland and plains give no trade of their own in civ45 (`civ45/terrain.ruleset`, `[terrain_grassland]` and
`[terrain_plains]`: `trade = 0`), so away from rivers and roads cottages are where commerce comes from. A city
can farm for growth, mine hills for shields, or cottage its flat land for gold and science, and a grown town is
something to defend: losing it to a raid costs decades.

## 2. What the engine gives

| Need | How | Evidence |
|---|---|---|
| Workers build it | An extra caused by `"Mine"`; the worker's mine job on grassland or plains builds it, since the Mine itself is kept off those two terrains | `causes` and `reqs` of `[extra_mine]` (`civ45/terrain.ruleset`); the job needs the terrain's `mining_time` above 0, so grassland and plains get 5 |
| It grows only while worked | Hamlet, Village and Town have cause `"Appear"`, `appearance_reqs` the stage below on the tile and `"CityTile", "Worked", "Tile"`, and an `appearance_chance` per turn | `server/srv_main.c:1734-1741` (chance out of 10000, each turn, every tile); `CITYT_WORKED` at `common/fc_types.h:549` |
| Its yield | `Output_Add_Tile` 1 trade per stage present | as the hidden resources of patch 0050 |
| Pillage one stage at a time | Every stage has `rmcauses "Pillage"`; each lower stage has `rmreqs` saying the stage above is absent, so only the top can go | `rmreqs` used for removal at `common/extras.c:604-627` |
| Only the top stage draws | `hidden_by` on each lower stage lists the stages above | `terrain.ruleset` header, `hidden_by` |
| Farm, mine or cottage | `conflicts`, which the ruleset loader makes mutual | `server/ruleset.c:3943-3944` |
| The AI | Its workers weigh a job by the tile's output after it, so the cottage's +1 trade is seen (the growth to come is not); hamlets, villages and towns then appear on their own, for the AI as for anyone | (inferred from the worker advisor; unverified in this note) |

## 3. The numbers

| Stage | Trade in all | Grows after | `appearance_chance` |
|---|---|---|---|
| Cottage | 1 | built in 5 worker turns | |
| Hamlet | 2 | about 10 worked turns | 1000 (10 % a turn) |
| Village | 3 (4 with Printing) | about 20 more | 500 (5 %) |
| Town | 4 (5 with Printing, +1 shield under Democracy) | about 40 more | 250 (2.5 %) |

Growth is a chance each turn, not a count, so a town takes 70 worked turns on average and can take much more or
less (mechanics.md 2.3 names this). The reference's Emancipation civic doubles growth; that waits for civics
(issue 274), since an effect can't change `appearance_chance`.

## 4. Art

The tileset needs `tx.cottage`, `tx.hamlet`, `tx.village_stage` (`tx.village` is taken: the hut uses it) and `tx.town`. Until our own
art exists every stage falls back to `tx.village`, which every stock tileset has (the client needs a style for
the graphic or its alt, `client/tilespec.c:4056-4062`), so a cottage looks like a hut at first. Art: a Codex queue
for four props on the 09_map_extras sheet (BK-Art issue 117, run 8); freeciv45iso can use the art pack's spare village and hermit takes
(run 1) in the meantime.

## 5. Test plan

A rules test like the religion one:

| # | Case | Expect |
|---|---|---|
| 1 | The Tester knows Pottery; a Workers on grassland next to its city does the mine job | a Cottage, no Mine; the tile's trade up by 1 |
| 2 | A Workers on hills does the mine job | a Mine, no Cottage |
| 3 | The city works the cottage tile for up to 60 turns | a Hamlet appears (10 % a turn: 99.8 % within 60) |
| 4 | A cottage on a tile no city works, 60 turns | nothing grows |
| 5 | Remove the Hamlet's tile from work, give the tile a Village and a Town by edit, then pillage | the Town goes first, then the Village |
| 6 | Trade of a Town tile with and without Printing | 4 and 5 |

Results (2026-10-21, `scripts/civ45-cottage-test.sh` on fork patch 0053): 15 of 15 checks.
- Cases 1 and 2: grassland gives a Cottage and no Mine; hills give a Mine and no Cottage.
- Case 3: the Hamlet appeared after 14 worked turns.
- Case 4: the unworked cottage didn't grow.
- Case 5: pillage refuses the Village while the Town stands, then takes the Town and leaves the rest.
- Case 6 (Printing) is a plain effect row and isn't in the test.

## 6. Balance games (religion, resources and cottages together)

Seeds 7 and 13, 10 Normal AIs, up to 475 turns, `scripts/test.sh --lua scripts/civ45-combat-log.lua`, compared
with the same seeds without the systems.
- Before: patch 0050, `~/freeciv-builds/qt`.
- After: patches 0051 to 0053 (data only, so the same binary with `--data`).

The figures are world totals from the saves (`score` sections; trade is the score's `bnp`). Cottages counts every
cottage tile; Towns counts how many of them have grown into a town.

| Seed, turn | Techs before | after | Trade before | after | Unhappy before | after | Mean city size before | after | Culture before | after | Cottages (Towns) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 7, T150 | 293 | 305 | 913 | 1,200 | 45 | 11 | 5.5 | 5.8 | 11,170 | 10,282 | 91 (23) |
| 7, T300 | 486 | 474 | 915 | 1,375 | 83 | 21 | 5.6 | 6.8 | 52,585 | 65,594 | 105 (95) |
| 7, T475 | 602 | 616 | 892 | 1,598 | 113 | 66 | 6.1 | 8.0 | 116,536 | 175,947 | 104 (100) |
| 13, T150 | 249 | 368 | 685 | 1,308 | 34 | 12 | 4.5 | 5.5 | 8,963 | 7,839 | 100 (29) |
| 13, T300 | 442 | 647 | 903 | 1,661 | 68 | 44 | 5.3 | 6.8 | 38,403 | 78,998 | 108 (103) |

How the games ended:
- Seed 7 ran to turn 475 both times.
- Seed 13 ended in a culture victory both times: at turn 462 before (Louis XIV), at turn 355 after (Mpande
  kaSenzangakhona).

Logs:
- before: `logs/test-qt-20261020-221249` (7) and `-232856` (13);
- after: `logs/test-qt-20261021-011811` (7) and `-010648` (13);
- first version, with history in every faith city: `-003618` and `-005437`.

What it shows:
- **The AI builds cottages:** about one per city by turn 150, and nearly all are towns by turn 300.
- **Trade rises by half to double.** That speeds research on seed 13 (+46 % techs at turn 300) but not on seed 7,
  where the extra trade goes elsewhere.
- **Cities are happier and bigger,** from the resources and the state faith.
- **Culture victory came about 100 turns sooner on seed 13.** This is the faster economy, not faith history:
  dropping that history took seed 7's culture at turn 300 from 92,827 to 65,594, against 52,585 before. Seed 11
  ended at turn 357 without the systems, so early culture wins already happen. Even so, the pacing (era costs,
  the 30,000-point culture bar) should be retuned with the systems in.
