# Kinder early raids for a lightly defended player (issue 357, patch 0070)

The tester found that with patch 0067 a player keeping one Spearmen in each of three cities on a small island map lost all three by turn 62 (issue 357). John asked to make the early raids "a bit kinder to a lightly defended player" without losing the barbarians he asked for in issue 345.

## Cause

- A barbarian boat carries a sea raider picked by `find_a_unit_type` (`server/unittools.c:175`). A unit with the tech role counts only once more than two non-barbarian players can build it. When none qualifies, the boat falls back to the base `BarbarianSea` role.
- In civ45 the base sea raider was Swordsmen ("Legion", attack 6). Against a Spearmen (defence 2), one landing is often enough.
- In issue 357's test only one player exists, so the tech check always failed and every boat carried Swordsmen from turn 30. A real game with one or two AIs would be the same.
- In 12-AI games Warriors always qualify, so early boats carry Warriors and Horsemen, and Swordsmen ride only once three players know Iron Working (first seen at turns 60 to 65 in seeds 7, 13, 42 and 5).

## Change

Archers, not Swordsmen, are civ45's base sea raider (`data/civ45/units.ruleset`). Swordsmen keep `BarbarianSeaTech`, so they still raid by sea once Iron Working spreads. The barbarian rate stays "Raging hordes".

## Tried first: the Normal rate

On map seed 7 with one Spearmen per city, `barbarians NORMAL` lost no cities in 5 games. But in 80-turn games with 12 AIs it cut barbarians from 25 to 67 units to 3 to 9, with the first one at turns 31 to 65, and they took no city. That undoes issue 345, so it was dropped. Starting at turn 40 on top of Normal left barbarians almost absent.

## Test

Map seed 7 (18 x 24 island map), game seeds 1 to 5, 100 turns, one AI ("Oscar") held to 3 cities by `passive.lua`. `pg1.lua` also tops each city up to one Spearmen ("Phalanx") every turn. `one.sh` runs the shipped app's server and `one2.sh` the built server with a data path; `sum.sh` counts from the observers' log lines. Raw lines are in `barbarians-357/results.txt`.

| Rules | Garrison | Games losing a city | Cities lost (5 games) | Barbarian units, landing by boat |
|---|---|---|---|---|
| 0067 (hordes, Swordsmen fallback) | 1 Spearmen per city | 4 of 5 | 9 | 16 to 32 |
| 0070 (hordes, Archers fallback) | 1 Spearmen per city | 1 of 5 | 1 | 22 to 30 |
| Normal rate (dropped) | 1 Spearmen per city | 0 of 5 | 0 | 2 to 8 |
| 0067 | AI's own (about 1 unit) | 5 of 5 | 15 | 2 to 12 |
| 0070 | AI's own | 4 of 5 | 15 | 2 to 26 |

- With 0070, raids come as often as before and still punish a player with no guards; one guard per city now usually holds.
- 12-AI games on seeds 7, 13, 42 and 5 (`auto.sh`, 80 turns) came out identical under 0067 and 0070 rules: 25 to 67 barbarian units, the first at turns 30 to 40, 0 to 5 cities taken. The fallback never applies there.
- None of these games logged "Cannot even build a fallback" (patch 0069, issue 358).

## Not checked

- A human player's game; these are AIs held passive by Lua.
- Maps other than seed 7 for the one-player test. Seeds 42 and 13 lost nothing even under 0067 (issue 357).
