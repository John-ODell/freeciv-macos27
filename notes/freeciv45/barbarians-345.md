# Barbarians from turn 30, out of the fog (issue 345, patch 0067)

John's play test, 2026-10-27: "there are no barbarians", and later: expanding to two or three cities with no protection is not like a Civ game, "that's why we need barbarians".

## Why there were none

- `data/civ45/game.ruleset` set `onsetbarbs` to 120, so no barbarian could appear before turn 120 (`server/barbarian.c`, `summon_barbarians`, line 747).
- A land uprising could only start on land the victim had already explored (`try_summon_barbarians`: an unknown land tile ends the try). Early in the game players know little land 5 to 8 tiles from their cities (`MIN_UNREST_DIST`, `MAX_UNREST_DIST` in `server/barbarian.h`), so the barbarians that did come were sea raiders.
- The only early raider was Horsemen (the `Barbarian` role), and the only raiding boat was the Galleon (`BarbarianBoat`), so the first sea raid of a test came in a Galleon at turn 37.

## Change

- New server setting `barbsfromfog` (default off, so other rulesets behave as before). When it is on, a land uprising can start on any tile the victim does not see at the moment, explored or not.
- civ45 turns it on, sets `onsetbarbs` to 30 and `barbarians` to HORDES.
- Warriors, Archers and Horsemen get `BarbarianTech` and `BarbarianSeaTech`, so early raiders are units of the era; Legion keeps its role and also gets `BarbarianSeaTech`.
- Trireme is the `BarbarianBoat`; Caravel and Galleon are `BarbarianBoatTech`, used once more than two players can build them.

## Test

80-turn autogames, 12 AIs at Normal, seeds 7, 42 and 13, with the 0066 rules plus each step. `barbwatch.lua` logs every barbarian unit the turn it first appears (on land, at sea, or aboard a boat); `scripts/civ45-combat-log.lua` logs captures. `sum.sh` counts them; raw output in `barbarians-345/results.txt`.

| Step | Rules | First barbarian (turn) | Uprisings per game | Land raiders per game | Cities barbarians took |
|---|---|---|---|---|---|
| A | onset 30 | 37, 61, 46 | sea only | 0 | 3, 1, 1 |
| B | A + FREQUENT, era units, Trireme | 46, 31, 33 | 4, 7, 8 | 0, 1, 0 | 0, 2, 2 |
| C | B + barbsfromfog | 35, 31, 32 | 6, 6, 5 | 8, 2, 4 | 5, 2, 2 |
| D (patch) | C at HORDES | 30, 40, 32 | 21, 9, 15 | 8, 2, 4 | 4, 0, 3 |

Seeds in the order 7, 42, 13. Step A was counted before `barbwatch.lua` existed; its numbers come from the combat log. At step D the AIs still had 7.2 to 9.2 cities each at turn 80 (C: 7.3 to 9.0), so the raids slow expansion without ending it.

## Not checked

- A human player's game; the AIs garrison by habit, a new player may not.
- Land uprisings are still fewer than sea raids. Freeciv spares small empires: the chance of an uprising grows with the victim's city count, so a two-city player is rarely hit. If John still sees too few, the next step is that check, not a higher rate.
- Barbarian cities: Freeciv barbarians take cities but don't found them, unlike Civ4.
