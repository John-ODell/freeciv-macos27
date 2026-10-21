# Freeciv45 resource happiness and health, first version

Roadmap slice 4 of [freeciv45-plan.md](../../freeciv45-plan.md) ("Happiness and health from resources") and part 4,
fourth slice, of [standalone.md](../standalone.md) (issue 276), made concrete. The reference behaviour is
[mechanics.md](../mechanics.md) 2.2 (luxuries add happiness, food resources add health, a resource counts for every
city once the nation reaches it) and 2.4 "Health and happiness caps". It uses the marker pattern of
[religion.md](religion.md) section 4.3: a hidden small wonder per player, kept in the capital by Lua, carrying
native effects the AI can see. Engine paths are the patched tree at patch 0051 (religion);
`civ45/...` is `data/civ45/...` there.

## 1. What it does in play

- **Every luxury resource inside your borders makes one citizen content in every city**, once per kind: two Wine
  tiles count once, Wine and Silk twice.
- **Every food resource inside your borders raises every city's size cap by one and its health (plague
  resistance) by 5 percent**, once per kind.
- The rest (Iron, Horses, Coal, Oil, Peat, Resources) stay as they are: tile output and, for the first four, unit
  requirements.

What that changes: a nation is happier and grows bigger for holding many kinds of resource, not many copies of
one, so expanding towards a new luxury, or taking a neighbour's, has a reason beyond the tiles' own yield. The size
cap matters from the start: civ45's cap is 8 without an Aqueduct and 16 with one (`civ45/effects.ruleset`,
`[effect_aqueduct_base]`, `[effect_aqueduct]`), so three food kinds let cities reach 11 before an Aqueduct.

## 2. The families

From civ45's 21 resources (`civ45/terrain.ruleset`, `[extra_gold]` to `[extra_oil]`, and the `resources` lists of
each terrain):

| Family | Resources | Effect per kind reached |
|---|---|---|
| Luxury (8) | Gold, Gems, Silk, Wine, Spice, Furs, Ivory, Whales | `Make_Content` 1 in every city |
| Food (7) | Wheat, Buffalo, Fruit, Pheasant, Game, Fish, Oasis | `Size_Adj` 1 and `Health_Pct` 5 in every city |
| Other (6) | Iron, Horses, Coal, Oil, Peat, Resources | unchanged |

The reference also has copper, stone, marble, aluminium and uranium; civ45 has none of them, and adding resources
is a map and art job of its own (plan row 4).

## 3. What "reached" means

**A resource counts when its tile is inside your borders** (`tile.owner` is you). The reference also asks for the
right improvement and a road, river or coast link to your cities (mechanics.md 2.2). This version leaves both out:

- the AI would not plan for them (it builds roads and improvements for its own reasons, not to link a resource),
  so a human would gain an edge the AI can't answer;
- borders already grow from cities and culture, so a resource inside them is one a city can work;
- a link check is a path search per resource per turn in Lua, the turn-start cost the plan names as the risk.

A later version can add the improvement (a Mine for Gold and Gems, Irrigation for Wheat) with one extra check per
tile.

## 4. What the engine gives and what Lua must do

| Need | How | Evidence |
|---|---|---|
| A nation-wide effect from a tile | Not native: an `Extra` requirement reaches at most TradeRoute range | plan row 4; `doc/README.effects` |
| A Player-range effect Lua can switch | A hidden small wonder `<Resource> Supply` per resource, created and removed in the capital, as the state faith (religion.md 4.3) | `edit.create_building`, `edit.remove_building` at `tolua_server.pkg:149-152` |
| Which resources a player holds | `whole_map_iterate()` once a turn; for each tile with an owner, `tile:has_extra(name)` for the 15 resources | `tolua_game.pkg:371-372` |
| The AI sees the gain | `Make_Content`, `Size_Adj` and `Health_Pct` are all native and weighed by the AI (`ai/default/daieffects.c:238, 308, 393`); the markers can't be built, so the AI only lives with them |

No Lua record is needed: the markers are recomputed from the map every turn, and the map is in the save.

## 5. Rules

Each `turn_begin`:

1. For every civ, the set of kinds held: one pass over the map, owned tiles only.
2. In each civ's capital, every `<Resource> Supply` the set says is created; every one it no longer says is
   removed (also from any other city, after the capital moves). A civ with no capital holds none.
3. A change is told to the player: "Your nation now has Wine: 1 more content citizen in every city." and "Your
   nation has lost its Wine."

## 6. Data

| Building (15) | Genus | Can be built | Effects (`Building <R> Supply Player`) |
|---|---|---|---|
| `Gold Supply` ... `Whales Supply` (8) | SmallWonder | no (`MinYear 9999 World`) | `Make_Content` 1 |
| `Wheat Supply` ... `Oasis Supply` (7) | SmallWonder | no | `Size_Adj` 1; `Health_Pct` 5 |

Graphic: `b.<r>_supply`, alt `b.marketplace` for luxuries and `b.granary` for food. With religion's 16 the ruleset
has 135 buildings of the 200 allowed (`common/fc_types.h:43`).

## 7. Test plan

A rules test like the religion one (`scripts/civ45-religion-test.sh`):

| # | Case | Expect |
|---|---|---|
| 1 | Put Wine and Silk in the Tester's borders, and a second Wine | next turn: `Wine Supply` and `Silk Supply` in the capital, no other luxury marker; `Make_Content` in a second city up by exactly 2 |
| 2 | Put Wheat and Fish in its borders | `Wheat Supply` and `Fish Supply`; `Size_Adj` in a city up by 2 and `Health_Pct` by 10 |
| 3 | Remove the Silk | next turn: `Silk Supply` gone, `Make_Content` down by 1 |
| 4 | A luxury outside every border | no marker |
| 5 | Turn-start time | the server log's turn time with and without the script on a size-110 map (the balance games' map) |

Results (2026-10-21, `scripts/civ45-supply-test.sh` on fork patch 0052): cases 1 to 4 pass, 12 checks in all.
- The capital holds exactly Buffalo, Silk, Wheat and Wine Supply.
- A second city gets content +2, size cap +2 and health +10.
- Removing the Silk takes its marker away and leaves content +1.
Case 5, turn-start time, wasn't timed; a 475-turn balance game with the script took 1,099 to 1,486 s, against 829
to 1,868 s without it.

Balance games: seeds 7 and 13 with religion, resources and cottages together (table in
[cottages.md](cottages.md), section 6).
- Each civ holds about 6 to 8 kinds (63 to 77 kinds held across the ten civs).
- Average city size at turn 475 (seed 7): 6.1 before, 8.0 after.
- Unhappy citizens at turn 150 (seed 7): 45 before, 11 after.
- Plague counts weren't measured.

## 8. Later

- The improvement and link requirement (section 3).
- Trading a spare resource to another civ through diplomacy: the treaty clause list is fixed in C
  (`common/diptreaty.h`), so this is engine work.
- The missing resources (section 2).
