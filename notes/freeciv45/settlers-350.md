# Settlers cost one citizen (issue 350, patch 0066)

John's play test, 2026-10-27: a second Settlers took about 15 more turns, so his first 27 turns gave one city, a Granary and a Warrior.

## Cause

`data/civ45/units.ruleset` gave Settlers `pop_cost = 2` (with `build_cost = 30`). A city can't give up its last citizen, so it had to reach size 3 before it could finish Settlers. Growth from size 1 to 3 needs two 20-food boxes (`granary_food_ini` in `game.ruleset`, line 111). John's capital also sat on Forest, which gives 1 food and gets no free irrigation, so it grew by about 1 food a turn (his autosaves, turns 10 and 18: food stock 8 and 16).

The start itself was equal: every player had the same 3 units at turn 1 (`startunits` "cwx", his turn 1 autosave). By turn 27 John had 1 city and 10 of the 11 AIs had 2 to 4 (issue 346).

## Change

Patch 0066 sets `pop_cost = 1`, so a size 2 city can finish Settlers, and replaces the help text's old size tip. Shield cost unchanged.

## Test

Ten 40-turn autogames, 12 AIs at Normal, seeds 7, 42, 13, 5 and 99, each with the 0065 rules (`base`) and with the change (`new`). `run.sh` runs one game; `second.py` reads the turn 40 save. Raw output in `settlers-350/results.txt`. The turn is the second city's founding turn, so it includes the Settlers' walk.

| Seed | 2nd city, median turn (before → after) | Cities per player at T40 (before → after) |
|---|---|---|
| 7 | 22 → 17 | 3.1 → 5.2 |
| 42 | 22 → 17 | 3.4 → 4.8 |
| 13 | 20.5 → 16.5 | 3.9 → 5.1 |
| 5 | 18.5 → 14.5 | 4.7 → 5.8 |
| 99 | 21 → 16.5 | 4.1 → 5.9 |

Every player had a second city by turn 40 in all ten games.

## Not checked

- A human player's opening (the games are AI only). The player gains the same as the AI, so the gap in issue 346 is not closed by this; that issue stays open.
- Late-game effects of faster expansion (victory timing, balance report 5's pacing). The next full-length balance run will show them.
